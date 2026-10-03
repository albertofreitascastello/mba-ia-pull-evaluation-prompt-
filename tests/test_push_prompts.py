"""Testes de publicação sem acessar o LangSmith."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import push_prompts


@pytest.fixture
def prompt():
    return {
        "description": "Converte bugs em user stories",
        "system_prompt": "Você é um Product Manager.",
        "user_prompt": "Relato: {bug_report}",
        "version": "v2",
        "tags": ["user-story"],
        "techniques_applied": ["few-shot", "role-prompting"],
    }


@pytest.mark.parametrize("value", [None, [], "texto", {}])
def test_rejects_invalid_structure(value):
    assert not push_prompts.validate_prompt(value)[0]


@pytest.mark.parametrize("field,value", [
    ("tags", "tag"),
    ("techniques_applied", [None]),
    ("user_prompt", "{wrong_input}"),
    ("user_prompt", "{bug_report"),
    ("system_prompt", "TODO: completar"),
])
def test_rejects_invalid_fields(prompt, field, value):
    prompt[field] = value
    assert not push_prompts.validate_prompt(prompt)[0]


def test_publishes_public_template_and_metadata(prompt):
    with patch.object(push_prompts.hub, "push", return_value="https://example.com/prompt") as push:
        assert push_prompts.push_prompt_to_langsmith("owner/bug_to_user_story_v2", prompt)
    args, kwargs = push.call_args
    assert args[0] == "owner/bug_to_user_story_v2"
    messages = args[1].format_messages(bug_report="Falha no login")
    assert [message.type for message in messages] == ["system", "human"]
    assert messages[1].content == "Relato: Falha no login"
    assert args[1].metadata["techniques_applied"] == prompt["techniques_applied"]
    assert kwargs["new_repo_is_public"] is True
    assert kwargs["new_repo_description"] == prompt["description"]
    assert "few-shot" in kwargs["tags"]
    assert "role-prompting" in kwargs["readme"]


def test_api_failure_returns_false(prompt):
    with patch.object(push_prompts.hub, "push", side_effect=RuntimeError("API indisponível")):
        assert not push_prompts.push_prompt_to_langsmith("owner/bug_to_user_story_v2", prompt)


@pytest.mark.parametrize("version,exit_code", [("v1", 1), ("v2", 0)])
def test_main_validates_version_and_uses_configured_owner(prompt, monkeypatch, version, exit_code):
    monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")
    monkeypatch.setenv("USERNAME_LANGSMITH_HUB", "configured-owner")
    prompt["version"] = version
    with patch.object(push_prompts, "load_yaml", return_value={"source/bug_to_user_story_v2": prompt}), patch.object(
        push_prompts, "push_prompt_to_langsmith", return_value=True
    ) as push:
        assert push_prompts.main() == exit_code
    if exit_code:
        push.assert_not_called()
    else:
        push.assert_called_once_with("configured-owner/bug_to_user_story_v2", prompt)


def test_missing_credentials_prevents_publication(monkeypatch):
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    with patch.object(push_prompts.hub, "push") as push:
        assert push_prompts.main() == 1
    push.assert_not_called()


@pytest.mark.parametrize("username", ["user@example.com", "https://example.com/user", "user name", " "])
def test_invalid_hub_username_prevents_publication(monkeypatch, username):
    monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")
    monkeypatch.setenv("USERNAME_LANGSMITH_HUB", username)
    with patch.object(push_prompts.hub, "push") as push:
        assert push_prompts.main() == 1
    push.assert_not_called()
