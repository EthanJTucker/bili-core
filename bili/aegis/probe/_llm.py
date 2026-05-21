"""LLM Protocol + fake/real adapters for PROBE.

PROBE's nodes and policies depend on the ``ProbeLLM`` Protocol rather than any
concrete provider. This lets unit tests use a deterministic in-process fake
(``_FakeLLM``) and production code use a real LangChain ChatModel (via
``resolve_real_llm``) through the same interface.

Token accounting is part of the Protocol: every ``invoke`` returns the
response text plus its ``(tokens_in, tokens_out)`` cost so the runner can
record per-turn consumption against the BudgetState without inspecting
provider-specific response objects.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from langchain_core.messages import HumanMessage

LOGGER = logging.getLogger(__name__)


# Single-method Protocol is the entire type contract; adding another
# method would change the contract. pylint min-public-methods=2 fires
# on any 1-method Protocol regardless.
@runtime_checkable
class ProbeLLM(Protocol):  # pylint: disable=too-few-public-methods
    """Minimal LLM interface used by every PROBE node and policy.

    Implementations return a 3-tuple of ``(response_text, tokens_in,
    tokens_out)``. Token counts of ``(0, 0)`` are valid (e.g. for the fake
    in unit tests where budget enforcement is not being exercised).
    """

    def invoke(self, prompt: str) -> tuple[str, int, int]:
        """Send ``prompt`` to the underlying model and return its response."""


class _FakeLLM:
    """Deterministic in-process LLM for unit tests.

    Two mutually-exclusive modes:

    - **Script mode**: pass ``script={"label": ["resp1", "resp2", ...]}``.
      Each ``invoke()`` returns the next response from the current label's
      bucket; switch labels via ``set_label()``. Raises ``AssertionError``
      when a bucket is exhausted.

    - **Responder mode**: pass ``responder=callable``. The callable receives
      the full prompt and returns ``(response, tokens_in, tokens_out)``.
      Use this for prompt-content assertions where the responder inspects
      what the node actually built.

    Exactly one mode must be set; rejecting both empty and both populated.
    """

    def __init__(
        self,
        script: Optional[dict[str, list[str]]] = None,
        responder: Optional[Callable[[str], tuple[str, int, int]]] = None,
        tokens_per_call: tuple[int, int] = (0, 0),
        label_when_unscripted: str = "default",
    ) -> None:
        if script is None and responder is None:
            raise ValueError(
                "_FakeLLM requires exactly one of `script` or `responder`."
            )
        if script is not None and responder is not None:
            raise ValueError(
                "_FakeLLM rejects both `script` and `responder` set "
                "simultaneously; pass exactly one."
            )
        self._script = script
        self._responder = responder
        self._tokens_per_call = tokens_per_call
        self._current_label = label_when_unscripted
        self._cursors: dict[str, int] = {}

    def invoke(self, prompt: str) -> tuple[str, int, int]:
        """See :class:`ProbeLLM`."""
        if self._responder is not None:
            return self._responder(prompt)
        # Script mode
        label = self._current_label
        if self._script is None or label not in self._script:
            raise AssertionError(
                f"_FakeLLM script has no bucket for label {label!r}; "
                f"available labels: {sorted(self._script or {})}"
            )
        bucket = self._script[label]
        cursor = self._cursors.get(label, 0)
        if cursor >= len(bucket):
            raise AssertionError(
                f"_FakeLLM script exhausted for label {label!r} "
                f"({cursor} responses requested, only {len(bucket)} scripted)"
            )
        response = bucket[cursor]
        self._cursors[label] = cursor + 1
        tokens_in, tokens_out = self._tokens_per_call
        return response, tokens_in, tokens_out

    def set_label(self, label: str) -> None:
        """Switch which script bucket subsequent ``invoke()`` calls drain from."""
        self._current_label = label


@dataclass
class _LangChainLLMAdapter:
    """Wraps a LangChain ChatModel to satisfy the :class:`ProbeLLM` Protocol.

    Stored as ``chat_model`` (the public dataclass field name). Tests
    that previously read ``adapter._chat`` should switch to
    ``adapter.chat_model``.
    """

    chat_model: Any

    def invoke(self, prompt: str) -> tuple[str, int, int]:
        """Invoke the underlying ChatModel with ``prompt`` as a HumanMessage."""
        response = self.chat_model.invoke([HumanMessage(content=prompt)])
        text = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )
        usage = getattr(response, "usage_metadata", None)
        if not usage:
            LOGGER.warning(
                "LangChain response has no usage_metadata; token counts "
                "default to (0, 0). Model: %s",
                type(self.chat_model).__name__,
            )
            return text, 0, 0
        return (
            text,
            int(usage.get("input_tokens", 0)),
            int(usage.get("output_tokens", 0)),
        )


def resolve_real_llm(model_config: dict[str, Any]) -> ProbeLLM:
    """Wrap an IRIS-loaded LangChain ChatModel into a :class:`ProbeLLM`.

    ``model_config`` is passed through to
    :func:`bili.iris.loaders.llm_loader.load_model` as keyword arguments.
    The dict MUST contain a ``model_type`` key (one of
    ``remote_aws_bedrock``, ``remote_google_vertex``, ``remote_azure_openai``,
    ``local_llamacpp``, ``local_huggingface``) plus the appropriate
    type-specific kwargs (e.g. ``model_name``, ``temperature``).

    Returns an adapter whose ``invoke`` method translates the LangChain
    ``AIMessage`` return into the PROBE 3-tuple shape, reading token counts
    from ``response.usage_metadata``; when absent, falls back to ``(0, 0)``
    with a ``LOGGER.warning``.
    """
    # IRIS llm_loader transitively imports torch, transformers, and
    # Streamlit — multi-second import cost. Defer until a real (non-stub)
    # LLM is actually needed so stub-only PROBE tests stay fast.
    from bili.iris.loaders.llm_loader import (  # pylint: disable=import-outside-toplevel
        load_model,
    )

    chat_model = load_model(**model_config)
    return _LangChainLLMAdapter(chat_model)
