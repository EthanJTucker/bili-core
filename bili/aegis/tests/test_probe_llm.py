"""Tests for :mod:`bili.aegis.probe._llm`.

Covers ProbeLLM Protocol satisfaction, _FakeLLM script + responder modes,
and _LangChainLLMAdapter token extraction. Real-LLM loading via
resolve_real_llm is mocked so the tests don't require provider credentials.
"""

import logging
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from bili.aegis.probe._llm import (
    ProbeLLM,
    _FakeLLM,
    _LangChainLLMAdapter,
    resolve_real_llm,
)

# =========================================================================
# _FakeLLM — mode-selection guards
# =========================================================================


def test_fake_llm_rejects_both_script_and_responder():
    """Constructor refuses both modes simultaneously.

    Catches: silently preferring one over the other.
    """
    with pytest.raises(ValueError, match="rejects both"):
        _FakeLLM(
            script={"default": ["x"]},
            responder=lambda p: ("y", 0, 0),
        )


def test_fake_llm_rejects_neither_script_nor_responder():
    """Constructor refuses both modes empty.

    Catches: a default-fallback behavior that hides config errors.
    """
    with pytest.raises(ValueError, match="exactly one"):
        _FakeLLM()


# =========================================================================
# _FakeLLM — script mode
# =========================================================================


def test_fake_llm_script_returns_scripted_responses_in_order():
    """Calls drain the bucket in order."""
    fake = _FakeLLM(script={"default": ["r1", "r2", "r3"]})
    assert fake.invoke("p1")[0] == "r1"
    assert fake.invoke("p2")[0] == "r2"
    assert fake.invoke("p3")[0] == "r3"


def test_fake_llm_script_raises_when_exhausted():
    """Past the end of the bucket raises AssertionError with the label."""
    fake = _FakeLLM(script={"default": ["r1"]})
    fake.invoke("p")
    with pytest.raises(AssertionError, match="default"):
        fake.invoke("p")


def test_fake_llm_script_raises_for_unknown_label():
    """invoke with no matching bucket raises with a clear message."""
    fake = _FakeLLM(script={"planner": ["r1"]})
    fake.set_label("nonexistent")
    with pytest.raises(AssertionError, match="nonexistent"):
        fake.invoke("p")


def test_fake_llm_set_label_switches_bucket():
    """Tests can drain different buckets in sequence."""
    fake = _FakeLLM(
        script={
            "planner": ["plan_resp"],
            "judge": ["judge_resp"],
        },
        label_when_unscripted="planner",
    )
    assert fake.invoke("p1")[0] == "plan_resp"
    fake.set_label("judge")
    assert fake.invoke("p2")[0] == "judge_resp"


def test_fake_llm_script_buckets_track_independent_cursors():
    """Switching labels mid-test preserves each bucket's cursor.

    Catches: a shared cursor across labels.
    """
    fake = _FakeLLM(
        script={"a": ["a1", "a2"], "b": ["b1"]},
        label_when_unscripted="a",
    )
    fake.invoke("p")  # a → a1
    fake.set_label("b")
    fake.invoke("p")  # b → b1
    fake.set_label("a")
    assert fake.invoke("p")[0] == "a2"


# =========================================================================
# _FakeLLM — responder mode
# =========================================================================


def test_fake_llm_responder_invoked_with_full_prompt():
    """Responder sees the exact prompt string the caller passed.

    Critical for anti-cheat prompt-content assertions in node tests.
    """
    received: list[str] = []

    def _resp(prompt: str) -> tuple[str, int, int]:
        received.append(prompt)
        return "ok", 0, 0

    fake = _FakeLLM(responder=_resp)
    fake.invoke("the actual prompt with multiple lines\nline 2")
    assert received == ["the actual prompt with multiple lines\nline 2"]


def test_fake_llm_responder_returns_tokens_unchanged():
    """Responder's token tuple flows through invoke verbatim."""
    fake = _FakeLLM(responder=lambda p: ("ok", 137, 42))
    assert fake.invoke("anything") == ("ok", 137, 42)


# =========================================================================
# _FakeLLM — token defaults
# =========================================================================


def test_fake_llm_tokens_per_call_default_zero_zero():
    """Default (0, 0) — explicit anti-cheat against accidental nonzero defaults.

    A nonzero default could mask bugs where tests expect zero tokens.
    """
    fake = _FakeLLM(script={"default": ["r"]})
    _, t_in, t_out = fake.invoke("p")
    assert (t_in, t_out) == (0, 0)


def test_fake_llm_tokens_per_call_overridable():
    """Caller can supply non-zero token defaults."""
    fake = _FakeLLM(
        script={"default": ["r"]},
        tokens_per_call=(123, 45),
    )
    _, t_in, t_out = fake.invoke("p")
    assert (t_in, t_out) == (123, 45)


# =========================================================================
# Protocol satisfaction
# =========================================================================


def test_fake_llm_satisfies_probellm_protocol():
    """isinstance(fake, ProbeLLM) is True (runtime-checkable Protocol)."""
    fake = _FakeLLM(script={"default": ["r"]})
    assert isinstance(fake, ProbeLLM)


def test_langchain_adapter_satisfies_probellm_protocol():
    """The real-LLM adapter also satisfies the Protocol."""
    adapter = _LangChainLLMAdapter(chat_model=SimpleNamespace())
    assert isinstance(adapter, ProbeLLM)


# =========================================================================
# _LangChainLLMAdapter
# =========================================================================


def test_langchain_adapter_reads_usage_metadata():
    """When response.usage_metadata is present, tokens flow through."""

    class _MockChat:  # pylint: disable=too-few-public-methods
        """Minimal LangChain ChatModel stub that returns a fixed response."""

        def invoke(self, messages):  # pylint: disable=unused-argument
            """Return a canned response with token usage metadata."""
            return SimpleNamespace(
                content="hello world",
                usage_metadata={"input_tokens": 50, "output_tokens": 17},
            )

    adapter = _LangChainLLMAdapter(_MockChat())
    text, t_in, t_out = adapter.invoke("anything")
    assert text == "hello world"
    assert t_in == 50
    assert t_out == 17


def test_langchain_adapter_logs_warning_when_usage_metadata_absent(caplog):
    """Without usage_metadata, falls back to (0, 0) and emits a warning."""

    class _MockChat:  # pylint: disable=too-few-public-methods
        """ChatModel stub whose response carries no usage_metadata."""

        def invoke(self, messages):  # pylint: disable=unused-argument
            """Return a response with usage_metadata set to None."""
            return SimpleNamespace(content="hi", usage_metadata=None)

    adapter = _LangChainLLMAdapter(_MockChat())
    with caplog.at_level(logging.WARNING, logger="bili.aegis.probe._llm"):
        text, t_in, t_out = adapter.invoke("p")
    assert (text, t_in, t_out) == ("hi", 0, 0)
    assert any("usage_metadata" in rec.message for rec in caplog.records)


def test_langchain_adapter_stringifies_non_string_content():
    """If chat_model.content is not a str, it's coerced via str()."""

    class _MockChat:  # pylint: disable=too-few-public-methods
        """ChatModel stub whose response.content is a list, not a string."""

        def invoke(self, messages):  # pylint: disable=unused-argument
            """Return a response with non-string list content."""
            return SimpleNamespace(
                content=["multi", "part", "list"],
                usage_metadata={"input_tokens": 0, "output_tokens": 0},
            )

    adapter = _LangChainLLMAdapter(_MockChat())
    text, _, _ = adapter.invoke("p")
    assert isinstance(text, str)


# =========================================================================
# resolve_real_llm
# =========================================================================


def test_resolve_real_llm_returns_adapter():
    """resolve_real_llm returns something satisfying ProbeLLM."""
    fake_chat = SimpleNamespace()
    with patch("bili.iris.loaders.llm_loader.load_model", return_value=fake_chat):
        result = resolve_real_llm(
            {"model_type": "remote_aws_bedrock", "model_name": "claude-x"}
        )
    assert isinstance(result, ProbeLLM)


def test_resolve_real_llm_passes_config_as_kwargs_to_load_model():
    """The full model_config dict is spread into load_model as kwargs.

    Catches: passing the dict as a positional argument (wrong signature).
    """
    captured: dict = {}

    def _fake_load_model(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace()

    with patch("bili.iris.loaders.llm_loader.load_model", side_effect=_fake_load_model):
        resolve_real_llm(
            {
                "model_type": "remote_google_vertex",
                "model_name": "gemini-2.5-flash",
                "temperature": 0.2,
            }
        )

    assert captured == {
        "model_type": "remote_google_vertex",
        "model_name": "gemini-2.5-flash",
        "temperature": 0.2,
    }
