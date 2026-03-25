"""Taiwan Seismic Design Code — simplified POC rules.

Source: Seismic Design Specifications and Commentary for Buildings (2024 edition).
"""

from __future__ import annotations

from promptbim.codes.base import BaseRule, CheckResult

# -- Simplified seismic zone coefficients -----------------------------------

SEISMIC_ZONES: dict[str, dict] = {
    "台北市": {"Ss": 0.60, "S1": 0.30, "site_class": "第三類（台北盆地軟弱土層）",
               "notes": "需考量盆地效應及土壤液化"},
    "新北市": {"Ss": 0.60, "S1": 0.30, "site_class": "第二~三類"},
    "桃園市": {"Ss": 0.55, "S1": 0.28, "site_class": "第二類"},
    "台中市": {"Ss": 0.65, "S1": 0.32, "site_class": "第二類",
               "notes": "鄰近車籠埔斷層"},
    "台南市": {"Ss": 0.70, "S1": 0.35, "site_class": "第二類"},
    "高雄市": {"Ss": 0.55, "S1": 0.28, "site_class": "第二類"},
    "花蓮縣": {"Ss": 0.80, "S1": 0.45, "site_class": "第一~二類",
               "notes": "高震區，鄰近多條活動斷層"},
    "宜蘭縣": {"Ss": 0.70, "S1": 0.35, "site_class": "第二類"},
    "嘉義市": {"Ss": 0.80, "S1": 0.40, "site_class": "第二類",
               "notes": "鄰近梅山斷層"},
    "嘉義縣": {"Ss": 0.75, "S1": 0.38, "site_class": "第二類"},
    "新竹市": {"Ss": 0.55, "S1": 0.28, "site_class": "第二類"},
    "新竹縣": {"Ss": 0.55, "S1": 0.28, "site_class": "第二類"},
    "苗栗縣": {"Ss": 0.60, "S1": 0.30, "site_class": "第二類"},
    "彰化縣": {"Ss": 0.65, "S1": 0.32, "site_class": "第二類"},
    "南投縣": {"Ss": 0.75, "S1": 0.40, "site_class": "第二類",
               "notes": "鄰近車籠埔斷層"},
    "雲林縣": {"Ss": 0.70, "S1": 0.35, "site_class": "第二類"},
    "屏東縣": {"Ss": 0.60, "S1": 0.30, "site_class": "第二類"},
    "台東縣": {"Ss": 0.70, "S1": 0.35, "site_class": "第二類"},
    "澎湖縣": {"Ss": 0.30, "S1": 0.15, "site_class": "第二類"},
    "基隆市": {"Ss": 0.60, "S1": 0.30, "site_class": "第二類"},
}

# Default for unknown cities
DEFAULT_SEISMIC = {"Ss": 0.60, "S1": 0.30, "site_class": "第二類"}

# -- Importance factor ------------------------------------------------------

IMPORTANCE_FACTOR: dict[str, float] = {
    "一般建築": 1.0,
    "學校": 1.25,
    "醫院": 1.25,
    "消防": 1.25,
    "警察": 1.25,
    "核電": 1.50,
    "水壩": 1.50,
}

# -- Minimum column size by stories (POC estimate) --------------------------

MIN_COLUMN_CM: dict[str, int] = {
    "<=5F": 40,
    "6~12F": 50,
    ">12F": 60,
}


def get_min_column_cm(num_stories: int) -> int:
    if num_stories <= 5:
        return 40
    if num_stories <= 12:
        return 50
    return 60


def get_seismic_params(city: str) -> dict:
    return SEISMIC_ZONES.get(city, DEFAULT_SEISMIC)


# ---------------------------------------------------------------------------
# Seismic Design Rule
# ---------------------------------------------------------------------------

class SeismicDesignRule(BaseRule):
    rule_id = "TW-SEISMIC"
    rule_name_zh = "耐震設計概估"
    law_reference = "耐震設計規範 第六章 + 建築技術規則構造編"

    def check(self, plan, land, zoning) -> list[CheckResult]:
        num = len(plan.stories)
        if num == 0:
            return [self._pass("無樓層，不適用")]

        # Determine city from land attributes (best-effort)
        city = getattr(land, "city", "") or ""
        params = get_seismic_params(city)

        results: list[CheckResult] = []

        # Info: seismic zone
        ss = params["Ss"]
        s1 = params["S1"]
        site_class = params["site_class"]
        notes = params.get("notes", "")
        msg = f"地區: {city or '未指定'}，Ss={ss}, S1={s1}, 地盤: {site_class}"
        if notes:
            msg += f"（{notes}）"
        results.append(self._info(msg, actual=f"Ss={ss}", limit=f"S1={s1}"))

        # Minimum column size recommendation
        min_col = get_min_column_cm(num)
        results.append(self._info(
            f"建築 {num} 層，RC柱建議最小 {min_col}cm x {min_col}cm",
            actual=num,
            limit=f"{min_col}cm",
        ))

        # Shear wall recommendation for 10+ stories
        if num >= 10:
            results.append(self._warning(
                f"建築 {num} 層 >= 10 層，建議設置剪力牆或含斜撐構架",
                actual=num,
                limit=10,
                suggestion="增設 RC 剪力牆，最小厚度 20cm",
            ))

        return results
