"""Agent tests with a scripted model (PydanticAI FunctionModel): no network, no API key."""
import pytest
from pydantic_ai.messages import ModelResponse, RetryPromptPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from support_agent.agent import SupportAgent
from support_agent.ingest import Chunk
from support_agent.orders import OrderStore
from support_agent.retrieval import SearchResult

RETURNS = Chunk(chunk_id="returns-general#0", doc_id="returns-general", title="Returns", text="30 days.")


class FixedRetriever:
    """Returns one chunk with a fixed score."""

    name = "fixed"

    def __init__(self, score: float):
        self.score = score

    def search(self, query, k=5):
        return [SearchResult(chunk=RETURNS, score=self.score)]


def scripted(*steps):
    """A fake model that makes the given tool calls in order, then gives the final answer.

    Each step is (tool_name, args). The last step must be ("final", {...}).
    Every request the model receives is recorded in `seen` for assertions.
    """
    seen = []

    def fn(messages, info: AgentInfo):
        seen.append(messages[-1])
        name, args = steps[len(seen) - 1]
        if name == "final":
            name = info.output_tools[0].name
        return ModelResponse(parts=[ToolCallPart(tool_name=name, args=args)])

    return FunctionModel(fn), seen


def tool_returns(seen):
    return [p for m in seen for p in m.parts if isinstance(p, ToolReturnPart)]


def make_agent(model, score=0.8):
    store = OrderStore()
    return SupportAgent(model, FixedRetriever(score), store), store


def test_policy_answer_with_valid_and_invented_citations():
    model, _ = scripted(
        ("search_policies", {"query": "return window"}),
        ("final", {"message": "You have 30 days.", "cited_doc_ids": ["returns-general", "made-up"]}),
    )
    result, _ = make_agent(model)[0].ask("How long can I return things?")
    assert result.message == "You have 30 days."
    assert result.cited_doc_ids == ["returns-general"]
    assert result.invalid_citations == ["made-up"]
    assert not result.escalated and not result.guardrail_triggered


def test_order_lookup_and_return_go_through_store_rules():
    model, seen = scripted(
        ("get_order_status", {"order_id": "NW-100006", "email": "farid@example.com"}),
        ("start_return", {"order_id": "NW-100006", "email": "farid@example.com",
                          "skus": ["EAR-055", "SCF-019"], "reason": "changed_mind"}),
        ("final", {"message": "Scarf return started; earrings cannot be returned."}),
    )
    agent, store = make_agent(model)
    result, _ = agent.ask("Return everything from NW-100006, farid@example.com")
    assert [c.tool for c in result.tool_calls] == ["get_order_status", "start_return"]
    assert result.tool_calls[1].outcome == "partially_started"
    assert store.get_order("NW-100006", "farid@example.com").items[1].already_returned  # SCF-019


def test_invalid_order_number_is_rejected_before_the_tool_runs():
    model, seen = scripted(
        ("get_order_status", {"order_id": "12345", "email": "anna@example.com"}),
        ("final", {"message": "Please give me your order number (NW-123456)."}),
    )
    result, _ = make_agent(model)[0].ask("Where is order 12345?")
    assert result.tool_calls == []  # the tool body never ran
    assert any(isinstance(p, RetryPromptPart) for p in seen[1].parts)  # model was told to fix the input


def test_order_data_the_customer_did_not_give_is_refused():
    # The live model once invented "NW-123456" / "customer@example.com" instead of asking.
    model, seen = scripted(
        ("get_order_status", {"order_id": "NW-100006", "email": "customer@example.com"}),
        ("final", {"message": "Please tell me your order number and e-mail address."}),
    )
    result, _ = make_agent(model)[0].ask("I want to return the earrings from NW-100006")
    assert result.tool_calls[0].outcome == "refused"
    assert "e-mail address" in tool_returns(seen)[0].content and "order number" not in tool_returns(seen)[0].content


def test_order_data_from_an_earlier_turn_counts_as_given():
    model, _ = scripted(
        ("final", {"message": "What is your e-mail address?"}),
        ("get_order_status", {"order_id": "NW-100004", "email": "david@example.com"}),
        ("final", {"message": "Your order has been shipped."}),
    )
    agent, _ = make_agent(model)
    _, history = agent.ask("Where is NW-100004?")
    result, _ = agent.ask("david@example.com", history=history)
    assert result.tool_calls[0].outcome == "shipped"


def test_repeated_identical_lookup_is_not_executed_twice():
    args = {"order_id": "NW-100001", "email": "ben@example.com"}
    model, seen = scripted(("get_order_status", args), ("get_order_status", args), ("final", {"message": "Not found."}))
    result, _ = make_agent(model)[0].ask("Status of NW-100001? ben@example.com")
    assert [c.outcome for c in result.tool_calls] == ["not_found", "refused"]


def test_repeated_identical_search_is_not_executed_twice():
    model, _ = scripted(
        ("search_policies", {"query": "Gift wrapping"}),
        ("search_policies", {"query": "gift wrapping "}),
        ("final", {"message": "Let me hand you over."}),
    )
    result, _ = make_agent(model)[0].ask("Do you offer gift wrapping?")
    assert [c.outcome for c in result.tool_calls] == ["found", "refused"]


def test_looping_model_is_stopped_and_handed_over():
    calls = []

    def loop(messages, info: AgentInfo):
        calls.append(1)
        return ModelResponse(parts=[ToolCallPart(tool_name="search_policies", args={"query": f"q{len(calls)}"})])

    result, history = make_agent(FunctionModel(loop))[0].ask("Hello?")
    assert len(calls) == 8  # MAX_REQUESTS_PER_TURN
    assert result.failure == "UsageLimitExceeded"
    assert result.escalated and result.ticket_id in result.message
    assert result.requests == 8 and history == []


RETURN_NL = ("start_return", {"order_id": "NW-100008", "email": "hannah@example.com",
                              "skus": ["BOT-411"], "reason": "wrong_size"})
ASK_NL = "Return the boots from NW-100008, hannah@example.com"


def test_reply_that_hides_the_return_fee_is_sent_back_to_the_model():
    # Live failure: tool charged EUR 6.95 (NL), model said "no label fee applies".
    model, seen = scripted(
        RETURN_NL,
        ("final", {"message": "Return started, no label fee applies - we'll cover the EUR 6.95."}),
        ("final", {"message": "Return started; EUR 6.95 for the label is deducted from your refund."}),
    )
    result, _ = make_agent(model)[0].ask(ASK_NL)
    retry = [p for p in seen[2].parts if isinstance(p, RetryPromptPart)]
    assert retry and "6.95" in str(retry[0].content)
    assert result.message.startswith("Return started; EUR 6.95")


def test_reply_with_invented_link_is_sent_back_to_the_model():
    model, seen = scripted(
        ("final", {"message": "See https://nordwind.example/returns"}),
        ("final", {"message": "You can start a return in My Orders."}),
    )
    result, _ = make_agent(model)[0].ask("How do I return?")
    assert "http" not in result.message


def test_model_that_keeps_breaking_the_rules_is_handed_over():
    bad = ("final", {"message": "The return is free of charge!"})
    model, _ = scripted(RETURN_NL, bad, bad, bad, bad)
    result, _ = make_agent(model)[0].ask(ASK_NL)
    assert result.failure == "UnexpectedModelBehavior" and result.escalated


def test_guardrail_escalates_when_no_relevant_policy_exists():
    model, seen = scripted(
        ("search_policies", {"query": "gift wrapping"}),
        ("final", {"message": "Yes, we offer free gift wrapping!", "cited_doc_ids": ["returns-general"]}),
    )
    result, _ = make_agent(model, score=0.5)[0].ask("Do you offer gift wrapping?")
    assert tool_returns(seen)[0].content.found is False  # excerpts were withheld from the model
    assert result.guardrail_triggered and result.escalated
    assert result.ticket_id == "TK-00001" and result.ticket_id in result.message
    assert "gift wrapping" not in result.message and result.cited_doc_ids == []


def test_guardrail_uses_the_customer_message_not_only_the_model_query():
    # Live failure: model searched "return jacket changed mind" (score 0.625) for an answerable question.
    class ScoreByText:
        name = "by-text"

        def search(self, query, k=5):
            return [SearchResult(chunk=RETURNS, score=0.8 if query.startswith("Can I send back") else 0.6)]

    model, _ = scripted(
        ("search_policies", {"query": "return jacket"}),
        ("final", {"message": "Yes, within 30 days.", "cited_doc_ids": ["returns-general"]}),
    )
    agent = SupportAgent(model, ScoreByText(), OrderStore())
    result, _ = agent.ask("Can I send back a jacket I don't like?")
    assert result.tool_calls[0].outcome == "found" and not result.escalated


def test_guardrail_does_not_fire_when_model_escalated_itself():
    model, _ = scripted(
        ("search_policies", {"query": "gift wrapping"}),
        ("escalate_to_human", {"reason": "not_covered_by_policy", "summary": "Asks about gift wrapping."}),
        ("final", {"message": "A colleague will help you, ticket TK-00001."}),
    )
    result, _ = make_agent(model, score=0.5)[0].ask("Do you offer gift wrapping?")
    assert result.escalated and not result.guardrail_triggered
    assert [c.tool for c in result.tool_calls] == ["search_policies", "escalate_to_human"]


def test_conversation_history_is_kept_between_turns():
    prompts_seen = []

    def fn(messages, info: AgentInfo):
        prompts_seen.append([p.content for m in messages for p in m.parts if p.part_kind == "user-prompt"])
        return ModelResponse(parts=[ToolCallPart(tool_name=info.output_tools[0].name, args={"message": "ok"})])

    agent, _ = make_agent(FunctionModel(fn))
    _, history = agent.ask("Where is my order?")
    agent.ask("NW-100004", history=history)
    assert prompts_seen[-1] == ["Where is my order?", "NW-100004"]
