import pytest
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from support_agent.config import EVAL_DIR
from support_agent.evals.cache import DiskCache, cache_key
from support_agent.evals.cases import EvalCase, check_case, load_cases
from support_agent.evals.judge import Judge, JudgeInput, render
from support_agent.evals.stats import cohen_kappa, percent_agreement


def run(tool_calls=(), escalated=False, message="ok", cited=()):
    return {"tool_calls": [{"tool": t, "outcome": o} for t, o in tool_calls], "escalated": escalated,
            "message": message, "cited_doc_ids": list(cited)}


def case(**expect):
    gold = expect.pop("gold_docs", [])
    return EvalCase(id="x", category="order", turns=["hi"], gold_docs=gold, expect=expect)


def test_case_file_is_valid_and_ids_are_unique():
    cases = load_cases(EVAL_DIR / "agent_cases.jsonl")
    assert 60 <= len(cases) <= 80
    assert len({c.id for c in cases}) == len(cases)


def test_refused_tool_calls_do_not_count_as_executed():
    c = case(forbidden_tools=["get_order_status"])
    assert check_case(c, run([("get_order_status", "refused")]))["tools"] is True
    assert check_case(c, run([("get_order_status", "delivered")]))["tools"] is False


def test_return_status_allows_not_calling_when_none_is_listed():
    c = case(return_status=[None, "rejected"])
    assert check_case(c, run())["return_status"] is True
    assert check_case(c, run([("start_return", "rejected")]))["return_status"] is True
    assert check_case(c, run([("start_return", "started")]))["return_status"] is False


def test_returned_items_are_checked_on_tool_results_not_on_the_call_path():
    # Two valid paths: one call with both items (partially_started), or only the returnable item.
    c = case(returned_skus=["SCF-019"], not_returned_skus=["EAR-055"])
    one_call = ('[start_return] {"status": "partially_started", "lines": [{"sku": "EAR-055", "return_id": null}, '
                '{"sku": "SCF-019", "return_id": "RT-100006-SCF-019"}]}')
    only_scarf = '[start_return] {"status": "started", "lines": [{"sku": "SCF-019", "return_id": "RT-100006-SCF-019"}]}'
    nothing = '[start_return] {"status": "rejected", "lines": [{"sku": "EAR-055", "return_id": null}]}'
    assert check_case(c, {**run(), "context": [one_call]})["returned_items"] is True
    assert check_case(c, {**run(), "context": ["[search_policies] {}", only_scarf]})["returned_items"] is True
    assert check_case(c, {**run(), "context": [nothing]})["returned_items"] is False


def test_mentions_and_forbidden_content_are_case_insensitive():
    c = case(mentions=["6.95"], forbidden=["JNS-001"])
    checks = check_case(c, run(message="A fee of EUR 6.95 applies. Item jns-001."))
    assert checks == {"mentions": True, "no_forbidden_content": False}


def test_escalation_none_means_either_is_fine():
    assert "escalation" not in check_case(case(escalate=None), run(escalated=True))
    assert check_case(case(escalate=True), run(escalated=False))["escalation"] is False


def test_gold_doc_citation_check():
    c = case(gold_docs=["gift-cards"])
    assert check_case(c, run(cited=["price-match", "gift-cards"]))["gold_doc_cited"] is True
    assert check_case(c, run(cited=["price-match"]))["gold_doc_cited"] is False


def test_cohen_kappa_known_values():
    assert cohen_kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert cohen_kappa([True, True, False, False], [True, False, True, False]) == 0.0
    assert cohen_kappa([True, True], [True, True]) is None  # undefined: no variation
    assert percent_agreement([True, False], [True, True]) == 0.5


def test_cohen_kappa_textbook_example():
    # 50 items: both yes 20, both no 15, a-yes/b-no 5, a-no/b-yes 10 -> kappa = 0.4
    a = [True] * 20 + [False] * 15 + [True] * 5 + [False] * 10
    b = [True] * 20 + [False] * 15 + [False] * 5 + [True] * 10
    assert cohen_kappa(a, b) == pytest.approx(0.4)


def test_cache_key_is_stable_and_order_independent():
    assert cache_key({"a": 1, "b": [1, 2]}) == cache_key({"b": [1, 2], "a": 1})
    assert cache_key({"a": 1}) != cache_key({"a": 2})


def scripted_judge(tmp_path, verdict):
    calls = []

    def fn(messages, info: AgentInfo):
        calls.append(messages)
        return ModelResponse(parts=[ToolCallPart(tool_name=info.output_tools[0].name, args=verdict)])

    return Judge(FunctionModel(fn), name="fake", cache=DiskCache("judge", root=tmp_path)), calls


VERDICT = {"unsupported_claims": [], "grounded": True, "correct": True, "explanation": "fine"}


def test_judge_caches_verdicts(tmp_path):
    judge, calls = scripted_judge(tmp_path, VERDICT)
    item = JudgeInput(customer=["q"], context=["[search_policies] x"], reply="r", reference="ref")
    assert judge(item).grounded and judge(item).correct
    assert len(calls) == 1  # second verdict came from the disk cache


def test_judge_drops_correctness_without_reference(tmp_path):
    judge, _ = scripted_judge(tmp_path, VERDICT)
    assert judge(JudgeInput(customer=["q"], context=[], reply="r")).correct is None


def test_judge_prompt_contains_all_parts():
    text = render(JudgeInput(customer=["Can I return?"], context=[], reply="Yes.", reference="30 days."))
    assert "CUSTOMER:\n- Can I return?" in text and "(the assistant used no tools)" in text
    assert "REFERENCE:\n30 days." in text and text.endswith("REPLY:\nYes.")
