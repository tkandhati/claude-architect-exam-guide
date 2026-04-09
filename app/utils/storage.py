import json
import os
import random
from datetime import datetime
from typing import Any

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "results.json")
SAMPLE_QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "sample_questions.json")


def load_sample_questions(category: str | None = None, n: int | None = None) -> list[dict]:
    """Load questions from the static sample bank. Optionally filter by category and limit count."""
    try:
        with open(SAMPLE_QUESTIONS_FILE, "r") as f:
            questions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    if category:
        questions = [q for q in questions if q.get("category") == category]
    random.shuffle(questions)
    if n:
        questions = questions[:n]
    return questions


def _load_raw() -> list[dict]:
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_raw(data: list[dict]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_result(category: str, score: int, total: int, mode: str) -> None:
    """Save a quiz/simulation result. mode is 'quick' or 'simulation'."""
    results = _load_raw()
    results.append(
        {
            "category": category,
            "score": score,
            "total": total,
            "pct": round(score / total * 100, 1) if total > 0 else 0,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
        }
    )
    _save_raw(results)


def load_results() -> list[dict]:
    """Return all stored results."""
    return _load_raw()


def get_category_summary() -> dict[str, dict[str, Any]]:
    """Return avg score pct, attempt count, and last score per category."""
    results = _load_raw()
    summary: dict[str, dict] = {}
    for r in results:
        cat = r.get("category", "Unknown")
        if cat not in summary:
            summary[cat] = {"scores": [], "attempts": 0, "last_pct": 0}
        summary[cat]["scores"].append(r.get("pct", 0))
        summary[cat]["attempts"] += 1
        summary[cat]["last_pct"] = r.get("pct", 0)
    for cat in summary:
        scores = summary[cat]["scores"]
        summary[cat]["avg_pct"] = round(sum(scores) / len(scores), 1)
    return summary


def get_last_activity() -> str | None:
    """Return ISO timestamp of the most recent result, or None."""
    results = _load_raw()
    if not results:
        return None
    timestamps = [r.get("timestamp", "") for r in results if r.get("timestamp")]
    return max(timestamps) if timestamps else None


def get_overall_readiness() -> float:
    """Return overall readiness as a percentage (0-100)."""
    results = _load_raw()
    if not results:
        return 0.0
    pcts = [r.get("pct", 0) for r in results]
    return round(sum(pcts) / len(pcts), 1)
