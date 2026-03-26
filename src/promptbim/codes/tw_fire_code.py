"""Taiwan Fire Safety Rules — fire compartment, egress, safety stairs.

Source: Building Technical Regulations (Design & Construction), Articles 69-108.
"""

from __future__ import annotations

from promptbim.codes.base import BaseRule, CheckResult
from promptbim.debug import get_logger

logger = get_logger("codes.tw_fire_code")


def _total_floor_area(plan) -> float:
    total = 0.0
    for story in plan.stories:
        if story.spaces:
            total += sum(s.area_sqm for s in story.spaces)
    return total


def _num_stories(plan) -> int:
    return len(plan.stories)


# ---------------------------------------------------------------------------
# Rule: Fire-Resistant Construction — Art. 69
# ---------------------------------------------------------------------------


class FireConstructionRule(BaseRule):
    rule_id = "TW-FIRE-69"
    rule_name_zh = "防火構造要求"
    law_reference = "建築技術規則建築設計施工編 第69條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        num = _num_stories(plan)
        total_area = _total_floor_area(plan)
        logger.debug("FireConstructionRule: stories=%d, total_area=%.1f", num, total_area)
        results: list[CheckResult] = []

        if num > 15:
            logger.debug("FireConstructionRule: >15F → fire rating 2hr required")
            results.append(
                self._info(
                    f"建築 {num} 層 > 15 層，主要構造應為防火時效 2hr 以上",
                    actual=num,
                    limit=15,
                )
            )
        elif num > 3 or total_area > 1500:
            results.append(
                self._info(
                    f"建築 {num} 層/總面積 {total_area:.0f}㎡，應為防火構造",
                    actual=f"{num}F/{total_area:.0f}㎡",
                    limit="3F/1500㎡",
                )
            )
        else:
            results.append(
                self._pass(
                    f"建築 {num} 層/總面積 {total_area:.0f}㎡ <= 3F且1500㎡，得免防火構造",
                )
            )
        return results


# ---------------------------------------------------------------------------
# Rule: Fire Compartment — Art. 79
# ---------------------------------------------------------------------------


class FireCompartmentRule(BaseRule):
    rule_id = "TW-FIRE-79"
    rule_name_zh = "防火區劃"
    law_reference = "建築技術規則建築設計施工編 第79條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        logger.debug("FireCompartmentRule: checking %d stories", len(plan.stories))
        results: list[CheckResult] = []
        for story in plan.stories:
            floor_area = sum(s.area_sqm for s in story.spaces) if story.spaces else 0
            logger.debug("FireCompartmentRule: %s floor_area=%.1f sqm", story.name, floor_area)
            if floor_area > 1500:
                compartments_needed = int(floor_area / 1500)
                results.append(
                    self._warning(
                        f"{story.name} 面積 {floor_area:.0f}㎡ > 1500㎡，需 {compartments_needed + 1} 個防火區劃",
                        actual=f"{floor_area:.0f}㎡",
                        limit="1500㎡",
                        suggestion="以防火牆/防火樓板劃分防火區劃",
                    )
                )
        if not results:
            results.append(self._pass("各樓層面積均 <= 1500㎡，防火區劃符合規定"))
        return results


# ---------------------------------------------------------------------------
# Rule: Egress Distance — Art. 93
# ---------------------------------------------------------------------------


class FireEscapeRule(BaseRule):
    rule_id = "TW-FIRE-93"
    rule_name_zh = "直通樓梯步行距離"
    law_reference = "建築技術規則建築設計施工編 第93條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        num = _num_stories(plan)
        max_dist = 50.0
        if num > 15:
            max_dist = 40.0
        logger.debug("FireEscapeRule: stories=%d, max_egress_dist=%.1fm", num, max_dist)

        results: list[CheckResult] = []
        # Estimate max distance from building dimensions
        if plan.building_footprint and len(plan.building_footprint) >= 3:
            xs = [p[0] for p in plan.building_footprint]
            ys = [p[1] for p in plan.building_footprint]
            diagonal = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
            # Worst-case egress ≈ half diagonal (stair at one end)
            est_egress = diagonal / 2
            logger.debug(
                "FireEscapeRule: diagonal=%.1fm, est_egress=%.1fm vs limit=%.1fm",
                diagonal,
                est_egress,
                max_dist,
            )

            if est_egress > max_dist:
                results.append(
                    self._fail(
                        f"估算最遠逃生距離 {est_egress:.1f}m > {max_dist}m",
                        actual=round(est_egress, 1),
                        limit=max_dist,
                        suggestion="增設直通樓梯或縮短建築平面最大尺寸",
                    )
                )
            elif est_egress > max_dist * 0.9:
                results.append(
                    self._warning(
                        f"估算最遠逃生距離 {est_egress:.1f}m 接近上限 {max_dist}m",
                        actual=round(est_egress, 1),
                        limit=max_dist,
                        suggestion="建議增設一座直通樓梯",
                    )
                )
            else:
                results.append(
                    self._pass(
                        f"估算最遠逃生距離 {est_egress:.1f}m <= {max_dist}m",
                        actual=round(est_egress, 1),
                        limit=max_dist,
                    )
                )
        else:
            results.append(self._info("無建築輪廓，無法估算逃生距離"))

        return results


# ---------------------------------------------------------------------------
# Rule: Two Egress Stairs — Art. 95
# ---------------------------------------------------------------------------


class TwoStairsRule(BaseRule):
    rule_id = "TW-FIRE-95"
    rule_name_zh = "兩座直通樓梯"
    law_reference = "建築技術規則建築設計施工編 第95條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        num = _num_stories(plan)
        logger.debug("TwoStairsRule: stories=%d", num)
        if num < 6:
            return [self._pass(f"建築 {num} 層 < 6 層，不強制兩座直通樓梯")]

        results: list[CheckResult] = []
        for story in plan.stories:
            floor_area = sum(s.area_sqm for s in story.spaces) if story.spaces else 0
            if floor_area > 200:
                results.append(
                    self._info(
                        f"{story.name} 居室面積 {floor_area:.0f}㎡ > 200㎡，6F以上需設 2 座以上直通樓梯",
                        actual=f"{floor_area:.0f}㎡",
                        limit="200㎡",
                    )
                )
        if not results:
            results.append(self._pass("各層居室面積均 <= 200㎡，單一直通樓梯即可"))
        return results


# ---------------------------------------------------------------------------
# Rule: Safety Stair — Art. 97
# ---------------------------------------------------------------------------


class SafetyStairRule(BaseRule):
    rule_id = "TW-FIRE-97"
    rule_name_zh = "特別安全梯"
    law_reference = "建築技術規則建築設計施工編 第97條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        num = _num_stories(plan)
        logger.debug("SafetyStairRule: stories=%d (threshold=15)", num)
        if num >= 15:
            return [
                self._info(
                    f"建築 {num} 層 >= 15 層，應設特別安全梯（排煙室面積 >= 5㎡）",
                    actual=num,
                    limit=15,
                )
            ]
        return [self._pass(f"建築 {num} 層 < 15 層，不強制特別安全梯")]
