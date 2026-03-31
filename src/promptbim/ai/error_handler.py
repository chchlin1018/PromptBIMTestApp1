"""ErrorHandler — Graceful error recovery for AI parsing failures.

Provides user-friendly fallback messages when the AI layer
cannot parse or execute a command.
"""

from __future__ import annotations

from typing import Any

from promptbim.ai.nl_parser import BIMIntent, IntentType
from promptbim.debug import get_logger

logger = get_logger("ai.error_handler")


class ErrorHandler:
    """Handles AI parsing and execution errors with friendly fallbacks."""

    # Example commands for help messages
    EXAMPLES = {
        "create": [
            "建立一面牆 (Create a wall)",
            "新增一根柱子在 (5, 10, 0)",
            "add a chiller at (20, 15, 0)",
        ],
        "move": [
            "移動 chiller-1 到 (10, 20, 0)",
            "move pump-1 to (5, 5, 0)",
        ],
        "query": [
            "查詢所有的牆",
            "find all chillers",
            "show scene info",
        ],
        "delete": [
            "刪除 wall-1",
            "remove chiller-2",
        ],
        "cost": [
            "成本是多少？",
            "total cost",
        ],
    }

    def handle_parse_failure(self, text: str) -> str:
        """Generate a friendly response when parsing fails."""
        logger.info("Parse failure for: %s", text[:80])
        examples = self._pick_relevant_examples(text)
        msg = "我無法理解這個指令。請試試以下格式：\n"
        for ex in examples:
            msg += f"  • {ex}\n"
        return msg

    def handle_execution_error(self, intent: BIMIntent, error: str) -> str:
        """Generate a friendly response when execution fails."""
        logger.warning(
            "Execution error: intent=%s, error=%s",
            intent.intent_type.value, error,
        )
        action = intent.intent_type.value

        if "not found" in error.lower():
            return (
                f"找不到指定的元件。請確認 ID 或名稱是否正確。\n"
                f"提示：使用「show scene info」查看所有元件。"
            )
        if "already exists" in error.lower():
            return f"該元件已存在。請使用不同的 ID。"

        return f"執行 {action} 時發生錯誤：{error}"

    def handle_low_confidence(self, intent: BIMIntent) -> str:
        """Suggest refinement when confidence is low."""
        return (
            f"我不太確定你的意思（信心度: {intent.confidence:.0%}）。\n"
            f"你是想要「{intent.intent_type.value}」嗎？\n"
            f"請更具體地描述，或使用 entity ID（如 chiller-1）。"
        )

    def handle_missing_info(self, intent: BIMIntent) -> str:
        """Ask for missing required information."""
        missing = []
        if intent.intent_type in (IntentType.MOVE, IntentType.CREATE) and not intent.position:
            missing.append("位置座標 (x, y, z)")
        if intent.intent_type == IntentType.CREATE and not intent.entity_type:
            missing.append("元件類型 (wall/column/chiller/...)")
        if intent.intent_type in (IntentType.DELETE, IntentType.MOVE, IntentType.ROTATE) and not intent.entity_id:
            missing.append("元件 ID (如 chiller-1)")

        if missing:
            return "需要更多資訊：\n" + "\n".join(f"  • {m}" for m in missing)
        return ""

    def _pick_relevant_examples(self, text: str) -> list[str]:
        """Pick the most relevant examples based on the input text."""
        lower = text.lower()
        results = []

        # Score categories by keyword match
        scores: dict[str, int] = {}
        for category, examples in self.EXAMPLES.items():
            score = 0
            for kw in category.split():
                if kw in lower:
                    score += 2
            scores[category] = score

        # Return examples from highest-scoring categories
        for cat in sorted(scores, key=scores.get, reverse=True)[:2]:
            results.extend(self.EXAMPLES[cat][:2])

        if not results:
            # Default: one from each category
            for examples in self.EXAMPLES.values():
                results.append(examples[0])
                if len(results) >= 4:
                    break

        return results
