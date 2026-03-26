# docs/backups/ — 關鍵文件備份參考

> ⚠️ **此資料夾用於紀錄關鍵文件的已知良好版本 SHA，以便快速恢復。**

## 受保護文件

| 文件 | 最新良好版本 | SHA | 恢復命令 |
|------|------------|-----|----------|
| `CLAUDE.md` | v1.16.0 | `b1b98603` | `git checkout e74cdc0 -- CLAUDE.md` |
| `SKILL.md` | v3.2 | `5a0c0620` | `git checkout 15fc0efe -- SKILL.md` |

## 恢復流程

```bash
# 1. 恢復 SKILL.md
git checkout 15fc0efe -- SKILL.md
wc -c SKILL.md  # 應為 27027 bytes

# 2. 恢復 CLAUDE.md
git checkout e74cdc0 -- CLAUDE.md
wc -c CLAUDE.md  # 應為 ~8450 bytes

# 3. Commit + push
git add SKILL.md CLAUDE.md
git commit -m "fix: restore critical files from backup"
git push origin main
```

## 歷史事件

| 日期 | 事件 | 影響 | 恢復方式 |
|------|------|------|----------|
| P18 | Claude Code 修改 CLAUDE.md | 18KB → 1.7KB | 人工重建 v1.14.1 |
| P22 prep | GitHub API push 截斷 SKILL.md | 27KB → 2.5KB | `git checkout 15fc0efe -- SKILL.md` |

## 規則

- Claude Code **絕對禁止**修改 CLAUDE.md / SKILL.md / 本資料夾
- 每次人工更新 CLAUDE.md 或 SKILL.md 後，更新本 README 的 SHA 和版本
- 如發現文件大小異常（< 50% 原始大小），立即從備份 SHA 恢復
