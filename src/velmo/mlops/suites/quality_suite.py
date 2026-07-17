"""Suite d'evaluation qualite : seul test d'integration des trois — passe par
agent.respond(...), la chaine complete (outils + FAQ), contrairement a T005/T006."""

from __future__ import annotations

from dataclasses import dataclass

from velmo.mlops.cases import load_quality_cases


@dataclass
class QualitySuiteResult:
    score: float
    passed: int
    total: int


def run_quality_suite(agent) -> QualitySuiteResult:
    cases = load_quality_cases()

    passed = 0
    for case in cases:
        answer = agent.respond(case["user_id"], case["question"])
        if case["expected_substring"].lower() in answer.lower():
            passed += 1

    total = len(cases)
    score = passed / total if total else 0.0

    return QualitySuiteResult(score=score, passed=passed, total=total)
