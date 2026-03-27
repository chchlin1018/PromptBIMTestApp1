# Reality Matrix 統一產品架構：IDTF × PromptToBuild × PromptToOperate

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **性質:** 產品架構關聯分析 — IDTF 底層框架與上層應用的技術銜接
> **前置文件:** IDTF v3.5 · PromptToBuild Architecture v2.1 · ILOS-FAB 技術文件集

---

## 1. 三者的本質關係

```
IDTF v3.5         = 底層框架（語言 + 資料中樞 + 代理平台）
PromptToBuild      = 上層應用 — 設計建造階段
PromptToOperate    = 上層應用 — 營運維護階段
```

**IDTF 不是一個產品，而是兩個產品共用的底層技術棧。**

```
                        使用者
                    ┌─────┴─────┐
             PromptToBuild   PromptToOperate
             (設計→建造→交付)  (交付→營運→維護→退役)
                    │              │
                    └──────┬───────┘
                           │
                    ┌──────▼──────┐
                    │  IDTF v3.5  │
                    │  底層共用框架 │
                    └─────────────┘
```

---

## 2. IDTF 核心組件與產品對應

| IDTF 組件 | 全稱 | 本質 | PromptToBuild | PromptToOperate |
|-----------|------|------|:-------------:|:---------------:|
| **IADL** | Industrial Asset Definition Language | 資產「是什麼」| ★ 核心 — 定義設備型錄 | ★ 核心 — 活化為數位分身 |
| **FDL** | Factory Design Language | 工廠「怎麼排」| ★ 核心 — 佈局設計 | ★ 參考 — 營運基準比對 |
| **NDH** | Neutral Data Hub | 資料「怎麼流」| ○ 輕度 — 設計資料交換 | ★ 核心 — 即時資料匯流排 |
| **MCP** | Multi-Agent Control Plane | AI「怎麼控」| ○ 設計 Agent | ★ 核心 — 營運/維護 Agent |
| **Asset Servants** | 記憶體中活躍物件 | 活的數位分身 | ○ 不需要 | ★ 核心 — 每個設備一個 |
| **OpenUSD** | 3D 場景描述 | 幾何 + 語義 SSOT | ★ 核心 — 3D 模型 | ★ 核心 — 3D 視覺化 |
| **ilos: metadata** | ILOS 元數據規範 | 連接設計與營運 | ★ 產出者 | ★ 消費者 |

---

## 3. 產品生命週期劃分

```
時間軸 →→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→

 概念    規劃    設計    施工    試車    營運    維護    擴建    退役
  ├───────┴───────┴───────┴───────┴───────┤
  │         PromptToBuild                  │
  │  輸入: 自然語言 + 土地 + 法規          │
  │  輸出: USD + Revit + IFC + BOM        │
  └────────────────────────┬───────────────┘
                           │ 交付物 = USD + IADL + FDL + ilos: metadata
                           │ (設計資料直接成為營運輸入)
  ┌────────────────────────▼───────────────────────────────────┐
  │                    PromptToOperate                          │
  │  輸入: Build 階段的 USD + 即時感測器 + 維護記錄            │
  │  輸出: Dashboard + 警報 + 工單 + 報表 + ESG               │
  └────────────────────────────────────────────────────────────┘
```

### 兩個產品的比較

| 維度 | PromptToBuild | PromptToOperate |
|------|:-------------:|:---------------:|
| 生命週期 | 概念 → 設計 → 建造 → 交付 | 交付 → 營運 → 維護 → 退役 |
| 使用者 | 建築師 / FAB 工程師 / 設備商 | 廠務 / 設備維護 / 營運管理 |
| 核心動作 | 「建一座晶圓廠」 | 「管這座晶圓廠」 |
| AI 問題 | 「設計 3F 潔淨室 UPW 配管」 | 「預測哪台幫浦會壞」 |
| 時間尺度 | 月/年（專案制） | 秒/分鐘（即時制） |
| 資料方向 | 產生 USD（設計→模型） | 消費 + 更新 USD（感測器→模型） |
| IDTF 主力 | IADL + FDL + ILOS | NDH + MCP + Asset Servants |
| 渲染需求 | 靜態場景審查 | 即時動態（感測器疊加） |

---

## 4. 四大技術架構關聯

### 關聯 1：IADL 資產定義貫穿兩個階段

**PromptToBuild 階段：**
```
IADL 定義 AssetType "ASML_NXE3400"
  → ilos:category = "Equipment"
  → ilos:part_number, ilos:connections, ilos:clearance...
  → USD 幾何 + metadata
  → 放進設計場景 → Revit 施工圖 → 建造
```

**PromptToOperate 階段：**
```
同一個 IADL AssetType 被 NDH 活化為 Asset Servant
  → 綁定真實設備 (OPC UA / MQTT)
  → 接收即時感測器資料 (溫度/壓力/流量)
  → AI Agent 監控/預測
  → 維護工單自動生成
```

**核心：PromptToBuild 產出的 USD + IADL metadata，直接成為 PromptToOperate 的 Digital Twin 基礎。不需要重新建模。**

### 關聯 2：FDL 從設計語言變成營運基準

- **Build 階段:** FDL = 「設計意圖」(Design Intent) — 設備位置、管路路由、閥門配置
- **Operate 階段:** FDL = 「營運基準」(Operational Baseline)
  - 實際 vs 設計偏差監控
  - 設備移位報警
  - 管路壓力 vs 設計壓力對比
  - 變更管理 (MOC - Management of Change)

### 關聯 3：OpenUSD 作為唯一 SSOT 貫穿全生命週期

**設計階段 USD Scene = 靜態 3D 模型 + ilos: metadata**
```
/World/Equipment/ (IADL 定義的設備)
/World/Piping/    (FDL 定義的管路)
/World/Structure/ (結構)
```

**營運階段 = 同一個 USD Scene + 即時數據層**
```
/World/Equipment/ASML_001
  ├─ ilos:status = "Running"          ← NDH 即時更新
  ├─ ilos:temperature = 23.5          ← 感測器
  ├─ ilos:vibration = 0.003           ← 感測器
  ├─ ilos:maintenance_due = "2027-06" ← AI 預測
  └─ ilos:uptime_hours = 12847        ← 累積

/World/Piping/UPW_System/
  ├─ ilos:flow_rate = 48.2            ← 即時流量
  ├─ ilos:pressure = 4.8              ← 即時壓力
  └─ ilos:leak_risk = 0.02            ← AI 預測
```

### 關聯 4：Plugin 架構完全共用

兩個產品共用同一個 Plugin Bus！差別只是載入不同的 Plugin 集合：

| 介面 | PromptToBuild Plugin | PromptToOperate Plugin |
|------|---------------------|------------------------|
| IIOPlugin | io_usd, io_revit, io_ifc | io_opcua, io_mqtt, io_kafka, io_modbus |
| IEnginePlugin | engine_ilos, engine_compliance, engine_cost | engine_predictive, engine_energy_opt, engine_maintenance |
| IRenderBackend | 靜態場景審查 | 即時動態（感測器數據疊加） |
| IShellPlugin | 設計面板 | 營運 Dashboard |
| ITransport | InProcess / WebSocket | MQTT / Kafka / gRPC |

---

## 5. 統一產品矩陣

```
┌──────────────────────────────────────────────────────────────┐
│                 Reality Matrix 產品矩陣                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              IDTF v3.5+ (底層框架)                     │  │
│  │  IADL · FDL · NDH · MCP · OpenUSD · Asset Servants    │  │
│  │  (MIT License · 供應商中立 · 標準整合)                  │  │
│  └───────────────┬───────────────────┬────────────────────┘  │
│                  │                   │                        │
│  ┌───────────────▼─────────┐  ┌─────▼──────────────────┐    │
│  │   PromptToBuild         │  │   PromptToOperate      │    │
│  │   設計 → 建造 → 交付    │  │   交付 → 營運 → 維護   │    │
│  │                         │  │                        │    │
│  │  ▪ AI 建築/工廠設計     │  │  ▪ 即時監控 Dashboard  │    │
│  │  ▪ ILOS 佈局優化        │  │  ▪ 預測性維護 AI       │    │
│  │  ▪ USD↔Revit 雙向      │  │  ▪ 能源優化 AI         │    │
│  │  ▪ 施工圖/BOM/IFC      │  │  ▪ 設備資產管理        │    │
│  │  ▪ 法規合規             │  │  ▪ 維護工單/排程       │    │
│  │  ▪ 成本估算             │  │  ▪ SCADA/OPC UA 整合   │    │
│  │                         │  │  ▪ BOM/備品管理        │    │
│  │  交付物:                │  │  ▪ 碳排/ESG 追蹤       │    │
│  │  USD + IADL + FDL      │  │                        │    │
│  │   ↓↓↓ 直接成為 ↓↓↓    │  │  輸入:                 │    │
│  └─────────┬───────────────┘  │  Build 階段的 USD      │    │
│            └─────────────────→│  + IADL + FDL          │    │
│                               └────────────────────────┘    │
│                                                              │
│  共用基礎:                                                   │
│  ▪ Plugin Bus (IPlugin 6 大介面)                             │
│  ▪ USD Stage (SSOT)                                          │
│  ▪ Omniverse Nucleus (儲存 + 協作)                           │
│  ▪ Omniverse Streaming (渲染)                                │
│  ▪ ITransport (本地 or 雲端)                                 │
│  ▪ 私有 LLM (零外部 AI)                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. 第六個抽象介面：ITransport

為了支援未來全部雲端化 + PromptToOperate 的即時資料流，需要在 P26 就定義 ITransport：

```cpp
class ITransport {
public:
    // 命令（Client → Server）
    virtual Response sendCommand(const Command& cmd) = 0;
    virtual void sendCommandAsync(const Command& cmd, Callback cb) = 0;

    // 事件（Server → Client）
    virtual void subscribe(const std::string& event, EventHandler handler) = 0;
    virtual void unsubscribe(const std::string& event) = 0;

    // 串流（雙向）
    virtual StreamHandle openStream(StreamConfig cfg) = 0;
};
```

| 實作 | 用途 | 產品 |
|------|------|------|
| InProcessTransport | 本地直接呼叫 | 開發期 Build |
| WebSocketTransport | Web Client 通訊 | 雲端 Build |
| MQTTTransport | 感測器資料流 | Operate |
| KafkaTransport | 高吞吐事件流 | Operate NDH |
| gRPCTransport | 高效能 RPC | 兩者通用 |

---

## 7. 對開發路線圖的影響

| Phase | 原計劃 | 加入 IDTF 後 |
|-------|--------|-------------|
| Phase 1-3 | PromptToBuild | 不變，但 IADL/FDL 格式要確保 NDH 可消費 |
| Phase 4 | Web + Mobile | 加入 PromptToOperate Dashboard 骨架 |
| Phase 5 | 私有 LLM | 加入 predictive/optimization AI Plugin |
| **Phase 7** | 不存在 | **PromptToOperate v1.0（NDH + Asset Servants + SCADA）** |
| **Phase 8** | 不存在 | **PromptToOperate v2.0（MCP 多 Agent + 預測維護）** |

---

## 8. 最終部署形態

### 私有數據中心 On-Premise

```
┌─────────────────────────────────────────────────────┐
│           客戶私有數據中心                            │
│                                                      │
│  Omniverse Server Farm (GPU Cluster + Nucleus)      │
│  PromptToBuild Core (設計階段服務)                   │
│  PromptToOperate Core (NDH + Asset Servants)        │
│  私有 LLM Server (零外部 AI API)                    │
│  SCADA/OPC UA Gateway (連接真實設備)                │
│                                                      │
│         ↑ 內部網路 (不對外)                          │
└─────────┬───────────────────────────────────────────┘
          │ WebRTC + WebSocket (內網 or VPN)
          ▼
  使用者 Thin Client (瀏覽器 / iPad)
  零本地運算 · 零本地資料
```

---

## 9. P26 起必須確保的資料合約

> **最重要的一句話：PromptToBuild 產出的每一個 USD Prim + ilos: metadata，都要設計成 PromptToOperate 的 NDH 可以直接活化為 Asset Servant。這是從 P26 第一天就要確保的資料合約。**

具體要求：
1. 每個 IADL AssetType 的 ilos: metadata 必須包含 NDH 綁定所需的欄位
2. /Connections/ 連接點規範必須支援 OPC UA/MQTT endpoint 映射
3. USD Stage 結構必須支援即時屬性更新（不能只有靜態 metadata）
4. FDL 佈局資訊必須可作為 Operate 階段的基準比對來源

---

## 10. 版本歷程

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-03-27 | 初版 — IDTF × PromptToBuild × PromptToOperate 統一產品架構 |

---

*Reality Matrix 統一產品架構 v1.0*
*IDTF × PromptToBuild × PromptToOperate*
*Reality Matrix Inc. | 2026-03-27*
