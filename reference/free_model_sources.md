# 免費 3D 模型來源清單

> 系統可自動從這些來源下載免費模型
> AI Agent 在生成時會參考此清單尋找適合的模型

## BIM / 建築專用

| 來源 | 網址 | 格式 | License | 特色 |
|------|------|------|---------|------|
| **BIMobject** | bimobject.com | IFC/RFA | 免費（廠商提供）| 真實產品：電梯、門窗、衛浴 |
| **GrabCAD** | grabcad.com | STEP/OBJ | 免費 | 工程零件、HVAC 設備 |
| **3D Warehouse** | 3dwarehouse.sketchup.com | SKP | 免費 | 5.6M+ 建築模型 |
| **ARCAT BIM** | arcat.com/bim | IFC/RFA | 免費 | 美國建築構件 |
| **Modlar** | modlar.com | IFC | 免費 | BIM 構件庫 |
| **CADmapper** | cadmapper.com | DXF | 免費(1km²) | 基地環境/地形 |

## 通用 3D 模型

| 來源 | 網址 | 格式 | License | 特色 |
|------|------|------|---------|------|
| **Sketchfab** | sketchfab.com | glTF/OBJ | CC0/CC-BY | 800K+ 免費, 高品質 |
| **CGTrader** | cgtrader.com | OBJ/FBX/glTF | 免費+付費 | 150K+ 免費 |
| **Polyhaven** | polyhaven.com | glTF/HDR | CC0 | 材質/HDRI/模型, 全部 CC0 |
| **Free3D** | free3d.com | OBJ/FBX | 個人免費 | 10K+ 模型 |
| **Clara.io** | clara.io | OBJ/FBX | 多種 | 100K+ 模型 |
| **OpenGameArt** | opengameart.org | OBJ/glTF | CC0/CC-BY | 開源遊戲資產 |
| **Kenney** | kenney.nl | glTF | CC0 | 低多邊形建築模組 |

## 材質 / 貼圖

| 來源 | 網址 | 格式 | License |
|------|------|------|--------|
| **Polyhaven** | polyhaven.com | EXR/PNG | CC0 |
| **ambientCG** | ambientcg.com | PNG/JPG | CC0 |
| **3D Textures** | 3dtextures.me | PNG | CC0 |

## 使用策略

系統依以下優先順序選擇模型：
1. **參數化生成** — 牆/板/柱/梁/樓梯等規則幾何
2. **BIMobject** — 真實產品（電梯、衛浴、門窗）
3. **Sketchfab CC0** — 複雜造型（家具、設備）
4. **Polyhaven** — 材質和環境貼圖
5. **佔位幾何** — 簡化方盒（無合適模型時）

每種零件類型僅保留 1-3 個代表性模型。
下載後統一轉存為 GLB 格式。
