"""CLI d'evaluation qualite (contracts/cli.md) : construit l'agent, lance
run_eval, ecrit toujours le rapport, puis applique le seuil de blocage."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from velmo.mlops import (
    DeliveryBlocked,
    current_version,
    enforce_threshold,
    run_eval,
    write_report,
)
from velmo.mlops.eval_agent import build_eval_agent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m velmo.mlops.score")
    parser.add_argument(
        "--min-score",
        type=float,
        default=float(os.getenv("EVAL_MIN_SCORE", "0.8")),
        help="seuil de note globale sous lequel la livraison est bloquee "
        "(defaut : EVAL_MIN_SCORE ou 0.8)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("mlops/report.md"),
        help="chemin du rapport genere (defaut : mlops/report.md a la racine du depot)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="utilise la vraie stack (Postgres + Chroma + gpt-5.4 via .env) au lieu de "
        "l'agent d'evaluation SQLite/EchoLLM par defaut — exige Docker et un .env "
        "charge, dure environ 60 s",
    )
    args = parser.parse_args(argv)

    if args.live:
        from dotenv import load_dotenv

        load_dotenv()
        from velmo.agent import build_default_agent

        agent = build_default_agent()
    else:
        agent = build_eval_agent()

    scores = run_eval(agent)
    write_report(scores, args.report)

    try:
        enforce_threshold(scores, args.min_score)
    except DeliveryBlocked as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"note globale {scores.global_:.3f} — version {current_version()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
