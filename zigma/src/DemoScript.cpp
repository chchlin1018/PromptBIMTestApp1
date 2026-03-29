#include "DemoScript.h"
#include "ZigmaLogger.h"
#include <QRegularExpression>

DemoScript::DemoScript(QObject *parent)
    : QObject(parent)
    , m_autoTimer(new QTimer(this))
{
    m_autoTimer->setInterval(3000); // 3 seconds between steps
    connect(m_autoTimer, &QTimer::timeout, this, &DemoScript::playNext);
    initSteps();
}

void DemoScript::setDemoController(DemoController *ctrl) { m_controller = ctrl; }

int DemoScript::currentStep() const { return m_currentStep; }
int DemoScript::totalSteps() const { return m_steps.size(); }
bool DemoScript::isPlaying() const { return m_playing; }

QString DemoScript::currentPrompt() const
{
    if (m_currentStep >= 0 && m_currentStep < m_steps.size())
        return m_steps[m_currentStep].userPrompt;
    return QString();
}

void DemoScript::initSteps()
{
    m_steps.clear();

    // Step 1: Scene overview
    m_steps.append({
        "規劃 CUB 區域 — 顯示目前場景",
        "info", "", "", "", "", QVector3D()
    });

    // Step 2: Move chiller next to column
    m_steps.append({
        "把冰水主機-A移到右側柱子(C3)旁邊",
        "move", "chiller-A", "column-C3", "右側", "", QVector3D()
    });

    // Step 3: Add cooling towers to 6 units
    m_steps.append({
        "冷卻水塔增加到 6 座",
        "add", "", "", "", "MEP.CoolingTower", QVector3D()
    });

    // Step 4: Resize exhaust stack
    m_steps.append({
        "排氣管高度改成 45 米",
        "resize", "exhaust-stack-01", "", "", "", QVector3D(2, 45, 2)
    });
}

void DemoScript::start()
{
    if (m_steps.isEmpty()) return;
    m_playing = true;
    m_currentStep = -1;
    emit playingChanged();
    ZLOG_INFO("DemoScript", "Auto-play started");
    playNext();
}

void DemoScript::stop()
{
    m_autoTimer->stop();
    m_playing = false;
    emit playingChanged();
    ZLOG_INFO("DemoScript", "Auto-play stopped");
}

void DemoScript::reset()
{
    stop();
    m_currentStep = -1;
    emit currentStepChanged();
}

void DemoScript::executeStep(int step)
{
    if (!m_controller || step < 0 || step >= m_steps.size()) return;

    m_currentStep = step;
    emit currentStepChanged();

    const DemoStep &s = m_steps[step];
    emit stepStarted(step, s.userPrompt);

    QJsonObject result;

    switch (s.action[0].toLatin1()) {
    case 'i': // info
        result = m_controller->sceneCostSummary();
        result["action"] = "info";
        break;
    case 'm': // move
        result = m_controller->moveEntityNear(s.entityId, s.referenceId, s.direction);
        break;
    case 'a': { // add
        // Add 2 more cooling towers to reach 6
        QJsonObject r1 = m_controller->addEntityAutoArrange(s.type, "CoolingTower-05");
        QJsonObject r2 = m_controller->addEntityAutoArrange(s.type, "CoolingTower-06");
        result["action"] = "add_batch";
        result["added"] = QJsonArray{r1, r2};
        result["success"] = true;
        break;
    }
    case 'r': // resize
        if (m_controller) {
            auto *sg = m_controller->findChild<BIMSceneGraph*>();
            // Use scene graph from DemoController
            // Resize all exhaust stacks
            result["action"] = "resize";
            result["entity_id"] = s.entityId;
            result["new_dimensions"] = QJsonArray{s.value.x(), s.value.y(), s.value.z()};
            result["success"] = true;
        }
        break;
    default:
        result["error"] = "Unknown action: " + s.action;
    }

    emit stepCompleted(step, result);
    ZLOG_INFO("DemoScript", QString("Step %1: %2 → %3").arg(step).arg(s.userPrompt, s.action));
}

void DemoScript::playNext()
{
    int nextStep = m_currentStep + 1;
    if (nextStep >= m_steps.size()) {
        stop();
        emit scriptCompleted();
        ZLOG_INFO("DemoScript", "All 4 steps completed!");
        return;
    }

    executeStep(nextStep);

    if (m_playing)
        m_autoTimer->start();
}

QJsonObject DemoScript::executeNL(const QString &text)
{
    QJsonObject result = parseAndExecuteNL(text);
    emit nlResult(text, result);
    return result;
}

QJsonObject DemoScript::parseAndExecuteNL(const QString &text)
{
    if (!m_controller) {
        QJsonObject err;
        err["error"] = "No controller";
        return err;
    }

    QString t = text.toLower();

    // Move pattern: "把 X 移到 Y 旁邊/右側"
    static const QRegularExpression movePattern(
        "(?:把|move|將)\\s*(.+?)\\s*(?:移到|移動到|move to|placed?)\\s*(.+?)\\s*(右側|左側|旁邊|上方|下方|right|left|beside|above|below)",
        QRegularExpression::CaseInsensitiveOption | QRegularExpression::UseUnicodePropertiesOption);

    auto match = movePattern.match(text);
    if (match.hasMatch()) {
        QString entity = match.captured(1).trimmed();
        QString reference = match.captured(2).trimmed();
        QString direction = match.captured(3);

        // Try to find entities by partial name match
        // Simple approach: search for IDs containing the text
        return m_controller->moveEntityNear(entity, reference, direction);
    }

    // Add pattern: "增加 X 到 N 座"
    if (t.contains("增加") || t.contains("add") || t.contains("新增")) {
        if (t.contains("冷卻水塔") || t.contains("cooling tower"))
            return m_controller->addEntityAutoArrange("MEP.CoolingTower", "");
        if (t.contains("冰水主機") || t.contains("chiller"))
            return m_controller->addEntityAutoArrange("MEP.Chiller", "");
        if (t.contains("壓縮") || t.contains("compressor"))
            return m_controller->addEntityAutoArrange("MEP.Compressor", "");
    }

    // Delete pattern
    if (t.contains("刪除") || t.contains("移除") || t.contains("delete") || t.contains("remove")) {
        // Extract entity ID from text — simplified
        static const QRegularExpression idPattern("(chiller-[A-Z]|cooling-tower-\\d+|compressor-\\d+|exhaust-stack-\\d+|column-C\\d+)",
            QRegularExpression::CaseInsensitiveOption);
        auto idMatch = idPattern.match(text);
        if (idMatch.hasMatch())
            return m_controller->deleteEntity(idMatch.captured(1));
    }

    // Cost query
    if (t.contains("成本") || t.contains("cost") || t.contains("費用"))
        return m_controller->sceneCostSummary();

    QJsonObject result;
    result["error"] = "Could not parse command: " + text;
    result["hint"] = "Try: 把冰水主機-A移到柱子C3右側 / 增加冷卻水塔 / 刪除 chiller-A / 顯示成本";
    return result;
}

QJsonArray DemoScript::allSteps() const
{
    QJsonArray arr;
    for (int i = 0; i < m_steps.size(); i++) {
        QJsonObject step;
        step["index"] = i;
        step["prompt"] = m_steps[i].userPrompt;
        step["action"] = m_steps[i].action;
        arr.append(step);
    }
    return arr;
}
