"""Taiwan Accessibility Design Rules.

Source: Building Technical Regulations, Articles 167-177.
"""

from __future__ import annotations

from promptbim.codes.base import BaseRule, CheckResult
from promptbim.debug import get_logger

logger = get_logger("codes.tw_accessibility_code")


class AccessibilityRule(BaseRule):
    rule_id = "TW-ACCESS"
    rule_name_zh = "無障礙設施"
    law_reference = "建築技術規則建築設計施工編 第167~177條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        results: list[CheckResult] = []
        zone = zoning.zone_type
        num = len(plan.stories)
        is_public = zone in ("commercial", "office", "public", "mixed")
        logger.debug("AccessibilityRule: zone=%s, stories=%d, is_public=%s", zone, num, is_public)

        # Public / commercial buildings must have accessibility facilities

        if not is_public:
            results.append(
                self._info(
                    f"用途分區「{zone}」，非公共建築可免部分無障礙設施（但仍建議設置）",
                )
            )
            return results

        # Ramp
        results.append(
            self._info(
                "公共建築應設無障礙坡道（坡度 <= 1:12，淨寬 >= 0.9m，兩側扶手）",
            )
        )

        # Elevator
        if num >= 2:
            results.append(
                self._info(
                    f"建築 {num} 層 >= 2 層，至少 1 台無障礙電梯（車廂 >= 1.1m x 1.35m，門寬 >= 0.9m）",
                    actual=num,
                    limit=2,
                )
            )

        # Accessible toilet
        results.append(
            self._info(
                "應設至少 1 處無障礙廁所（>= 4㎡，外開門/推拉門，門寬 >= 0.9m）",
            )
        )

        # Accessible parking
        results.append(
            self._info(
                "應設至少 1 處無障礙停車位（寬 >= 3.5m，深 >= 5.5m，最靠近出入口）",
            )
        )

        # Accessible path
        results.append(
            self._info(
                "無障礙通路淨寬 >= 1.3m，門寬 >= 0.8m，門檻 <= 0.5cm",
            )
        )

        return results
