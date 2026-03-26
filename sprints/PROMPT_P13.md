# PROMPT_P13.md — Sprint P13: CLI 完整化 + 依賴修復 + PDF OCR

> 版本: v1.0.0 | 建立時間: 2026-03-26
> 前置 Sprint: P12 完成（品質修復 + 效能優化）
> 依賴: P4 (Agent Pipeline), P9 (AI 辨識), P12 (品質修復)
> 品質分析: docs/reports/Full_Codebase_Quality_Report.md

## Sprint 目標

1. **修復 Critical 依賴問題** — pyproject.toml 版本、缺失套件、optional-deps 不符
2. **實作 `generate` CLI 命令** — 讓命令列可直接生成建築（目前是空殼）
3. **新增 PDF OCR 土地匯入** — 解析 PDF 地籍圖提取土地邊界
4. **測試基礎設施改進** — conftest.py 共用 fixtures + pytest markers

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. CLAUDE.md
3. docs/reports/Full_Codebase_Quality_Report.md（⚠️ 必讀，C1-C4 修復項目來自此報告）
4. `pyproject.toml`
5. `src/promptbim/__main__.py`
6. `src/promptbim/agents/orchestrator.py`
7. `src/promptbim/config.py`

---

## Part A: Critical 依賴修復

### Task 1: 修復 pyproject.toml

- ⬜ 更新 `version` 從 `"0.1.0"` 到正確版本（與 CHANGELOG 一致）
- ⬜ 加入缺失的核心依賴：
  ```toml
  "pydantic-settings>=2.0",  # config.py 需要
  "imageio>=2.30",           # simulation/animator.py GIF 匯出需要
  ```
- ⬜ 修正 `[project.optional-dependencies]`：
  ```toml
  web = ["streamlit>=1.30"]                        # 原本錯誤寫 fastapi
  voice = ["faster-whisper>=1.0", "sounddevice>=0.4"]  # 加入 sounddevice
  pdf = ["pdfplumber>=0.10", "PyMuPDF>=1.23"]      # 加入 PyMuPDF
  ```
- ⬜ 移除未使用的依賴：
  - `rich>=13.0`（整個專案未 import rich）
- ⬜ 移除 `f3d_path` 從 `config.py` Settings（從未使用）
- ⬜ 驗證 `pip install -e .` 在乾淨 conda env 中成功

### Task 2: `__init__.py` version 同步

- ⬜ 確認 `src/promptbim/__init__.py` 中 `__version__` 與 `pyproject.toml` 一致
- ⬜ 考慮使用 `importlib.metadata` 動態讀取版本：
  ```python
  try:
      from importlib.metadata import version
      __version__ = version("promptbim")
  except Exception:
      __version__ = "1.5.0"  # fallback
  ```

---

## Part B: 實作 `generate` CLI 命令

### Task 3: 實作 `_run_generate()`

- ⬜ 在 `__main__.py` 中實作 `_run_generate(args)` 函式
  ```python
  def _run_generate(args):
      from promptbim.agents.orchestrator import Orchestrator
      from promptbim.schemas.zoning import ZoningRules
      from promptbim.config import get_settings
      from pathlib import Path
      import json
      
      output_dir = Path(args.output)
      output_dir.mkdir(parents=True, exist_ok=True)
      
      # 載入土地（如果提供）
      land = None
      if args.land:
          land = _load_land_file(args.land)
      else:
          # 預設 30x30 地塊
          from promptbim.schemas.land import LandParcel
          land = LandParcel(
              name="CLI-Default",
              boundary=[(0,0),(30,0),(30,30),(0,30)],
              area_sqm=900.0,
          )
      
      zoning = ZoningRules()
      orch = Orchestrator(output_dir=output_dir, on_status=_cli_status)
      result = orch.generate(args.prompt, land, zoning)
      
      # 輸出結果
      if result.success:
          print(f"✅ Generated: {result.building_name}")
          print(f"   IFC: {result.ifc_path}")
          print(f"   USD: {result.usd_path}")
          print(f"   Stories: {result.summary.get('stories', '?')}")
          # 儲存 JSON 摘要
          summary_path = output_dir / "result.json"
          summary_path.write_text(json.dumps(result.model_dump(mode='json', exclude={'ifc_path','usd_path'}), indent=2, ensure_ascii=False, default=str))
          print(f"   Summary: {summary_path}")
      else:
          print(f"❌ Generation failed: {result.errors}")
          sys.exit(1)
  ```
- ⬜ 實作 `_load_land_file(path)` 支援 GeoJSON/SHP/DXF/KML 自動偵測
- ⬜ 實作 `_cli_status(status)` 顯示進度
- ⬜ 加入 `--format` 選項：`ifc`, `usd`, `both`（預設 both）
- ⬜ 加入 `--city` 選項：指定城市查詢法規（預設 Taipei）
- ⬜ 加入 `--template` 選項：使用建築模板（residential/school/hospital/factory）

### Task 4: CLI 整合測試

- ⬜ 建立 `tests/test_cli.py`
  ```python
  def test_version_output():
      result = subprocess.run(["python", "-m", "promptbim", "--version"], capture_output=True)
      assert "promptbim" in result.stdout.decode()
  
  def test_generate_no_land():
      result = subprocess.run(
          ["python", "-m", "promptbim", "generate", "3-story villa", "-o", tmpdir],
          capture_output=True,
      )
      assert result.returncode == 0
      assert (tmpdir / "result.json").exists()
  
  def test_generate_with_geojson():
      ...
  
  def test_check_json_output():
      ...
  ```

---

## Part C: PDF OCR 土地匯入

### Task 5: PDF 地籍圖解析器

- ⬜ 建立 `src/promptbim/land/parsers/pdf_ocr.py`
  ```python
  class PDFLandParser:
      """Parse cadastral PDF documents to extract land boundaries."""
      
      def parse(self, pdf_path: str | Path) -> list[LandParcel]:
          """Extract land parcels from a PDF cadastral document.
          
          Strategy:
          1. Extract text tables (pdfplumber) for area/address data
          2. Extract images/diagrams for boundary shapes
          3. If boundary detected, use Claude Vision for AI recognition
          4. Combine text + boundary data into LandParcel
          """
  ```
- ⬜ 整合 pdfplumber 表格提取 + PyMuPDF 圖像提取
- ⬜ 結合 LandReaderAgent（Claude Vision）辨識圖形邊界
- ⬜ 建立 `tests/test_land/test_pdf_ocr.py`
  - Mock Claude Vision API
  - 使用 fixture PDF 測試表格提取

### Task 6: GUI 整合 PDF 匯入

- ⬜ 在 `gui/dialogs/import_land.py` 加入 PDF Tab
  - 支援 .pdf 拖放
  - 自動偵測是否包含地籍圖（關鍵字：地號、面積、坐標）
  - 顯示提取結果供用戶確認
- ⬜ 更新 `Info.plist` 加入 PDF 支援：
  ```xml
  <dict>
      <key>CFBundleTypeName</key>
      <string>PDF Document</string>
      <key>CFBundleTypeExtensions</key>
      <array><string>pdf</string></array>
      <key>CFBundleTypeRole</key>
      <string>Viewer</string>
  </dict>
  ```

---

## Part D: 測試基礎設施

### Task 7: 共用 Fixtures + Markers

- ⬜ 建立 `tests/conftest.py` 統一 fixtures
  ```python
  import pytest
  from promptbim.schemas.land import LandParcel
  from promptbim.schemas.plan import BuildingPlan
  
  @pytest.fixture
  def sample_land():
      return LandParcel(name="Test", boundary=[(0,0),(30,0),(30,30),(0,30)], area_sqm=900.0)
  
  @pytest.fixture
  def sample_plan():
      # ... 完整 3-story plan fixture
  
  @pytest.fixture
  def tmp_output(tmp_path):
      return tmp_path / "output"
  ```
- ⬜ 在 `pyproject.toml` 加入 pytest markers：
  ```toml
  [tool.pytest.ini_options]
  markers = [
      "integration: requires real environment",
      "api: requires Claude API key",
      "benchmark: performance benchmarks",
      "slow: tests taking > 10 seconds",
  ]
  ```
- ⬜ 重構 `test_e2e_integration.py` 使用共用 fixtures

### Task 8: 統一重複函式

- ⬜ 將 `orchestrator.py` 的 `_poly_area()` 移至 `bim/geometry.py` 並統一引用
- ⬜ 確認專案中無其他重複的 shoelace 實作

---

## Part E: 收尾

### Task 9: Orchestrator 改進

- ⬜ 加入部分結果恢復：Builder 失敗時保存 Plan 到 JSON
  ```python
  except Exception as e:
      logger.error("Builder failed: %s", e)
      # Save partial result
      plan_json = output_dir / "plan_partial.json"
      plan_json.write_text(self.plan.model_dump_json(indent=2))
      return GenerationResult(success=False, errors=[str(e)], ...)
  ```
- ⬜ Orchestrator.modify() 在 API 失敗時嘗試 keyword fallback

### Task 10: 測試 + 收尾

- ⬜ 所有新增功能測試通過
- ⬜ `python -m promptbim generate "3-story villa" -o ./output` 正常執行
- ⬜ `python -m promptbim --version` 顯示正確版本
- ⬜ `pip install -e .` 在乾淨 env 成功
- ⬜ xcodebuild BUILD SUCCEEDED
- ⬜ pytest 全部通過
- ⬜ 更新 CHANGELOG / TODO / Context Prompt
- ⬜ git tag v1.5.0
- ⬜ iMessage 通知已發送

---

## 驗收標準

1. **`generate` CLI 可用** — `python -m promptbim generate "villa" -o ./out` 輸出 IFC + USD
2. **版本一致** — pyproject.toml / __init__.py / --version 全部一致
3. **依賴正確** — 乾淨 conda env `pip install -e .` 成功
4. **PDF OCR** — PDF 地籍圖可提取土地資料（至少文字部分）
5. **共用 Fixtures** — conftest.py 定義，E2E 測試使用
6. **所有測試通過** + xcodebuild BUILD SUCCEEDED

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
**執行順序: Part A (T1-2) → Part B (T3-4) → Part C (T5-6) → Part D (T7-8) → Part E (T9-10)**
使用 P10.2 的 debug.py logger，不要用 print()。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
