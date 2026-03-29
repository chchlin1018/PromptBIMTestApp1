#ifndef AGENTBRIDGE_H
#define AGENTBRIDGE_H

#include <QObject>
#include <QProcess>
#include <QJsonObject>
#include <QJsonArray>
#include <QTimer>
#include <QQmlEngine>
#include <QVector3D>

class BIMSceneGraph;

class AgentBridge : public QObject
{
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(bool connected READ isConnected NOTIFY connectedChanged)
    Q_PROPERTY(bool busy READ isBusy NOTIFY busyChanged)
    Q_PROPERTY(bool reconnecting READ isReconnecting NOTIFY reconnectingChanged)

public:
    explicit AgentBridge(QObject *parent = nullptr);
    ~AgentBridge() override;

    bool isConnected() const;
    bool isBusy() const;
    bool isReconnecting() const;

    Q_INVOKABLE void generate(const QString &prompt, const QJsonObject &landData);
    Q_INVOKABLE void modify(const QString &intent);
    Q_INVOKABLE void getCost();
    Q_INVOKABLE void getSchedule();
    Q_INVOKABLE void startPython();
    Q_INVOKABLE void stopPython();

    // Scene Query actions (M2-BRIDGE)
    Q_INVOKABLE void queryByType(const QString &type);
    Q_INVOKABLE void queryByName(const QString &name);
    Q_INVOKABLE void getPosition(const QString &id);
    Q_INVOKABLE void getNearby(const QString &id, double radius);
    Q_INVOKABLE void getSceneInfo();

    // Scene Operate actions (M2-BRIDGE)
    Q_INVOKABLE void moveEntity(const QString &id, const QVector3D &position);
    Q_INVOKABLE void rotateEntity(const QString &id, const QVector3D &rotation);
    Q_INVOKABLE void resizeEntity(const QString &id, const QVector3D &dimensions);
    Q_INVOKABLE void addEntity(const QString &type, const QVector3D &position, const QJsonObject &properties);
    Q_INVOKABLE void deleteEntity(const QString &id);
    Q_INVOKABLE void connectEntities(const QString &fromId, const QString &toId);

    // Cost/Schedule delta
    Q_INVOKABLE void getCostDelta();
    Q_INVOKABLE void getScheduleImpact();

    void setSceneGraph(BIMSceneGraph *sg);

signals:
    void connectedChanged();
    void busyChanged();
    void reconnectingChanged();
    void resultReady(const QJsonObject &result);
    void statusUpdate(const QString &message, double progress);
    void deltaReady(const QJsonObject &delta);
    void errorOccurred(const QString &error);
    void queryResult(const QJsonObject &result);
    void operateResult(const QJsonObject &result);

private slots:
    void onReadyRead();
    void onReadyReadStderr();
    void onProcessFinished(int exitCode, QProcess::ExitStatus status);
    void onHeartbeatTimeout();

private:
    void sendRequest(const QJsonObject &request);
    void handleResponse(const QJsonObject &response);
    void handleSceneAction(const QJsonObject &request);
    void restartPython();

    BIMSceneGraph *m_sceneGraph = nullptr;
    QProcess *m_process = nullptr;
    QTimer *m_heartbeat = nullptr;
    bool m_connected = false;
    bool m_busy = false;
    bool m_reconnecting = false;
    int m_restartCount = 0;
    QByteArray m_buffer;
    QString m_pythonRunner;
};

#endif // AGENTBRIDGE_H
