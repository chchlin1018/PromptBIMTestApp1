#include "AgentBridge.h"
#include "BIMSceneGraph.h"
#include "BIMEntity.h"
#include "ZigmaLogger.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QCoreApplication>
#include <QDir>
#include <QDebug>

AgentBridge::AgentBridge(QObject *parent)
    : QObject(parent)
{
    m_heartbeat = new QTimer(this);
    m_heartbeat->setInterval(120000); // 120s timeout
    connect(m_heartbeat, &QTimer::timeout, this, &AgentBridge::onHeartbeatTimeout);

    // Find agent_runner.py relative to the app
    QDir appDir(QCoreApplication::applicationDirPath());
    appDir.cdUp(); appDir.cdUp(); // zigma/build -> project root
    m_pythonRunner = appDir.filePath("agent_runner.py");
}

AgentBridge::~AgentBridge()
{
    stopPython();
}

bool AgentBridge::isConnected() const { return m_connected; }
bool AgentBridge::isBusy() const { return m_busy; }
bool AgentBridge::isReconnecting() const { return m_reconnecting; }

void AgentBridge::startPython()
{
    if (m_process && m_process->state() != QProcess::NotRunning) return;

    m_process = new QProcess(this);
    connect(m_process, &QProcess::readyReadStandardOutput, this, &AgentBridge::onReadyRead);
    connect(m_process, &QProcess::readyReadStandardError, this, &AgentBridge::onReadyReadStderr);
    connect(m_process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &AgentBridge::onProcessFinished);

    // Use conda run -n promptbim python agent_runner.py
    m_process->setProgram("conda");
    m_process->setArguments({"run", "-n", "promptbim", "--no-banner", "python", m_pythonRunner});

    // Pass env vars
    QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
    env.insert("PYTHONUNBUFFERED", "1");
    m_process->setProcessEnvironment(env);

    m_process->start();
    if (m_process->waitForStarted(5000)) {
        m_connected = true;
        emit connectedChanged();
        if (m_reconnecting) {
            m_reconnecting = false;
            emit reconnectingChanged();
            emit statusUpdate("AI reconnected", 0.0);
        }
        m_restartCount = 0;
        m_heartbeat->start();
        qDebug() << "AgentBridge: Python started";
    } else {
        emit errorOccurred("Failed to start Python agent: " + m_process->errorString());
    }
}

void AgentBridge::stopPython()
{
    m_heartbeat->stop();
    if (m_process) {
        m_process->terminate();
        if (!m_process->waitForFinished(3000))
            m_process->kill();
        m_process->deleteLater();
        m_process = nullptr;
    }
    if (m_connected) {
        m_connected = false;
        emit connectedChanged();
    }
}

void AgentBridge::generate(const QString &prompt, const QJsonObject &landData)
{
    QJsonObject req;
    req["type"] = "generate";
    req["prompt"] = prompt;
    req["land"] = landData;
    sendRequest(req);
}

void AgentBridge::modify(const QString &intent)
{
    QJsonObject req;
    req["type"] = "modify";
    req["intent"] = intent;
    sendRequest(req);
}

void AgentBridge::getCost()
{
    QJsonObject req;
    req["type"] = "get_cost";
    sendRequest(req);
}

void AgentBridge::getSchedule()
{
    QJsonObject req;
    req["type"] = "get_schedule";
    sendRequest(req);
}

void AgentBridge::setSceneGraph(BIMSceneGraph *sg)
{
    m_sceneGraph = sg;
}

// --- Scene Query actions (M2-BRIDGE) ---

void AgentBridge::queryByType(const QString &type)
{
    QJsonObject req;
    req["action"] = "query";
    req["type"] = type;
    handleSceneAction(req);
}

void AgentBridge::queryByName(const QString &name)
{
    QJsonObject req;
    req["action"] = "query";
    req["name"] = name;
    handleSceneAction(req);
}

void AgentBridge::getPosition(const QString &id)
{
    QJsonObject req;
    req["action"] = "get_position";
    req["id"] = id;
    handleSceneAction(req);
}

void AgentBridge::getNearby(const QString &id, double radius)
{
    QJsonObject req;
    req["action"] = "nearby";
    req["id"] = id;
    req["radius"] = radius;
    handleSceneAction(req);
}

void AgentBridge::getSceneInfo()
{
    QJsonObject req;
    req["action"] = "scene_info";
    handleSceneAction(req);
}

// --- Scene Operate actions (M2-BRIDGE) ---

void AgentBridge::moveEntity(const QString &id, const QVector3D &position)
{
    QJsonObject req;
    req["action"] = "move";
    req["id"] = id;
    req["position"] = QJsonArray{position.x(), position.y(), position.z()};
    handleSceneAction(req);
}

void AgentBridge::rotateEntity(const QString &id, const QVector3D &rotation)
{
    QJsonObject req;
    req["action"] = "rotate";
    req["id"] = id;
    req["rotation"] = QJsonArray{rotation.x(), rotation.y(), rotation.z()};
    handleSceneAction(req);
}

void AgentBridge::resizeEntity(const QString &id, const QVector3D &dimensions)
{
    QJsonObject req;
    req["action"] = "resize";
    req["id"] = id;
    req["dimensions"] = QJsonArray{dimensions.x(), dimensions.y(), dimensions.z()};
    handleSceneAction(req);
}

void AgentBridge::addEntity(const QString &type, const QVector3D &position, const QJsonObject &properties)
{
    QJsonObject req;
    req["action"] = "add";
    req["type"] = type;
    req["position"] = QJsonArray{position.x(), position.y(), position.z()};
    req["properties"] = properties;
    handleSceneAction(req);
}

void AgentBridge::deleteEntity(const QString &id)
{
    QJsonObject req;
    req["action"] = "delete";
    req["id"] = id;
    handleSceneAction(req);
}

void AgentBridge::connectEntities(const QString &fromId, const QString &toId)
{
    QJsonObject req;
    req["action"] = "connect";
    req["from"] = fromId;
    req["to"] = toId;
    handleSceneAction(req);
}

void AgentBridge::getCostDelta()
{
    QJsonObject req;
    req["action"] = "cost_delta";
    // Forward to Python for IDTF cost_delta.py
    req["type"] = "scene_action";
    sendRequest(req);
}

void AgentBridge::getScheduleImpact()
{
    QJsonObject req;
    req["action"] = "schedule_impact";
    req["type"] = "scene_action";
    sendRequest(req);
}

void AgentBridge::handleSceneAction(const QJsonObject &request)
{
    if (!m_sceneGraph) {
        emit errorOccurred("SceneGraph not available");
        return;
    }

    QString action = request["action"].toString();
    QJsonObject result;
    result["action"] = action;
    result["success"] = true;

    if (action == "query") {
        if (request.contains("type") && !request["type"].toString().isEmpty()) {
            QVariantList list = m_sceneGraph->queryByType(request["type"].toString());
            QJsonArray arr;
            for (const auto &v : list) arr.append(v.toJsonValue());
            result["entities"] = arr;
            result["count"] = arr.size();
        } else if (request.contains("name")) {
            QVariantList list = m_sceneGraph->queryByName(request["name"].toString());
            QJsonArray arr;
            for (const auto &v : list) arr.append(v.toJsonValue());
            result["entities"] = arr;
            result["count"] = arr.size();
        }
    } else if (action == "get_position") {
        BIMEntity *e = m_sceneGraph->findEntity(request["id"].toString());
        if (e) {
            result["id"] = e->entityId();
            result["position"] = QJsonArray{e->position().x(), e->position().y(), e->position().z()};
        } else {
            result["success"] = false;
            result["error"] = "Entity not found: " + request["id"].toString();
        }
    } else if (action == "nearby") {
        QVariantList list = m_sceneGraph->nearbyEntities(request["id"].toString(), request["radius"].toDouble());
        QJsonArray arr;
        for (const auto &v : list) arr.append(v.toJsonValue());
        result["entities"] = arr;
        result["count"] = arr.size();
    } else if (action == "scene_info") {
        result["scene"] = m_sceneGraph->sceneInfo();
    } else if (action == "move") {
        QJsonArray posArr = request["position"].toArray();
        QVector3D pos(posArr[0].toDouble(), posArr[1].toDouble(), posArr[2].toDouble());
        result["success"] = m_sceneGraph->moveEntity(request["id"].toString(), pos);
    } else if (action == "rotate") {
        QJsonArray rotArr = request["rotation"].toArray();
        QVector3D rot(rotArr[0].toDouble(), rotArr[1].toDouble(), rotArr[2].toDouble());
        result["success"] = m_sceneGraph->rotateEntity(request["id"].toString(), rot);
    } else if (action == "resize") {
        QJsonArray dimArr = request["dimensions"].toArray();
        QVector3D dims(dimArr[0].toDouble(), dimArr[1].toDouble(), dimArr[2].toDouble());
        result["success"] = m_sceneGraph->resizeEntity(request["id"].toString(), dims);
    } else if (action == "add") {
        QString id = request.contains("id") ? request["id"].toString()
                     : "entity-" + QString::number(m_sceneGraph->entityCount() + 1);
        QJsonArray posArr = request["position"].toArray();
        QVector3D pos(posArr[0].toDouble(), posArr[1].toDouble(), posArr[2].toDouble());
        QVariantMap props;
        QJsonObject propsObj = request["properties"].toObject();
        for (auto it = propsObj.constBegin(); it != propsObj.constEnd(); ++it)
            props[it.key()] = it.value().toVariant();
        m_sceneGraph->registerEntity(id, request["type"].toString(),
                                      request.value("name").toString(id),
                                      pos, QVector3D(), props);
        result["id"] = id;
    } else if (action == "delete") {
        result["success"] = m_sceneGraph->removeEntity(request["id"].toString());
    } else if (action == "connect") {
        result["success"] = m_sceneGraph->connectEntities(request["from"].toString(), request["to"].toString());
    } else {
        result["success"] = false;
        result["error"] = "Unknown scene action: " + action;
    }

    // For query actions emit queryResult, for operate emit operateResult
    if (action == "query" || action == "get_position" || action == "nearby" || action == "scene_info") {
        emit queryResult(result);
    } else {
        emit operateResult(result);
    }

    // Also forward operate actions to Python for cost recalculation
    if (action == "move" || action == "rotate" || action == "resize" || action == "add" || action == "delete") {
        QJsonObject pyReq = request;
        pyReq["type"] = "scene_action";
        pyReq["scene_data"] = m_sceneGraph->toJson();
        sendRequest(pyReq);
    }
}

void AgentBridge::sendRequest(const QJsonObject &request)
{
    if (!m_process || m_process->state() != QProcess::Running) {
        startPython();
        if (!m_connected) {
            emit errorOccurred("Python agent not running");
            return;
        }
    }

    m_busy = true;
    emit busyChanged();
    emit statusUpdate("Processing...", 0.0);

    QJsonDocument doc(request);
    QByteArray data = doc.toJson(QJsonDocument::Compact) + "\n";
    m_process->write(data);
    m_heartbeat->start(); // reset heartbeat
}

void AgentBridge::onReadyRead()
{
    m_buffer.append(m_process->readAllStandardOutput());

    while (m_buffer.contains('\n')) {
        int idx = m_buffer.indexOf('\n');
        QByteArray line = m_buffer.left(idx).trimmed();
        m_buffer.remove(0, idx + 1);

        if (line.isEmpty()) continue;

        // Log every stdout line from Python
        ZigmaLogger::instance()->logPythonStdout(QString::fromUtf8(line));

        QJsonParseError err;
        QJsonDocument doc = QJsonDocument::fromJson(line, &err);
        if (err.error != QJsonParseError::NoError) {
            qWarning() << "AgentBridge: invalid JSON:" << line;
            continue;
        }

        handleResponse(doc.object());
    }

    m_heartbeat->start(); // reset on activity
}

void AgentBridge::handleResponse(const QJsonObject &response)
{
    QString type = response["type"].toString();

    if (type == "status") {
        emit statusUpdate(response["message"].toString(), response["progress"].toDouble());
    } else if (type == "result") {
        m_busy = false;
        emit busyChanged();
        emit resultReady(response);
    } else if (type == "delta") {
        m_busy = false;
        emit busyChanged();
        emit deltaReady(response);
    } else if (type == "scene_result") {
        m_busy = false;
        emit busyChanged();
        emit operateResult(response);
    } else if (type == "error") {
        m_busy = false;
        emit busyChanged();
        emit errorOccurred(response["message"].toString());
    }
}

void AgentBridge::onProcessFinished(int exitCode, QProcess::ExitStatus status)
{
    Q_UNUSED(exitCode)
    m_heartbeat->stop();
    bool wasConnected = m_connected;
    m_connected = false;
    m_busy = false;

    if (wasConnected) {
        emit connectedChanged();
        emit busyChanged();

        if (status == QProcess::CrashExit) {
            emit errorOccurred("Python agent crashed, restarting...");
            restartPython();
        }
    }
}

void AgentBridge::onHeartbeatTimeout()
{
    qWarning() << "AgentBridge: heartbeat timeout, restarting Python";
    emit errorOccurred("Python agent timeout, restarting...");
    restartPython();
}

void AgentBridge::restartPython()
{
    if (m_restartCount >= 3) {
        emit errorOccurred("Python agent failed to restart after 3 attempts");
        return;
    }
    m_restartCount++;
    m_reconnecting = true;
    emit reconnectingChanged();
    emit statusUpdate("AI reconnecting... (attempt " + QString::number(m_restartCount) + "/3)", 0.0);
    stopPython();
    QTimer::singleShot(1000 * m_restartCount, this, &AgentBridge::startPython);
}

void AgentBridge::onReadyReadStderr()
{
    if (!m_process) return;
    QByteArray data = m_process->readAllStandardError();
    QString text = QString::fromUtf8(data);
    const QStringList lines = text.split('\n', Qt::SkipEmptyParts);
    for (const QString &line : lines) {
        ZigmaLogger::instance()->logPythonStderr(line.trimmed());
    }
}
