"""Testes locais da integração de avaliação com experimentos LangSmith."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import evaluate as evaluate_script


class FakePrompt:
    def __or__(self, llm):
        return self

    def invoke(self, inputs):
        return SimpleNamespace(content=f"Resposta para {inputs['bug_report']}")


def test_evaluate_prompt_creates_experiment_and_logs_all_metrics(capsys):
    experiment_result = SimpleNamespace(experiment_name="experiment-v2")
    example = SimpleNamespace(
        inputs={"bug_report": "Falha no login"},
        outputs={"reference": "User Story esperada"},
    )

    def run_fake_experiment(target, **kwargs):
        output = target({"bug_report": "Falha no login"})
        evaluation = kwargs["evaluators"][0](
            SimpleNamespace(outputs=output),
            example,
        )
        assert {result["key"] for result in evaluation["results"]} == {
            "f1_score", "clarity", "precision", "helpfulness", "correctness"
        }
        assert all(
            result["score"] == round(result["score"], 4)
            for result in evaluation["results"]
        )
        return experiment_result

    with (
        patch.object(evaluate_script, "pull_prompt_from_langsmith", return_value=FakePrompt()),
        patch.object(evaluate_script, "get_llm", return_value=object()),
        patch.object(evaluate_script, "evaluate_f1_score", return_value={"score": 0.82335}),
        patch.object(evaluate_script, "evaluate_clarity", return_value={"score": 0.84285}),
        patch.object(evaluate_script, "evaluate_precision", return_value={"score": 0.79285}),
        patch.object(evaluate_script, "langsmith_evaluate", side_effect=run_fake_experiment) as run_evaluate,
    ):
        scores = evaluate_script.evaluate_prompt(
            "owner/bug_to_user_story_v2",
            "dataset-eval",
            SimpleNamespace(list_examples=lambda dataset_name: [example]),
        )

    assert scores == {
        "f1_score": round(0.82335, 4),
        "clarity": round(0.84285, 4),
        "precision": round(0.79285, 4),
        "helpfulness": round((0.84285 + 0.79285) / 2, 4),
        "correctness": round((0.82335 + 0.79285) / 2, 4),
    }
    _, kwargs = run_evaluate.call_args
    assert kwargs["data"] == [example]
    assert kwargs["experiment_prefix"] == "bug_to_user_story_v2-evaluation"
    assert kwargs["metadata"] == {"prompt_name": "owner/bug_to_user_story_v2"}
    assert kwargs["max_concurrency"] == 0
    logs = capsys.readouterr().out
    assert "Dataset: 1 exemplos" in logs
    assert "Avaliando exemplos..." in logs
    assert "[1/1] F1:0.82 Clarity:0.84 Precision:0.79" in logs
