"""Taiwan Building Technical Regulations — Design & Construction.

Rules cover: BCR, FAR, height, stairs, corridors, ceiling height, elevators,
and parking requirements.
"""

from __future__ import annotations

from promptbim.codes.base import BaseRule, CheckResult
from promptbim.debug import get_logger

logger = get_logger("codes.tw_building_code")


# ---------------------------------------------------------------------------
# Helper: compute total floor area from plan
# ---------------------------------------------------------------------------

def _total_floor_area(plan) -> float:
    """Sum of slab areas across all stories."""
    total = 0.0
    for story in plan.stories:
        if story.slab_boundary and len(story.slab_boundary) >= 3:
            total += _polygon_area(story.slab_boundary)
        elif story.spaces:
            total += sum(s.area_sqm for s in story.spaces)
    return total


def _polygon_area(coords: list[tuple[float, float]]) -> float:
    n = len(coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def _footprint_area(plan) -> float:
    if plan.building_footprint and len(plan.building_footprint) >= 3:
        return _polygon_area(plan.building_footprint)
    return 0.0


def _building_height(plan) -> float:
    if not plan.stories:
        return 0.0
    top = plan.stories[-1]
    return top.elevation_m + top.height_m


def _num_stories(plan) -> int:
    return len(plan.stories)


# ---------------------------------------------------------------------------
# Rule 1: Building Coverage Ratio (BCR) — Art. 25
# ---------------------------------------------------------------------------

class BCRRule(BaseRule):
    rule_id = "TW-BTC-BCR"
    rule_name_zh = "建蔽率檢查"
    law_reference = "建築技術規則建築設計施工編 第25條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        fp_area = _footprint_area(plan)
        logger.debug("BCRRule: footprint_area=%.2f, land_area=%.2f", fp_area, land.area_sqm)
        if land.area_sqm <= 0:
            return [self._info("土地面積為零，無法計算建蔽率")]
        actual_bcr = fp_area / land.area_sqm
        limit = zoning.bcr_limit
        logger.debug("BCRRule: actual_bcr=%.4f, limit=%.4f → %s", actual_bcr, limit,
                      "FAIL" if actual_bcr > limit else "PASS")

        if actual_bcr > limit:
            return [self._fail(
                f"建蔽率 {actual_bcr:.1%} 超過上限 {limit:.1%}",
                actual=round(actual_bcr, 4),
                limit=round(limit, 4),
                suggestion="縮小建築投影面積",
            )]
        if actual_bcr > limit * 0.95:
            return [self._warning(
                f"建蔽率 {actual_bcr:.1%} 接近上限 {limit:.1%}",
                actual=round(actual_bcr, 4),
                limit=round(limit, 4),
            )]
        return [self._pass(
            f"建蔽率 {actual_bcr:.1%} <= {limit:.1%}",
            actual=round(actual_bcr, 4),
            limit=round(limit, 4),
        )]


# ---------------------------------------------------------------------------
# Rule 2: Floor Area Ratio (FAR) — Art. 161
# ---------------------------------------------------------------------------

class FARRule(BaseRule):
    rule_id = "TW-BTC-FAR"
    rule_name_zh = "容積率檢查"
    law_reference = "建築技術規則建築設計施工編 第161條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        total_area = _total_floor_area(plan)
        logger.debug("FARRule: total_floor_area=%.2f, land_area=%.2f", total_area, land.area_sqm)
        if land.area_sqm <= 0:
            return [self._info("土地面積為零，無法計算容積率")]
        actual_far = total_area / land.area_sqm
        limit = zoning.far_limit
        logger.debug("FARRule: actual_far=%.4f, limit=%.4f → %s", actual_far, limit,
                      "FAIL" if actual_far > limit else "PASS")

        if actual_far > limit:
            return [self._fail(
                f"容積率 {actual_far:.2f} 超過上限 {limit:.2f}",
                actual=round(actual_far, 4),
                limit=round(limit, 4),
                suggestion="減少樓層數或縮小各層面積",
            )]
        if actual_far > limit * 0.95:
            return [self._warning(
                f"容積率 {actual_far:.2f} 接近上限 {limit:.2f}",
                actual=round(actual_far, 4),
                limit=round(limit, 4),
            )]
        return [self._pass(
            f"容積率 {actual_far:.2f} <= {limit:.2f}",
            actual=round(actual_far, 4),
            limit=round(limit, 4),
        )]


# ---------------------------------------------------------------------------
# Rule 3: Height Limit — Art. 24-1
# ---------------------------------------------------------------------------

class HeightLimitRule(BaseRule):
    rule_id = "TW-BTC-24-1"
    rule_name_zh = "建築物高度限制"
    law_reference = "建築技術規則建築設計施工編 第24條之一"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        height = _building_height(plan)
        limit = zoning.height_limit_m
        logger.debug("HeightLimitRule: height=%.2fm, limit=%.2fm → %s", height, limit,
                      "FAIL" if height > limit else "PASS")

        if height > limit:
            return [self._fail(
                f"建築高度 {height:.1f}m 超過限制 {limit:.1f}m",
                actual=round(height, 2),
                limit=round(limit, 2),
                suggestion="減少樓層數或降低層高",
            )]
        if height > limit * 0.95:
            return [self._warning(
                f"建築高度 {height:.1f}m 接近限制 {limit:.1f}m",
                actual=round(height, 2),
                limit=round(limit, 2),
            )]
        return [self._pass(
            f"建築高度 {height:.1f}m <= {limit:.1f}m",
            actual=round(height, 2),
            limit=round(limit, 2),
        )]


# ---------------------------------------------------------------------------
# Rule 4: Stairs — Art. 33
# ---------------------------------------------------------------------------

class StairRule(BaseRule):
    rule_id = "TW-BTC-33"
    rule_name_zh = "樓梯設置規定"
    law_reference = "建築技術規則建築設計施工編 第33條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        num = _num_stories(plan)
        logger.debug("StairRule: num_stories=%d", num)
        if num <= 1:
            return [self._pass("單層建築無樓梯要求")]

        total_area = _total_floor_area(plan)
        area_per_floor = total_area / num if num else 0
        logger.debug("StairRule: area_per_floor=%.1f sqm", area_per_floor)

        results: list[CheckResult] = []
        if area_per_floor > 200:
            results.append(self._info(
                f"每層面積 {area_per_floor:.0f}㎡ > 200㎡，樓梯淨寬需 >= 1.2m、級高 <= 20cm、級深 >= 24cm",
                actual=f"{area_per_floor:.0f}㎡",
                limit="200㎡",
            ))
        else:
            results.append(self._info(
                f"每層面積 {area_per_floor:.0f}㎡ <= 200㎡，樓梯淨寬需 >= 0.75m",
                actual=f"{area_per_floor:.0f}㎡",
                limit="200㎡",
            ))

        return results


# ---------------------------------------------------------------------------
# Rule 5: Corridors — Art. 92
# ---------------------------------------------------------------------------

class CorridorRule(BaseRule):
    rule_id = "TW-BTC-92"
    rule_name_zh = "走廊寬度規定"
    law_reference = "建築技術規則建築設計施工編 第92條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        logger.debug("CorridorRule: checking %d stories", len(plan.stories))
        results: list[CheckResult] = []
        for story in plan.stories:
            for space in story.spaces:
                if space.space_type == "corridor":
                    # Estimate width from area / length heuristic
                    if space.area_sqm > 0 and space.boundary and len(space.boundary) >= 2:
                        # Use minimum dimension as estimated width
                        xs = [p[0] for p in space.boundary]
                        ys = [p[1] for p in space.boundary]
                        w = min(max(xs) - min(xs), max(ys) - min(ys))
                        logger.debug("CorridorRule: %s/%s width=%.2fm", story.name, space.name, w)
                        if w < 1.2:
                            results.append(self._fail(
                                f"{story.name} 走廊「{space.name}」寬 {w:.2f}m < 1.2m (單側居室最低)",
                                actual=round(w, 2),
                                limit=1.2,
                                suggestion="加寬走廊至 1.2m 以上",
                            ))
        if not results:
            results.append(self._pass("走廊寬度符合規定（或無走廊空間）"))
        return results


# ---------------------------------------------------------------------------
# Rule 6: Ceiling Height — Art. 26
# ---------------------------------------------------------------------------

class CeilingHeightRule(BaseRule):
    rule_id = "TW-BTC-26"
    rule_name_zh = "天花板高度規定"
    law_reference = "建築技術規則建築設計施工編 第26條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        logger.debug("CeilingHeightRule: checking %d stories", len(plan.stories))
        results: list[CheckResult] = []
        for story in plan.stories:
            # Net ceiling height = story height - slab thickness
            net_height = story.height_m - story.slab_thickness_m
            logger.debug("CeilingHeightRule: %s net_height=%.2fm (h=%.2f - slab=%.2f)",
                          story.name, net_height, story.height_m, story.slab_thickness_m)
            if net_height < 2.1:
                results.append(self._fail(
                    f"{story.name} 淨高 {net_height:.2f}m < 2.1m (居室最低)",
                    actual=round(net_height, 2),
                    limit=2.1,
                    suggestion="增加層高或減小樓板厚度",
                ))
        if not results:
            results.append(self._pass("所有樓層淨高 >= 2.1m"))
        return results


# ---------------------------------------------------------------------------
# Rule 7: Elevators — Art. 55
# ---------------------------------------------------------------------------

class ElevatorRule(BaseRule):
    rule_id = "TW-BTC-55"
    rule_name_zh = "電梯設置規定"
    law_reference = "建築技術規則建築設計施工編 第55條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        num = _num_stories(plan)
        logger.debug("ElevatorRule: num_stories=%d", num)
        if num < 6:
            return [self._pass(f"建築 {num} 層 < 6 層，不強制設電梯")]

        results: list[CheckResult] = []
        if num >= 6:
            results.append(self._info(
                f"建築 {num} 層 >= 6 層，需設至少 1 台電梯（>= 8人）",
                actual=num,
                limit=6,
            ))
        if num >= 10:
            results.append(self._info(
                f"建築 {num} 層 >= 10 層，需設至少 2 台電梯（含緊急用）",
                actual=num,
                limit=10,
            ))
        return results


# ---------------------------------------------------------------------------
# Rule 8: Parking — Art. 59
# ---------------------------------------------------------------------------

PARKING_THRESHOLDS = {
    "residential": 150,
    "commercial": 100,
    "office": 100,
    "industrial": 200,
}


class ParkingRule(BaseRule):
    rule_id = "TW-BTC-59"
    rule_name_zh = "停車空間規定"
    law_reference = "建築技術規則建築設計施工編 第59條"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        total_area = _total_floor_area(plan)
        zone = zoning.zone_type
        threshold = PARKING_THRESHOLDS.get(zone, 150)
        required_spaces = max(1, int(total_area / threshold)) if total_area >= threshold else 0
        logger.debug("ParkingRule: total_area=%.1f, zone=%s, threshold=%d, required=%d",
                      total_area, zone, threshold, required_spaces)

        if required_spaces == 0:
            return [self._pass(
                f"總樓地板 {total_area:.0f}㎡ < {threshold}㎡，無停車需求",
                actual=f"{total_area:.0f}㎡",
                limit=f"{threshold}㎡",
            )]

        return [self._info(
            f"總樓地板 {total_area:.0f}㎡，需設 {required_spaces} 個停車位 "
            f"（每 {threshold}㎡ 設 1 位）",
            actual=f"{total_area:.0f}㎡",
            limit=f"每{threshold}㎡/位",
        )]
