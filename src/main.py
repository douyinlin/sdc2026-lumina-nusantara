"""CLI smoke demo. Web entry point is app.py (modified 2026-10-20)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.demo import compare_skills, load_demo


def main() -> None:
    data = load_demo()
    print("Synthetic demo only. Skill coverage is not hiring probability.")
    print(json.dumps(compare_skills(data["profile"]["skills"], data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
