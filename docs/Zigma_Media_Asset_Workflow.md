# Zigma — 媒體資源管理工作流 v1.0

> **日期:** 2026-03-28
> **方案:** GitHub (程式碼) + iCloud Drive (大檔案) + manifest.json (同步清單)

---

## 1. 架構

```
GitHub: PromptBIMTestApp1          iCloud Drive: ZigmaMedia/
├── zigma/ src/ tests/             ├── textures/
├── media/manifest.json ← SSOT    ├── models/construction/
├── media/.gitkeep                 ├── models/equipment/
└── .gitignore (排除大檔)           ├── scenes/
                                   ├── test_data/
    manifest.json 記錄              ├── branding/
    所有檔案清單+sha256             ├── screenshots/
    ↕ git push/pull                └── exports/
                                   ↕ iCloud 自動同步三台機器
```

## 2. 為什麼 iCloud Drive

- Mac Mini / MacBook / Windows **全自動同步**
- 右鍵 →「始終保留」= **離線存取**
- 你已有 iCloud+ (200GB/2TB)
- 不需額外 server

## 3. 三平台路徑

| 平台 | 實際路徑 | Symlink |
|------|---------|---------|
| Mac Mini | `~/Library/Mobile Documents/com~apple~CloudDocs/ZigmaMedia/` | `~/ZigmaMedia` |
| MacBook | 同上 | `~/ZigmaMedia` |
| Windows | `%USERPROFILE%\iCloudDrive\ZigmaMedia\` | `C:\ZigmaMedia` |

### 建立 symlink

**Mac:**
```bash
ln -sf ~/Library/Mobile\ Documents/com~apple~CloudDocs/ZigmaMedia ~/ZigmaMedia
```

**Windows (Admin CMD):**
```cmd
mklink /D C:\ZigmaMedia "%USERPROFILE%\iCloudDrive\ZigmaMedia"
```

## 4. 目錄結構

```
ZigmaMedia/
├── textures/                  ← PBR 紋理
│   ├── concrete_diffuse_2k.png
│   ├── glass_roughness_1k.png
│   ├── steel_metallic_1k.png
│   └── wood_diffuse_2k.png
├── models/
│   ├── construction/          ← 施工機械
│   │   ├── crane_simplified.obj
│   │   └── excavator_simplified.obj
│   └── equipment/             ← 半導體設備
│       ├── asml_euv_blackbox.usd
│       └── edwards_pump.usd
├── scenes/                    ← USD 測試場景
│   ├── ILOS_Test_Pipeline_v4.usda
│   ├── tsmc_fab_demo.usd
│   └── datacenter_demo.usd
├── test_data/                 ← 測試用 JSON
├── branding/                  ← 品牌素材
│   ├── zigma_logo.svg
│   └── splash_background.png
├── screenshots/               ← Demo 截圖
└── exports/                   ← 匯出檔案
```

## 5. manifest.json (SSOT — 在 GitHub)

```json
{
  "version": "1.0",
  "updated": "2026-03-28T02:30:00+08:00",
  "media_root": "iCloudDrive/ZigmaMedia",
  "total_files": 0,
  "total_size_mb": 0,
  "files": [
    {
      "path": "textures/concrete_diffuse_2k.png",
      "sha256": "a1b2c3...",
      "size_bytes": 4194304,
      "category": "texture",
      "description": "Concrete diffuse 2K",
      "required_by": ["BIMMaterialLibrary"],
      "status": "active"
    }
  ],
  "missing": []
}
```

## 6. 工作流程

### 新增媒體
1. 放入 `~/ZigmaMedia/textures/` → iCloud 自動同步
2. 跑 `python scripts/media_sync.py` → 更新 manifest → git push
3. 其他機器 `git pull` → 知道有新檔案

### 找不到檔案
1. `MediaManager.resolve("textures/xxx.png")` → 不存在
2. → emit `fileMissing` signal → StatusBar 顯示警告
3. → 寫入 `missing_files.log`
4. → 更新 manifest.json 的 `missing[]` → git push
5. → **App 不 crash** → graceful fallback（紋理→灰色、模型→跳過、場景→提示下載中）

### 可能原因
- iCloud 尚未同步 → 等待 / 手動觸發下載
- 檔案被刪除 → manifest sha256 可辨識
- 路徑變更 → manifest 記錄新路徑

## 7. C++ MediaManager

```cpp
class MediaManager : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString mediaPath READ mediaPath CONSTANT)
public:
    QString mediaPath() const {
        #ifdef ZIGMA_MEDIA_PATH
            return QString(ZIGMA_MEDIA_PATH);
        #elif defined(Q_OS_MAC)
            return QDir::homePath() + "/ZigmaMedia";
        #elif defined(Q_OS_WIN)
            return "C:/ZigmaMedia";
        #endif
    }

    Q_INVOKABLE QString resolve(const QString& rel) {
        QString full = mediaPath() + "/" + rel;
        if (QFile::exists(full)) return full;
        logMissing(rel);
        return "";
    }

signals:
    void fileMissing(const QString& path);

private:
    void logMissing(const QString& path) {
        emit fileMissing(path);
        QFile log(mediaPath() + "/missing_files.log");
        if (log.open(QIODevice::Append | QIODevice::Text)) {
            QTextStream(&log)
                << QDateTime::currentDateTime().toString(Qt::ISODate)
                << " MISSING: " << path << "\n";
        }
    }
};
```

## 8. CMake 整合

```cmake
# zigma/CMakeLists.txt
if(APPLE)
    set(ZIGMA_MEDIA_DEFAULT "$ENV{HOME}/ZigmaMedia")
elseif(WIN32)
    set(ZIGMA_MEDIA_DEFAULT "C:/ZigmaMedia")
endif()

set(ZIGMA_MEDIA_PATH "${ZIGMA_MEDIA_DEFAULT}" CACHE PATH "ZigmaMedia path")
target_compile_definitions(zigma PRIVATE ZIGMA_MEDIA_PATH="${ZIGMA_MEDIA_PATH}")
```

## 9. .gitignore 規則

```gitignore
# Media files (in iCloud, not GitHub)
media/**/*.png
media/**/*.jpg
media/**/*.obj
media/**/*.fbx
media/**/*.usd
media/**/*.usda
media/**/*.usdc
media/**/*.step
media/**/*.ifc
# Keep manifest
!media/manifest.json
!media/.gitkeep
```

## 10. 離線存取設定

**macOS:** Finder → 右鍵 ZigmaMedia →「下載到此 Mac」
**Windows:** 右鍵 ZigmaMedia →「始終保留在此裝置上」

## 11. 一次性設定

**Mac Mini:**
```bash
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/ZigmaMedia/{textures,models/construction,models/equipment,scenes,test_data,branding,screenshots,exports}
ln -sf ~/Library/Mobile\ Documents/com~apple~CloudDocs/ZigmaMedia ~/ZigmaMedia
```

**Windows:**
```cmd
mklink /D C:\ZigmaMedia "%USERPROFILE%\iCloudDrive\ZigmaMedia"
```

---

## 關鍵原則

- **iCloud** 負責檔案同步（大檔案）
- **GitHub** 負責清單同步（manifest.json）
- 程式碼中**永遠不硬編路徑**，用 `MediaManager.resolve()`
- 找不到檔案**不 crash**，graceful fallback + log + notify

---
*Media Asset Workflow v1.0 | 2026-03-28*
*iCloud Drive (三平台) + manifest.json (SSOT) + MediaManager (fallback)*
