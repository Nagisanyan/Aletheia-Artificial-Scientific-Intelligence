from __future__ import annotations

import sys

from alethia.core.orchestration.orchestrator import Orchestrator


def main() -> None:
    print("Aletheia 0.3")
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("\n> ")

    result = Orchestrator().run(task)
    print(f"\nTask:\n{result.task}")
    print(f"\nGoal:\n{result.goal}")
    print(f"\nReasoning:\n{', '.join(step.content for step in result.reasoning_steps) or 'No explicit reasoning steps recorded.'}")
    print(f"\nTool:\n{result.tool_calls[-1] if result.tool_calls else 'No tool call recorded.'}")
    print(f"\nVerification:\n{result.uncertainty.upper()}")
    print(f"\nConclusion:\n{result.conclusion or 'No conclusion produced.'}")


if __name__ == "__main__":
    main()
