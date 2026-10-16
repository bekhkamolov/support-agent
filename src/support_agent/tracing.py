"""Optional tracing to Langfuse via OpenTelemetry.

PydanticAI emits OpenTelemetry spans for every agent run, model call and tool call. Here they are
exported to Langfuse's OTLP endpoint. OpenTelemetry keeps this vendor-neutral: another backend
(Jaeger, Grafana Tempo, Logfire) only needs a different endpoint and headers.

Tracing is off unless LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are set.
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass

DEFAULT_HOST = "https://cloud.langfuse.com"  # EU region


@dataclass(frozen=True)
class OtlpConfig:
    endpoint: str
    headers: dict[str, str]
    include_content: bool


def langfuse_config(env: dict[str, str] | None = None) -> OtlpConfig | None:
    """Build the OTLP exporter settings from environment variables; None if tracing is not configured."""
    env = os.environ if env is None else env
    public, secret = env.get("LANGFUSE_PUBLIC_KEY", "").strip(), env.get("LANGFUSE_SECRET_KEY", "").strip()
    if not public or not secret:
        return None
    host = (env.get("LANGFUSE_HOST") or DEFAULT_HOST).rstrip("/")
    auth = base64.b64encode(f"{public}:{secret}".encode()).decode()
    return OtlpConfig(
        endpoint=f"{host}/api/public/otel/v1/traces",
        headers={"Authorization": f"Basic {auth}", "x-langfuse-ingestion-version": "4"},
        # Prompts and replies contain customer messages. The demo data is synthetic; for real
        # customers set LANGFUSE_INCLUDE_CONTENT=false to export only structure, timings and tokens.
        include_content=env.get("LANGFUSE_INCLUDE_CONTENT", "true").strip().lower() != "false",
    )


UNTRACED_SPANS = {"GET /health"}  # platform health checks (Render polls about twice a minute)


def health_check_sampler():
    """Drop health-check requests and, via ParentBased, all their child spans; sample everything else.

    Without this, health checks would be the majority of traces and use up the tracing quota.
    """
    from opentelemetry.sdk.trace.sampling import Decision, ParentBased, Sampler, SamplingResult

    class DropUntraced(Sampler):
        def should_sample(self, parent_context, trace_id, name, kind=None, attributes=None, links=None,
                          trace_state=None):
            return SamplingResult(Decision.DROP if name in UNTRACED_SPANS else Decision.RECORD_AND_SAMPLE,
                                  attributes)

        def get_description(self) -> str:
            return "DropUntraced"

    return ParentBased(root=DropUntraced())


def setup_tracing(service_name: str = "nordwind-support-agent") -> bool:
    """Install a global tracer provider exporting to Langfuse and instrument all agents.

    Returns False (and changes nothing) when tracing is not configured.
    """
    config = langfuse_config()
    if config is None:
        return False

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from pydantic_ai import Agent
    from pydantic_ai.models.instrumented import InstrumentationSettings

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}), sampler=health_check_sampler())
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=config.endpoint, headers=config.headers)))
    trace.set_tracer_provider(provider)
    Agent.instrument_all(InstrumentationSettings(tracer_provider=provider, include_content=config.include_content))
    return True
