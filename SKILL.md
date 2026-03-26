# PromptBIMTestApp1 — SKILL.md v3.3

> Claude Code SSOT — 開發前必讀
> 最後更新: 2026-03-26

---

## 0. Sprint 執行必備：notify 函數

> ⚠️ **P22 教訓: Claude Code `-p` 模式不載入 `.zshrc`，shell 中的 `notify` 函數不存在。**
> ⚠️ **每個 Sprint PROMPT 的最前面必須包含 notify 函數定義。**
> ⚠️ **定義完 notify 後，立即發送啟動通知 — 這是 Sprint 的絕對第一個動作。**

### notify 函數（必須複製到每個 PROMPT 最前面）

```bash
notify() {
    local msg="$1"
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"chchlin1018@icloud.com\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"+886972535899\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "display notification \"$msg\" with title \"PromptBIM\"" 2>/dev/null || \
    echo "[NOTIFY FALLBACK] $msg"
}
```

### iMessage 收件人

- **主要:** `chchlin1018@icloud.com`
- **備用:** `+886972535899`

### PROMPT 創建 Checklist（MANDATORY）

```
☐ 最前面有 notify() 函數定義（含正確收件人）
☐ notify 定義後緊接啟動通知（echo + notify）
☐ 每個 Task 有 echo + notify 完成通知
☐ 每個 Part 有 echo + notify 完成通知
☐ 包含 Task 失敗通知模板
☐ 包含中斷通知模板（3 次修復失敗）
```

---

## 1. 專案核心定位

**用自然語言在一塊真實土地上蓋建築。**

使用者流程：
1. 匯入土地資料（地籍圖 PDF、Shapefile、GeoJSON、手動輸入座標）
2. 在 2D 地圖上看到土地輪廓、面積、形狀
3. 用文字或語音描述想蓋的建築
4. AI 自動在這塊地上生成 3D BIM 建築模型
5. 同時輸出 IFC（BIM 語義）+ OpenUSD（Digital Twin / IDTF）
6. 桌面 3D 互動預覽（旋轉/縮放/剖面）

**⚠️ 硬性規則：零商業軟體依賴。全部使用開源 GitHub / Library。**

---

## 2. 100% 開源技術棧

（以下內容與 v3.2 相同，省略重複...）

---

*SKILL.md v3.3 | 2026-03-26 | 新增: Section 0 — notify 函數定義 + iMessage 收件人 + PROMPT 創建 Checklist*
