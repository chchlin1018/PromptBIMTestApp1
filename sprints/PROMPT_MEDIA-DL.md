# PROMPT_MEDIA-DL.md — Zigma 媒體資源下載 Sprint

> **Sprint:** MEDIA-DL | **環境:** Mac Mini M4 | macOS
> **目的:** 下載全部 40 項 Demo 必要媒體資源到 iCloud ZigmaMedia/
> **前置:** iCloud Drive 已啟用, ~/ZigmaMedia symlink 已建立
> **Tasks:** 12 | **預估:** 30-60 分鐘

---

## ★★★ 函數定義（同 M1-MVP）★★★

（複製 PROMPT_M1-MVP.md 的全部函數定義）

```bash
SPRINT="MEDIA-DL"
SPRINT_DESC="Zigma 媒體資源下載 — 40 項 Demo 素材到 iCloud ZigmaMedia/"
VERSION="media-v1.0"
TASK_TOTAL=12
TASK_DONE=0
PART_TOTAL=3
PART_DONE=0
PCT=0
```

---

## Part A: 環境準備 + iCloud 目錄 (3T)

```bash
part_start "A" "環境準備 + iCloud 目錄" 3
```

### Task 1: 建立 iCloud ZigmaMedia 目錄結構

```bash
task_start 1 "建立 iCloud ZigmaMedia 目錄結構"
```

```bash
# 建立完整目錄結構（iCloud Drive）
MEDIA_ROOT=~/Library/Mobile\ Documents/com~apple~CloudDocs/ZigmaMedia

mkdir -p "$MEDIA_ROOT"/{textures,models/construction,models/industrial,models/building,scenes,test_data,branding,screenshots,exports,hdri}

# 建立 symlink（如果還沒有）
[ ! -L ~/ZigmaMedia ] && ln -sf ~/Library/Mobile\ Documents/com~apple~CloudDocs/ZigmaMedia ~/ZigmaMedia

# 驗證
ls -la ~/ZigmaMedia/
notify "✅ ZigmaMedia 目錄結構建立完成: $(ls ~/ZigmaMedia/ | wc -l) 子目錄"
```

驗收: `~/ZigmaMedia/` 存在且有 10 個子目錄

```bash
task_done
```

### Task 2: 修改 download_assets.py 下載到 iCloud

```bash
task_start 2 "修改 download_assets.py → iCloud ZigmaMedia"
```

修改 `scripts/download_assets.py`:
- `--output-dir` 預設值從 `assets` 改為 `$HOME/ZigmaMedia`
- 或新增參數 `--icloud` 自動選擇 iCloud 路徑
- 同時保留 `assets/` 作為 fallback

```python
# 路徑選擇邏輯
if args.icloud or args.output_dir == "auto":
    if sys.platform == 'darwin':
        base = Path.home() / "ZigmaMedia"
    elif sys.platform == 'win32':
        base = Path(os.environ.get('USERPROFILE', '')) / "iCloudDrive" / "ZigmaMedia"
else:
    base = Path(args.output_dir)
```

驗收: `python scripts/download_assets.py --icloud --dry-run` 顯示目標路徑為 ~/ZigmaMedia/

```bash
task_done
```

### Task 3: 確認網路連線 + Poly Haven API

```bash
task_start 3 "確認網路連線 + Poly Haven API 可用"
```

```bash
# 測試 Poly Haven API
curl -s "https://api.polyhaven.com/files/concrete_wall_008" | head -c 200
echo ""
# 測試下載速度
curl -o /dev/null -s -w "%{speed_download}" "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/concrete_wall_008/concrete_wall_008_diff_1k.jpg"
notify "✅ Poly Haven API 可用, 下載速度正常"
```

驗收: API 回應正常

```bash
task_done
part_done "Part B: 自動下載"
```

---

## Part B: 自動下載 Poly Haven (5T)

```bash
part_start "B" "自動下載 Poly Haven CC0 素材" 5
```

### Task 4: 下載 🔴 必備 PBR 紋理 (4 套)

```bash
task_start 4 "下載 🔴 必備 PBR 紋理: concrete_wall + concrete_floor + metal_plate + corrugated_iron"
```

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda run -n promptbim python scripts/download_assets.py --priority red --output-dir ~/ZigmaMedia --category textures
notify "✅ 🔴 PBR 紋理下載完成: $(ls ~/ZigmaMedia/textures/ | wc -l) 檔案"
```

驗收: ~/ZigmaMedia/textures/ 至少 4 套紋理目錄

```bash
task_done
```

### Task 5: 下載 🔴 必備 HDRI (2 個)

```bash
task_start 5 "下載 🔴 必備 HDRI: industrial_sunset + partly_cloudy"
```

```bash
conda run -n promptbim python scripts/download_assets.py --priority red --output-dir ~/ZigmaMedia --category hdri
notify "✅ 🔴 HDRI 下載完成: $(ls ~/ZigmaMedia/hdri/ | wc -l) 檔案"
```

驗收: ~/ZigmaMedia/hdri/ 有 .hdr 檔案

```bash
task_done
```

### Task 6: 下載 🟡 選用 PBR + HDRI

```bash
task_start 6 "下載 🟡 選用 PBR: glass + wood + plaster + tiles + asphalt + studio HDRI"
```

```bash
conda run -n promptbim python scripts/download_assets.py --priority all --output-dir ~/ZigmaMedia
notify "✅ 全部 Poly Haven 下載完成: textures=$(ls ~/ZigmaMedia/textures/ | wc -l) hdri=$(ls ~/ZigmaMedia/hdri/ | wc -l)"
```

驗收: 10 套紋理 + 3 個 HDRI

```bash
task_done
```

### Task 7: 建立品牌素材 (SVG/PNG)

```bash
task_start 7 "建立 Zigma 品牌素材: logo + splash"
```

用 Python 或手動建立:
- `~/ZigmaMedia/branding/zigma_logo.svg` — Zigma 文字 logo
- `~/ZigmaMedia/branding/zigma_logo_dark.svg` — 深色版
- `~/ZigmaMedia/branding/zigma_icon_512.png` — App 圖示
- `~/ZigmaMedia/branding/splash_background.png` — Splash 背景

可以用簡單的 SVG 模板：

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100">
  <text x="200" y="65" text-anchor="middle" font-family="Helvetica,sans-serif"
        font-size="48" font-weight="700" fill="#2563eb">Zigma</text>
  <text x="200" y="90" text-anchor="middle" font-family="Helvetica,sans-serif"
        font-size="14" fill="#64748b">PromptToBuild</text>
</svg>
```

驗收: ~/ZigmaMedia/branding/ 有 logo SVG

```bash
task_done
```

### Task 8: 列出 Sketchfab 手動下載清單

```bash
task_start 8 "列出 Sketchfab 手動下載清單 + 紀錄 URL"
```

```bash
conda run -n promptbim python scripts/download_assets.py --priority all --output-dir ~/ZigmaMedia --dry-run 2>&1 | tee /tmp/sketchfab_manual_list.txt
notify "📋 Sketchfab 手動下載清單已產出: /tmp/sketchfab_manual_list.txt
🔴 必備: crane, excavator, chiller, cooling tower, AHU, FFU, overhead crane
🟡 選用: transformer, generator, elevator, toilet, door, window"
```

驗收: 清單檔案存在

```bash
task_done
part_done "Part C: manifest 同步 + 驗證"
```

---

## Part C: manifest 同步 + 驗證 (4T)

```bash
part_start "C" "manifest 同步 + 驗證" 4
```

### Task 9: 執行 media_sync.py 更新 manifest

```bash
task_start 9 "執行 media_sync.py → 更新 media/manifest.json"
```

```bash
conda run -n promptbim python scripts/media_sync.py
notify "✅ manifest.json 已更新: $(cat media/manifest.json | python3 -c 'import sys,json;d=json.load(sys.stdin);print(f\"{d[\"total_files\"]} files, {d[\"total_size_mb\"]}MB\")')"
```

驗收: media/manifest.json 更新且有 total_files > 0

```bash
task_done
```

### Task 10: 驗證 iCloud 同步

```bash
task_start 10 "驗證 iCloud 同步狀態"
```

```bash
# 列出所有檔案
echo "=== ZigmaMedia 檔案清單 ==="
find ~/ZigmaMedia -type f -not -name ".*" | sort
echo ""
echo "=== 統計 ==="
echo "總檔案數: $(find ~/ZigmaMedia -type f -not -name ".*" | wc -l)"
echo "總大小: $(du -sh ~/ZigmaMedia | cut -f1)"
echo ""
echo "=== 各目錄 ==="
for d in textures models hdri branding; do
    echo "$d: $(find ~/ZigmaMedia/$d -type f 2>/dev/null | wc -l) files"
done
notify "📊 ZigmaMedia 統計: $(find ~/ZigmaMedia -type f -not -name '.*' | wc -l) files, $(du -sh ~/ZigmaMedia | cut -f1)"
```

驗收: 至少 20+ 檔案存在

```bash
task_done
```

### Task 11: 統一 ASSET_MANIFEST + manifest.json

```bash
task_start 11 "統一 assets/ASSET_MANIFEST.md 和 media/manifest.json"
```

- 在 `assets/ASSET_MANIFEST.md` 頂部加入說明:
  > 實際檔案存放在 iCloud Drive ~/ZigmaMedia/，不在 GitHub。
  > 自動同步清單: media/manifest.json (SSOT)
- 確保 `media/manifest.json` 的 files[] 和 ASSET_MANIFEST.md 一致
- 更新 `.gitignore` 排除大型媒體檔案

驗收: 兩份文件指向同一來源

```bash
task_done
```

### Task 12: git push 最終結果

```bash
task_start 12 "git commit + push 全部變更"
```

```bash
git add -A
git commit -m "[media] Download assets to iCloud ZigmaMedia + sync manifest"
git push origin main
notify "🏗️ MEDIA-DL Sprint 完成 🎉
📦 Poly Haven 自動下載: textures + HDRI
📋 Sketchfab 手動清單已產出
📊 manifest.json 已同步
💡 剩餘: Sketchfab GLB 需手動下載"
```

```bash
task_done
part_done "Sprint 完成"
```

---

## Sprint 後手動做

1. 📱 在 MacBook/Windows 確認 iCloud 已同步 ZigmaMedia/
2. 🔴 手動下載 Sketchfab GLB (需登入):
   - CE-001: Construction Equipment Pack
   - CE-007: Mobile Crane
   - CE-008: Dump Truck
   - IE-001: Air-Cooled Chiller
   - IE-002: Cooling Tower
   - IE-004: Rooftop AHU
   - IE-009: Cleanroom FFU
   - IE-010: Overhead Crane
3. 下載後放到 `~/ZigmaMedia/models/` 對應子目錄
4. 再跑一次 `python scripts/media_sync.py`

---

*PROMPT_MEDIA-DL.md | 12T/3Parts | iCloud ZigmaMedia | 2026-03-28*
