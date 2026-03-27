#include "AgentBridge.h"
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

void AgentBridge::startPython()
{
    if (m_process && m_process->state() != QProcess::NotRunning) return;

    m_process = new QProcess(this);
    connect(m_process, &QProcess::readyReadStandardOutput, this, &AgentBridge::onReadyRead);
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
    stopPython();
    QTimer::singleShot(1000, this, &AgentBridge::startPython);
}
