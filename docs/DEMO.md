# DEMO.md — PromptBIM TSMC Demo 展示流程

> **Version:** mvp-v1.0.0-demo | **Duration:** 5 minutes | **Target:** TSMC Fab

---

## Quick Start

```bash
# Build & verify
cmake -B build -DBUILD_TESTS=ON && cmake --build build
ctest --test-dir build --output-on-failure

# Run demo (Python GUI)
conda activate promptbim
python -m promptbim.gui.main_window
```

---

## 5-Minute Demo Script

### Step 1: Scene Load (0:00-0:30)

**Action:** Load the TSMC factory scene

**Commands:**
```
> 給我整個場景的概覽
> scene info
```

**Expected Result:**
- 48 BIM entities displayed (structural + MEP + safety)
- 4 floor levels: B1(-4m), 1F(0m), 2F(8m), RF(16m)
- 100m x 70m semiconductor fab layout
- Total cost: ~NT$ 28.5M

**Talking Points:**
- 30+ entities modeled from real TSMC fab specs
- Three categories: structural, MEP, safety equipment
- Real-time NT$ cost calculation

---

### Step 2: Safety Inspection (0:30-1:30)

**Action:** Demonstrate safety equipment queries

**Commands:**
```
> 列出所有消防栓的位置
> 查詢灑水頭覆蓋率
> 檢查安全網完整性
```

**Expected Result:**
- 4 fire hydrants (one per quadrant, 1F)
- 6 sprinklers (ceiling-mounted, Zone A1-A3, B1-B3)
- 4 safety nets (perimeter, all 4 sides)
- 2 emergency exits (N & S)
- Safety audit: PASS

**Talking Points:**
- Natural language query in Chinese/English
- Automatic safety compliance audit
- Spatial coverage analysis

---

### Step 3: Real-Time Cost (1:30-2:30)

**Action:** Move equipment, observe cost changes

**Commands:**
```
> 目前場景的總成本是多少
> 移動冰水主機A到座標 (30, 25, -3)
> 成本變了多少
```

**Expected Result:**
- Total cost breakdown: structural 43.6%, MEP 52.2%
- Chiller A moved → pipe reconfiguration needed
- Cost delta displayed instantly

**Talking Points:**
- Instant cost delta on any change
- Taiwan NT$ pricing (real material costs)
- Pipe rerouting cost estimation

---

### Step 4: 4D Schedule (2:30-3:30)

**Action:** Show construction timeline

**Commands:**
```
> 查詢目前的施工進度
> 第三階段有哪些設備
```

**Expected Result:**
- 5 phases / 220 days total:
  1. Foundation & Structure (60 days, 19 entities)
  2. Envelope & Enclosure (45 days, 8 entities)
  3. MEP Installation (50 days, 9 entities)
  4. Piping & Ductwork (35 days, 4 entities)
  5. Commissioning & Safety (30 days, 8 entities)

**Talking Points:**
- Each entity assigned to a construction phase
- Timeline playback animation
- Phase-based entity filtering

---

### Step 5: AI + Collision (3:30-5:00)

**Action:** Full AI pipeline demo

**Commands:**
```
> 在座標 (60, 35, 0.5) 新增一台 AHU
> 檢查冰水主機附近有沒有碰撞
> 連接冷水泵A和冰水主機A
```

**Expected Result:**
- New AHU added, cost +NT$ 450,000
- No collision for chiller-1 (nearest: pump-1 at 5m)
- Pump→Chiller connection established, pipe cost estimated

**Talking Points:**
- Complete NL→AI→C++→Result pipeline
- AABB collision detection
- MEP topology connections
- All operations are undoable

---

## Architecture

```
User (Chinese/English NL)
  → NLParser (regex + Claude LLM)
    → IntentRouter (14 intent types → 13 actions)
      → AgentBridge.executeJson()
        → BIMSceneGraph (C++ core)
          → Result JSON → GUI display
```

## Test Coverage

| Suite | Tests | Status |
|-------|:-----:|:------:|
| ctest (C++) | 69+ | PASS |
| TSMC Demo (C++) | 20+ | PASS |
| E2E Integration | 53 | PASS |

---

*DEMO.md v1.0 | mvp-v1.0.0-demo | S-PTB-DEMO-TSMC*
