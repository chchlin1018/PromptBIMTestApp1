# PromptBIMTestApp1 — 台灣建築法規自動設計規則引擎

> SKILL.md v3.0 Addendum #3
> 法源：建築技術規則建築設計施工編、建築物耐震設計規範及解說（民國113年版）
> ⚠️ 本規則僅供 POC 概估，不替代結構技師簽證

---

## 設計原則

系統讀取台灣建築法規，編碼為 Python 規則引擎，在三個階段自動檢查：

```
Stage 1: Planner Agent 生成 BuildingPlan 前
  → 注入法規約束到 prompt（容積率、建蔽率、高度限制、退縮）
  → AI 在規劃時就遵守法規

Stage 2: Builder Agent 生成 IFC/USD 後
  → Checker Agent 用規則引擎逐條驗證
  → 不合規項自動標記 + 回傳 Planner 修正

Stage 3: 匯出報告
  → 合規檢查報告（通過/不通過/警告 + 法條引用）
```

---

## 專案結構新增

```
src/promptbim/
└── codes/                           # 台灣建築法規引擎
    ├── __init__.py
    ├── registry.py                  # 法規註冊中心
    ├── base.py                      # BaseRule 抽象類別
    ├── tw_building_code.py          # 建築技術規則（設計施工編）
    ├── tw_seismic_code.py           # 耐震設計規範
    ├── tw_fire_code.py              # 防火避難規則
    ├── tw_accessibility_code.py     # 無障礙設計規範
    ├── tw_parking_code.py           # 停車空間規則
    ├── tw_zoning_data.py            # 都市/非都市分區建蔽率容積率表
    ├── report.py                    # 合規檢查報告生成
    └── data/
        ├── zoning_bcr_far.json      # 各縣市分區 建蔽率/容積率
        ├── seismic_zones.json       # 震區係數表
        └── fire_ratings.json        # 防火時效對照表
```

---

## 規則引擎架構

```python
# codes/base.py
from pydantic import BaseModel
from enum import Enum

class Severity(str, Enum):
    PASS = "pass"          # 合規
    WARNING = "warning"    # 建議改善（不違規但接近上限）
    FAIL = "fail"          # 違規
    INFO = "info"          # 資訊提示

class CheckResult(BaseModel):
    rule_id: str            # "TW-BTC-25" (建築技術規則第25條)
    rule_name_zh: str       # "建築物高度限制"
    law_reference: str      # "建築技術規則建築設計施工編 第25條"
    severity: Severity
    message_zh: str         # "建築物高度 18.5m 超過限制 15.0m"
    actual_value: float | str
    limit_value: float | str
    suggestion: str = ""    # "建議減少一層樓或降低層高"

class BaseRule:
    """所有法規規則的抽象基底類別"""
    rule_id: str
    rule_name_zh: str
    law_reference: str

    def check(self, plan, land, zoning) -> CheckResult:
        raise NotImplementedError
```

---

## 法規 1：建築技術規則建築設計施工編

### 1.1 建蔽率與容積率（第25條/第161條）

```python
# codes/tw_building_code.py

# === 都市土地分區 建蔽率/容積率 ===
# 來源: 各縣市都市計畫書（以台北市為範例）
TAIPEI_ZONING = {
    "住一": {"bcr": 0.30, "far": 0.60},
    "住二": {"bcr": 0.35, "far": 1.20},
    "住三": {"bcr": 0.45, "far": 2.25},
    "住三之一": {"bcr": 0.45, "far": 1.60},
    "住三之二": {"bcr": 0.50, "far": 3.00},
    "住四": {"bcr": 0.50, "far": 3.00},
    "住四之一": {"bcr": 0.50, "far": 2.00},
    "商一": {"bcr": 0.55, "far": 3.60},
    "商二": {"bcr": 0.65, "far": 6.30},
    "商三": {"bcr": 0.65, "far": 5.60},
    "商四": {"bcr": 0.75, "far": 8.00},
    "工二": {"bcr": 0.55, "far": 2.10},
    "工三": {"bcr": 0.60, "far": 3.00},
}

# === 非都市土地 ===
NON_URBAN_ZONING = {
    "甲種建築用地": {"bcr": 0.60, "far": 2.40},
    "乙種建築用地": {"bcr": 0.60, "far": 2.40},
    "丙種建築用地": {"bcr": 0.40, "far": 1.20},
    "丁種建築用地": {"bcr": 0.70, "far": 3.00},
}
```

### 1.2 建築物高度限制（第24條之一）

```python
class HeightLimitRule(BaseRule):
    """建築物高度 ≤ 前面道路寬度 × 1.5 + 6m"""
    rule_id = "TW-BTC-24-1"
    rule_name_zh = "建築物高度限制"
    law_reference = "建築技術規則建築設計施工編 第24條之一"

    def check(self, plan, land, zoning) -> CheckResult:
        road_width = land.front_road_width_m  # 前面道路寬度
        height_limit = road_width * 1.5 + 6.0
        building_height = sum(s.height_m for s in plan.stories)

        if building_height > height_limit:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name_zh=self.rule_name_zh,
                law_reference=self.law_reference,
                severity=Severity.FAIL,
                message_zh=f"建築高度 {building_height:.1f}m 超過限制 {height_limit:.1f}m "
                           f"(前面道路寬 {road_width:.1f}m × 1.5 + 6 = {height_limit:.1f}m)",
                actual_value=building_height,
                limit_value=height_limit,
                suggestion="減少樓層數或降低層高",
            )
        return CheckResult(severity=Severity.PASS, ...)
```

### 1.3 樓梯規定（第33條）

```python
STAIR_RULES = {
    # 建築技術規則 第33條
    "居室面積 > 200㎡": {
        "min_width_m": 1.20,       # 樓梯淨寬 ≥ 1.2m
        "max_riser_height_cm": 20, # 級高 ≤ 20cm
        "min_tread_depth_cm": 24,  # 級深 ≥ 24cm
        "landing_required": True,   # 高度每 3m 設休息平台
    },
    "居室面積 ≤ 200㎡": {
        "min_width_m": 0.75,
        "max_riser_height_cm": 20,
        "min_tread_depth_cm": 21,
    },
    "直通樓梯": {
        "min_width_m": 1.20,
        "max_riser_height_cm": 18,
        "min_tread_depth_cm": 26,
    },
}
```

### 1.4 走廊寬度（第92條）

```python
CORRIDOR_RULES = {
    # 建築技術規則 第92條
    "雙側居室": {"min_width_m": 1.60},  # 走廊兩側皆有居室
    "單側居室": {"min_width_m": 1.20},  # 走廊僅一側有居室
    "醫院/學校_雙側": {"min_width_m": 2.40},
    "醫院/學校_單側": {"min_width_m": 1.80},
}
```

### 1.5 天花板高度（第26條）

```python
CEILING_HEIGHT_RULES = {
    # 建築技術規則 第26條
    "居室": {"min_height_m": 2.10},         # 一般居室 ≥ 2.1m
    "學校教室": {"min_height_m": 3.00},      # 學校教室 ≥ 3.0m
    "機械停車": {"min_height_m": 2.10},
    "地下室走廊": {"min_height_m": 1.90},
}
```

### 1.6 電梯設置規定（第55條）

```python
ELEVATOR_RULES = {
    # 建築技術規則 第55條
    "六層以上": {
        "required": True,
        "min_count": 1,
        "min_capacity_persons": 8,      # ≥ 8人
        "door_min_width_m": 0.90,
    },
    "十層以上": {
        "required": True,
        "min_count": 2,                  # ≥ 2台
        "emergency_elevator": True,      # 含緊急用電梯
    },
    "無障礙電梯": {
        "required_if": "有無障礙需求",
        "min_car_width_m": 1.10,
        "min_car_depth_m": 1.35,
    },
}
```

### 1.7 停車空間（第59條）

```python
PARKING_RULES = {
    # 建築技術規則 第59條
    "集合住宅": {
        "threshold_sqm": 150,  # 超過 150㎡ 需設停車位
        "ratio": "每 150㎡ 設 1 位",
        "calc": lambda total_area: max(1, int(total_area / 150)),
    },
    "辦公": {
        "threshold_sqm": 100,
        "ratio": "每 100㎡ 設 1 位",
        "calc": lambda total_area: max(1, int(total_area / 100)),
    },
    "商場": {
        "threshold_sqm": 100,
        "ratio": "每 100㎡ 設 1 位",
        "calc": lambda total_area: max(1, int(total_area / 100)),
    },
    "標準車位尺寸": {
        "width_m": 2.50,
        "depth_m": 5.50,
        "accessible_width_m": 3.50,
    },
}
```

---

## 法規 2：建築物耐震設計規範

### 2.1 震區分區與震區係數

```python
# codes/tw_seismic_code.py

# 來源: 建築物耐震設計規範及解說（民國113年版）
# 工址短週期水平譜加速度係數 Ss 及 工址一秒週期水平譜加速度係數 S1
# (簡化為 POC 等級，實務應查 Sederes 平台)

SEISMIC_ZONES_SIMPLIFIED = {
    # 城市: (Ss, S1, 地盤分類建議)
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
}

# 用途係數 I
IMPORTANCE_FACTOR = {
    "一般建築": 1.0,
    "學校/醫院/消防/警察": 1.25,
    "核電/水壩/危險物品": 1.50,
}
```

### 2.2 結構系統與耐震設計 POC 規則

```python
# POC 等級簡化耐震規則（概估用，非結構計算）

SEISMIC_DESIGN_RULES = {
    "柱斷面最小尺寸": {
        # 建築技術規則構造編 + 耐震規範
        "RC柱_≤5F": {"min_width_cm": 40, "min_depth_cm": 40},
        "RC柱_6~12F": {"min_width_cm": 50, "min_depth_cm": 50},
        "RC柱_>12F": {"min_width_cm": 60, "min_depth_cm": 60},
        "law": "建築技術規則構造編 + 耐震設計規範第六章",
    },
    "梁深最小值": {
        "rule": "梁深 ≥ 跨距/12（一般）或 跨距/10（連續梁）",
        "calc": lambda span_m: span_m / 12,
    },
    "樓板最小厚度": {
        "RC樓板_cm": 12,       # ≥ 12cm
        "PT樓板_cm": 16,       # 預力 ≥ 16cm
    },
    "剪力牆設置": {
        "建議": "10層以上RC建築應設剪力牆或含斜撐構架",
        "最小厚度_cm": 20,
        "配筋率_min": 0.0025,   # 水平+垂直各 ≥ 0.25%
    },
    "層間位移角限制": {
        "一般": 0.02,          # Δ/h ≤ 2%
        "含非結構牆": 0.01,    # 有隔間牆時 ≤ 1%
        "law": "耐震設計規範 2.12節",
    },
    "結構規則性": {
        "建議": "避免軟弱層、扭轉不規則、質量不規則",
        "軟弱層定義": "該層剛度 < 上層剛度 70%",
    },
}
```

### 2.3 Sederes 平台整合 (選用)

```python
# codes/tw_seismic_code.py
# 可選: 查詢國震中心 Sederes 平台取得精確震區參數
SEDERES_URL = "https://seaport.ncree.org/sederes/"
# POC 階段用內建簡化表，未來可接 API 取得精確值
```

---

## 法規 3：防火避難規則

```python
# codes/tw_fire_code.py

FIRE_SAFETY_RULES = {
    "防火構造要求": {
        # 建築技術規則 第69條
        "≤3F且總面積≤1500㎡": "得免用防火構造",
        ">3F或總面積>1500㎡": "應為防火構造",
        ">15F": "主要構造應為防火時效2hr以上",
    },
    "防火區劃": {
        # 建築技術規則 第79條
        "面積區劃": "每 1500㎡ 以防火牆/防火樓板區劃",
        "樓層區劃": "每層以防火樓板區劃",
        "防火門": "甲種防火門 (1hr) 或乙種防火門 (0.5hr)",
    },
    "直通樓梯步行距離": {
        # 建築技術規則 第93條
        "一般": {"max_distance_m": 50},
        "醫院/旅館": {"max_distance_m": 35},
        "15F以上": {"max_distance_m": 40},
    },
    "兩座直通樓梯": {
        # 建築技術規則 第95條
        "要求": "6F以上 且 該層居室面積 > 200㎡ 應設2座以上直通樓梯",
        "間距": "兩座樓梯間距 ≥ 對角線長度的 1/2",
    },
    "緊急進口": {
        # 建築技術規則 第108條
        "要求": "3F以上 各層應設進口（供消防車雲梯救援）",
        "尺寸": "寬 ≥ 75cm, 高 ≥ 120cm",
        "間距": "每 40m 設一處",
    },
    "排煙設備": {
        "自然排煙": "排煙窗面積 ≥ 該防煙區劃面積 2%",
        "機械排煙": "排煙量 ≥ 120 m³/min",
    },
    "安全梯": {
        "特別安全梯": "15F以上 或 地下3層以下 應設特別安全梯",
        "排煙室面積": "≥ 5㎡",
    },
}
```

---

## 法規 4：無障礙設計

```python
# codes/tw_accessibility_code.py

ACCESSIBILITY_RULES = {
    # 建築技術規則 第167條~第177條
    "適用範圍": "公共建築物應設置無障礙設施",
    "無障礙坡道": {
        "max_slope": 1/12,        # 坡度 ≤ 1:12
        "min_width_m": 0.90,       # 淨寬 ≥ 90cm
        "landing_every_m": 0.75,   # 高差每 75cm 設休息平台
        "handrail": True,          # 兩側扶手
    },
    "無障礙電梯": {
        "min_car_width_m": 1.10,
        "min_car_depth_m": 1.35,
        "min_door_width_m": 0.90,
        "braille_buttons": True,
        "audio_announce": True,
    },
    "無障礙廁所": {
        "min_area_sqm": 4.0,       # ≥ 4㎡ (含迴轉空間)
        "door_min_width_m": 0.90,
        "door_type": "外開或推拉",
        "grab_bars": True,
        "emergency_call": True,
    },
    "無障礙停車位": {
        "min_width_m": 3.50,       # 含卸載區
        "min_depth_m": 5.50,
        "min_count": "總數的 2%, 至少1位",
        "location": "最靠近出入口",
    },
    "無障礙通路": {
        "min_width_m": 1.30,       # 淨寬 ≥ 130cm
        "door_min_width_m": 0.80,
        "threshold_max_cm": 0.50,  # 門檻 ≤ 0.5cm
    },
}
```

---

## Checker Agent 整合

### 自動合規檢查流程

```python
# codes/registry.py
from .tw_building_code import (
    BCRRule, FARRule, HeightLimitRule, StairRule,
    CorridorRule, CeilingHeightRule, ElevatorRule, ParkingRule,
)
from .tw_seismic_code import SeismicDesignRule
from .tw_fire_code import FireEscapeRule, FireCompartmentRule
from .tw_accessibility_code import AccessibilityRule

ALL_RULES = [
    # 建蔽率容積率 (最高優先)
    BCRRule(),
    FARRule(),
    HeightLimitRule(),
    # 避難安全
    StairRule(),
    CorridorRule(),
    FireEscapeRule(),
    FireCompartmentRule(),
    # 使用機能
    CeilingHeightRule(),
    ElevatorRule(),
    ParkingRule(),
    # 結構安全
    SeismicDesignRule(),
    # 無障礙
    AccessibilityRule(),
]

def run_all_checks(plan, land, zoning) -> list[CheckResult]:
    """對 BuildingPlan 執行所有法規檢查"""
    results = []
    for rule in ALL_RULES:
        result = rule.check(plan, land, zoning)
        results.append(result)
    return results

def get_compliance_summary(results: list[CheckResult]) -> dict:
    """產生合規摘要"""
    fails = [r for r in results if r.severity == Severity.FAIL]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    passes = [r for r in results if r.severity == Severity.PASS]
    return {
        "total_rules": len(results),
        "passed": len(passes),
        "warnings": len(warnings),
        "failed": len(fails),
        "compliance_rate": len(passes) / len(results) * 100,
        "fail_details": [
            {"rule": f.rule_id, "law": f.law_reference, "issue": f.message_zh}
            for f in fails
        ],
    }
```

### Planner Agent 法規注入

```python
# agents/planner.py — 動態注入法規約束
def get_code_constraints(land, zoning) -> str:
    """為 Planner Agent 生成法規約束摘要"""
    return f"""
## 台灣建築法規約束 (MUST comply)

### 量體限制
- 建蔽率上限: {zoning.bcr_limit*100:.0f}% (建築面積 ≤ {land.area_sqm * zoning.bcr_limit:.1f} ㎡)
- 容積率上限: {zoning.far_limit*100:.0f}% (總樓地板面積 ≤ {land.area_sqm * zoning.far_limit:.1f} ㎡)
- 高度限制: {zoning.height_limit_m:.1f}m (前面道路寬 {land.front_road_width_m:.1f}m × 1.5 + 6)
- 退縮: 前{zoning.setback_front_m}m 後{zoning.setback_back_m}m 左{zoning.setback_left_m}m 右{zoning.setback_right_m}m

### 避難安全
- 走廊淨寬: 雙側居室 ≥ 1.6m, 單側 ≥ 1.2m
- 直通樓梯步行距離: ≤ 50m
- 6F以上且居室 > 200㎡: 需 2 座直通樓梯
- 樓梯淨寬 ≥ 1.2m, 級高 ≤ 20cm, 級深 ≥ 24cm

### 設備要求
- 6F 以上: 必須設電梯 (≥ 8人)
- 10F 以上: ≥ 2台電梯 (含緊急用)
- 停車: 辦公每100㎡ 1位, 住宅每150㎡ 1位

### 耐震 (地區: {land.city})
- 震區參數: Ss={zoning.seismic_ss}, S1={zoning.seismic_s1}
- RC柱建議最小: {zoning.min_column_cm}cm×{zoning.min_column_cm}cm

### 無障礙
- 公共建築必須設無障礙設施
- 至少1台無障礙電梯 (車廂 ≥ 1.1m×1.35m)
- 至少1處無障礙廁所 (≥ 4㎡)
- 至少1處無障礙停車位 (寬 ≥ 3.5m)
"""
```

---

## 合規報告輸出範例

```json
{
  "project": "L型辦公大樓",
  "check_date": "2026-03-25",
  "location": "台北市信義區",
  "zoning": "商三",
  "total_rules_checked": 15,
  "passed": 13,
  "warnings": 1,
  "failed": 1,
  "compliance_rate": 86.7,
  "results": [
    {
      "rule_id": "TW-BTC-BCR",
      "law_reference": "建築技術規則 第25條",
      "severity": "pass",
      "message": "建蔽率 58.2% ≤ 65.0% ✓"
    },
    {
      "rule_id": "TW-BTC-FAR",
      "law_reference": "建築技術規則 第161條",
      "severity": "pass",
      "message": "容積率 485.0% ≤ 560.0% ✓"
    },
    {
      "rule_id": "TW-BTC-24-1",
      "law_reference": "建築技術規則 第24條之一",
      "severity": "fail",
      "message": "建築高度 21.0m 超過限制 18.0m (道路寬8m×1.5+6=18m)",
      "suggestion": "減少1層或降低層高至3.0m"
    },
    {
      "rule_id": "TW-FIRE-93",
      "law_reference": "建築技術規則 第93條",
      "severity": "warning",
      "message": "最遠居室至直通樓梯距離 46m，接近上限 50m",
      "suggestion": "建議增設一座直通樓梯"
    },
    {
      "rule_id": "TW-SEISMIC",
      "law_reference": "耐震設計規範 第六章",
      "severity": "pass",
      "message": "RC柱 50×50cm ≥ 最小建議 50×50cm (6~12F) ✓"
    }
  ],
  "disclaimer": "本報告為 AI 概估用，不替代結構技師及建築師簽證。"
}
```

---

## 開發路線圖新增

在 P4 (AI Agent) 中整合：

### P4.5: 台灣建築法規引擎 (~3 天)
- [ ] `codes/base.py` — BaseRule + CheckResult
- [ ] `codes/tw_building_code.py` — 建蔽率/容積率/高度/樓梯/走廊/電梯/停車
- [ ] `codes/tw_seismic_code.py` — 震區簡化表 + 結構概估規則
- [ ] `codes/tw_fire_code.py` — 防火區劃/逃生距離/安全梯
- [ ] `codes/tw_accessibility_code.py` — 無障礙設施
- [ ] `codes/tw_zoning_data.py` — 各縣市分區 BCR/FAR JSON
- [ ] `codes/registry.py` — 規則註冊 + 批次檢查
- [ ] `codes/report.py` — 合規報告 JSON + 表格
- [ ] 整合到 Checker Agent 迴圈
- [ ] 整合到 Planner Agent prompt 注入
- **驗收:** 生成建築後自動執行 15+ 條法規檢查，輸出合規報告

---

## 法規資料來源 (公開)

| 法規 | 來源 | 網址 |
|------|------|------|
| 建築技術規則 | 全國法規資料庫 | law.moj.gov.tw |
| 耐震設計規範 | 內政部法規系統 | glrs.moi.gov.tw |
| 震區係數查詢 | 國震中心 Sederes | seaport.ncree.org/sederes |
| 防火避難評定 | 台灣建築中心 TABC | tabc.org.tw |
| 都市計畫分區 | 全國土地使用分區查詢 | luz.tcd.gov.tw |
| 無障礙設計 | 內政部營建署 | cpami.gov.tw |

> 所有法規資料皆為政府公開資訊，系統內建為 JSON/Python dict 形式。
> 未來可透過爬蟲或 API 自動更新（法規資料庫有 API）。

---

*Taiwan Building Code Addendum v1.0 | 2026-03-25*
