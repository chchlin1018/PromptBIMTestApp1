# Zigma Demo-1 TSMC — Asset Manifest v1.0

> **更新:** 2026-03-28
> **下載腳本:** `scripts/download_assets.py`
> **存放:** `assets/models/`, `assets/textures/`, `assets/hdri/`

---

## 1. 施工機械 (4D Demo 必備)

| ID | 名稱 | 來源 | License | 優先 |
|----|------|------|---------|:----:|
| CE-001 | 施工機械合集(塔吊/挖土機/混凝土車/推土機/裝載機) | Sketchfab GOGA dcd9c8e | CC-BY-4.0 | 🔴 |
| CE-006 | 塔吊 HD Tower Crane | Sketchfab Chamod1999 49851dc | CC-BY-4.0 | 🟡 |
| CE-007 | 移動式吊車 Mobile Crane | Sketchfab search | CC-BY-4.0 | 🔴 |
| CE-008 | 傾卸卡車 Dump Truck | Sketchfab search | CC-BY-4.0 | 🔴 |

> **CE-001 合集包含:** Crane, Concrete Truck, Bulldozer, Roller, Fuel Tanker, Loader, Excavator 共 7+ 台 LowPoly 模型

---

## 2. 工廠/半導體設備 (TSMC 核心)

| ID | 名稱 | 來源 | License | 優先 |
|----|------|------|---------|:----:|
| IE-001 | 冰水主機 Chiller | Sketchfab chillerkirala cc833e9 | CC-BY-4.0 | 🔴 |
| IE-002 | 冷卻水塔 Cooling Tower | Sketchfab search | CC-BY-4.0 | 🔴 |
| IE-003 | 冰水系統配管 Chiller Plant | Sketchfab geppettomaster 8bf1ced | CC-BY-4.0 | 🟡 |
| IE-004 | 屋頂空調箱 AHU | Sketchfab search | CC-BY-4.0 | 🔴 |
| IE-005 | 風機盤管 FCU | BIMobject | 免費商用 | 🟡 |
| IE-006 | 變壓器 Transformer | Sketchfab search | CC-BY-4.0 | 🟡 |
| IE-007 | 發電機 Generator | Sketchfab search | CC-BY-4.0 | 🟡 |
| IE-008 | UPW 超純水系統 | parametric 自建 | — | 🔴 |
| IE-009 | 潔淨室 FFU (Fan Filter Unit) | Sketchfab search | CC-BY-4.0 | 🔴 |
| IE-010 | 廠內天車 Overhead Crane | Sketchfab search | CC-BY-4.0 | 🔴 |
| IE-011 | 配電盤 Distribution Board | BIMobject | 免費商用 | 🟡 |

---

## 3. 建築/家用設備 (別墅/辦公場景)

| ID | 名稱 | 來源 | License | 優先 |
|----|------|------|---------|:----:|
| BR-001 | 電梯 Elevator | Sketchfab | CC-BY-4.0 | 🟡 |
| BR-002 | 廚房流理臺 Kitchen Counter | Sketchfab | CC0 | 🟡 |
| BR-003 | 馬桶 Toilet | Sketchfab | CC0 | 🟡 |
| BR-004 | 洗手台 Washbasin | Sketchfab | CC0 | 🟡 |
| BR-005 | 淋浴間 Shower | Sketchfab | CC0 | 🟢 |
| BR-006 | 消防灑水頭 Sprinkler | BIMobject | 免費商用 | 🟡 |
| BR-007 | 滅火器 Fire Extinguisher | Sketchfab | CC0 | 🟡 |
| BR-008 | 嵌燈 Recessed Light | Sketchfab | CC0 | 🟢 |
| BR-009 | 泳池 Swimming Pool | Sketchfab | CC-BY-4.0 | 🟡 |
| BR-010 | 門 Door | Sketchfab | CC0 | 🟡 |
| BR-011 | 窗 Window | Sketchfab | CC0 | 🟡 |
| BR-012 | 樓梯 Staircase | Sketchfab | CC0 | 🟢 |

---

## 4. PBR 材質 (Poly Haven CC0)

| ID | 名稱 | Poly Haven slug | 解析度 | 優先 |
|----|------|----------------|:------:|:----:|
| TX-001 | 混凝土牆 Concrete Wall | concrete_wall_008 | 1K | 🔴 |
| TX-002 | 混凝土地板 Concrete Floor | concrete_floor_02 | 1K | 🔴 |
| TX-003 | 鋼材 Metal Plate | metal_plate | 1K | 🔴 |
| TX-004 | 工業金屬 Corrugated Steel | corrugated_iron | 1K | 🔴 |
| TX-005 | 玻璃 Glass Window | glass_window_002 | 1K | 🟡 |
| TX-006 | 木地板 Wood Floor | wood_floor_deck | 1K | 🟡 |
| TX-007 | 白牆 White Plaster | white_plaster | 1K | 🟡 |
| TX-008 | 磁磚 Ceramic Tiles | large_square_tiles | 1K | 🟡 |
| TX-009 | 瀝青路面 Asphalt | asphalt_04 | 1K | 🟡 |
| TX-010 | 草地 Grass | grass_path_2 | 1K | 🟢 |

---

## 5. HDRI 環境光 (Poly Haven CC0)

| ID | 名稱 | Poly Haven slug | 解析度 | 優先 |
|----|------|----------------|:------:|:----:|
| HD-001 | 工業區日落 | industrial_sunset_02_puresky | 1K | 🔴 |
| HD-002 | 晴天 | kloofendal_48d_partly_cloudy_puresky | 1K | 🔴 |
| HD-003 | 室內攝影棚 | photo_studio_loft_hall | 1K | 🟡 |

---

## 6. 場景 ↔ 資源對應

### S1 別墅場景
BR-001~BR-012, TX-006 木地板, TX-007 白牆, TX-008 磁磚, HD-002

### S2 半導體廠房場景 (TSMC 重點)
CE-001~CE-008, IE-001~IE-011, TX-001~TX-004, HD-001

### S3 數據中心場景
IE-001, IE-002, IE-006, IE-007, TX-003, TX-004, HD-001

---

## 7. 統計總覽

| 類別 | 數量 | 🔴 必備 | 🟡 建議 | 🟢 選用 |
|------|:----:|:------:|:------:|:------:|
| 施工機械 | 4 | 3 | 1 | 0 |
| 工廠設備 | 11 | 5 | 6 | 0 |
| 建築家用 | 12 | 0 | 9 | 3 |
| PBR 材質 | 10 | 4 | 4 | 2 |
| HDRI | 3 | 2 | 1 | 0 |
| **合計** | **40** | **14** | **21** | **5** |

---

## 8. License 合規

| License | 條件 | 模型數 |
|---------|------|:------:|
| CC0 (Public Domain) | 無限制 | ~20 |
| CC-BY-4.0 | 需標註原作者 | ~16 |
| BIMobject 免費 | 商業可用 | ~4 |

CC-BY 模型需在產品 About/Credits 頁面標註來源。

---

## 9. 目錄結構

```
assets/
├── ASSET_MANIFEST.md
├── LICENSES.md
├── models/
│   ├── construction/    ← CE-001~CE-008 (.glb)
│   ├── industrial/      ← IE-001~IE-011 (.glb)
│   └── building/        ← BR-001~BR-012 (.glb)
├── textures/
│   ├── concrete/        ← TX-001~TX-002
│   ├── metal/           ← TX-003~TX-004
│   ├── glass/           ← TX-005
│   ├── wood/            ← TX-006
│   ├── plaster/         ← TX-007
│   ├── tiles/           ← TX-008
│   ├── asphalt/         ← TX-009
│   └── grass/           ← TX-010
└── hdri/                ← HD-001~HD-003 (.hdr)
```

---

*Asset Manifest v1.0 | Zigma Demo-1 TSMC | 2026-03-28*
