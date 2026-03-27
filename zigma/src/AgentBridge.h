#ifndef AGENTBRIDGE_H
#define AGENTBRIDGE_H

#include <QObject>
#include <QProcess>
#include <QJsonObject>
#include <QTimer>
#include <QQmlEngine>

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

signals:
    void connectedChanged();
    void busyChanged();
    void reconnectingChanged();
    void resultReady(const QJsonObject &result);
    void statusUpdate(const QString &message, double progress);
    void deltaReady(const QJsonObject &delta);
    void errorOccurred(const QString &error);

private slots:
    void onReadyRead();
    void onProcessFinished(int exitCode, QProcess::ExitStatus status);
    void onHeartbeatTimeout();

private:
    void sendRequest(const QJsonObject &request);
    void handleResponse(const QJsonObject &response);
    void restartPython();

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
