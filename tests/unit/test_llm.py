"""Tests unitaires — velmo.llm : repli EchoLLM, adaptateur AzureLLM, sélection get_llm."""

from __future__ import annotations

from velmo.llm import AzureLLM, EchoLLM, get_llm


def test_echo_llm_acknowledges_message():
    assert EchoLLM().invoke("sys", "ctx", "Bonjour") == "[velmo] J'ai bien reçu : Bonjour"


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeModel:
    def __init__(self) -> None:
        self.received: list[dict] = []

    def invoke(self, messages):
        self.received = messages
        return _FakeResponse("réponse simulée")


def test_azure_llm_includes_memory_context_when_present():
    model = _FakeModel()
    answer = AzureLLM(model).invoke("system prompt", "fait=x", "question")
    assert answer == "réponse simulée"
    roles = [m["role"] for m in model.received]
    assert roles == ["system", "system", "user"]
    assert model.received[1]["content"] == "Mémoire:\nfait=x"


def test_azure_llm_skips_memory_message_when_context_empty():
    model = _FakeModel()
    AzureLLM(model).invoke("system prompt", "", "question")
    roles = [m["role"] for m in model.received]
    assert roles == ["system", "user"]  # pas de 2e message système


def test_get_llm_falls_back_to_echo_without_azure_endpoint(monkeypatch):
    monkeypatch.delenv("AZURE_AI_INFERENCE_ENDPOINT", raising=False)
    assert isinstance(get_llm(), EchoLLM)


def test_get_llm_builds_azure_client_when_configured(monkeypatch):
    captured = {}

    class FakeAzureModel:
        def __init__(self, endpoint, credential, model):
            captured.update(endpoint=endpoint, credential=credential, model=model)

    monkeypatch.setattr(
        "langchain_azure_ai.chat_models.AzureAIOpenAIApiChatModel", FakeAzureModel
    )
    monkeypatch.setenv("AZURE_AI_INFERENCE_ENDPOINT", "https://example.test")
    monkeypatch.setenv("AZURE_AI_INFERENCE_API_KEY", "secret-key")
    monkeypatch.delenv("AZURE_AI_INFERENCE_MODEL", raising=False)

    llm = get_llm()

    assert isinstance(llm, AzureLLM)
    assert captured == {
        "endpoint": "https://example.test",
        "credential": "secret-key",
        "model": "Kimi-K2.6",  # défaut
    }
