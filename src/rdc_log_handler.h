#pragma once
// CHAIN-V8 Phase 3 T66-T70: RDCLogHandler for PTB Qt
// Installs a Qt message handler and forwards logs to RDC Server /api/logs/ptb
// Features: async delivery, offline buffer (100 entries), auto-flush

#include <QObject>
#include <QString>
#include <QJsonObject>
#include <QJsonDocument>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QDateTime>
#include <QMutex>
#include <QQueue>
#include <QTimer>
#include <QUrl>
#include <QtMessageHandler>

class RDCLogHandler : public QObject
{
    Q_OBJECT
public:
    static constexpr int kMaxBufferSize = 100;
    static constexpr int kFlushIntervalMs = 5000;

    static void install(const QString &serverBaseUrl)
    {
        QMutexLocker lock(&s_instanceMutex);
        if (!s_instance) {
            s_instance = new RDCLogHandler(serverBaseUrl);
            s_previousHandler = qInstallMessageHandler(&RDCLogHandler::qtMessageHandler);
        } else {
            s_instance->m_serverBaseUrl = serverBaseUrl;
        }
    }

    static void uninstall()
    {
        QMutexLocker lock(&s_instanceMutex);
        if (s_instance) {
            qInstallMessageHandler(s_previousHandler);
            s_previousHandler = nullptr;
            delete s_instance;
            s_instance = nullptr;
        }
    }

    ~RDCLogHandler() override { m_flushTimer->stop(); }

private:
    explicit RDCLogHandler(const QString &serverBaseUrl, QObject *parent = nullptr)
        : QObject(parent), m_serverBaseUrl(serverBaseUrl),
          m_nam(new QNetworkAccessManager(this)),
          m_flushTimer(new QTimer(this)), m_pendingRequest(false)
    {
        m_flushTimer->setInterval(kFlushIntervalMs);
        connect(m_flushTimer, &QTimer::timeout, this, &RDCLogHandler::flushBuffer);
        m_flushTimer->start();
    }

    static void qtMessageHandler(QtMsgType type, const QMessageLogContext &context, const QString &msg)
    {
        if (s_previousHandler) s_previousHandler(type, context, msg);
        else fprintf(stderr, "%s\n", msg.toLocal8Bit().constData());
        if (!s_instance) return;
        QJsonObject payload = s_instance->buildPayload(type, context, msg);
        QMetaObject::invokeMethod(s_instance, "enqueueAndSend", Qt::QueuedConnection, Q_ARG(QJsonObject, payload));
    }

    QJsonObject buildPayload(QtMsgType type, const QMessageLogContext &context, const QString &msg) const
    {
        QJsonObject obj;
        obj["level"] = qtMsgTypeToString(type);
        obj["source"] = QStringLiteral("ptb");
        obj["projectKey"] = QStringLiteral("PTB");
        obj["message"] = msg;
        obj["timestamp"] = QDateTime::currentDateTimeUtc().toString(Qt::ISODateWithMs);
        obj["category"] = (context.category && *context.category) ? QString::fromUtf8(context.category) : QStringLiteral("default");
        return obj;
    }

    static QString qtMsgTypeToString(QtMsgType type)
    {
        switch (type) {
        case QtDebugMsg:    return QStringLiteral("debug");
        case QtInfoMsg:     return QStringLiteral("info");
        case QtWarningMsg:  return QStringLiteral("warning");
        case QtCriticalMsg: return QStringLiteral("critical");
        case QtFatalMsg:    return QStringLiteral("fatal");
        default:            return QStringLiteral("unknown");
        }
    }

    Q_INVOKABLE void enqueueAndSend(const QJsonObject &payload)
    {
        { QMutexLocker lock(&m_bufferMutex);
          if (m_buffer.size() >= kMaxBufferSize) m_buffer.dequeue();
          m_buffer.enqueue(payload); }
        if (!m_pendingRequest) sendNext();
    }

    void sendNext()
    {
        QJsonObject payload;
        { QMutexLocker lock(&m_bufferMutex);
          if (m_buffer.isEmpty()) return;
          payload = m_buffer.head(); }
        m_pendingRequest = true;
        QUrl url(m_serverBaseUrl + QStringLiteral("/api/logs/ptb"));
        QNetworkRequest request(url);
        request.setHeader(QNetworkRequest::ContentTypeHeader, QStringLiteral("application/json"));
        request.setTransferTimeout(3000);
        QNetworkReply *reply = m_nam->post(request, QJsonDocument(payload).toJson(QJsonDocument::Compact));
        if (!reply) { m_pendingRequest = false; return; }
        connect(reply, &QNetworkReply::finished, this, [this, reply]() {
            reply->deleteLater();
            m_pendingRequest = false;
            if (reply->error() == QNetworkReply::NoError) {
                QMutexLocker lock(&m_bufferMutex);
                if (!m_buffer.isEmpty()) m_buffer.dequeue();
                lock.unlock();
                sendNext();
            }
        });
    }

    void flushBuffer()
    {
        QMutexLocker lock(&m_bufferMutex);
        bool has = !m_buffer.isEmpty();
        lock.unlock();
        if (has && !m_pendingRequest) sendNext();
    }

    QString m_serverBaseUrl;
    QNetworkAccessManager *m_nam;
    QTimer *m_flushTimer;
    QQueue<QJsonObject> m_buffer;
    QMutex m_bufferMutex;
    bool m_pendingRequest;
    static RDCLogHandler *s_instance;
    static QMutex s_instanceMutex;
    static QtMessageHandler s_previousHandler;
};

#ifdef RDC_LOG_HANDLER_IMPL
RDCLogHandler *RDCLogHandler::s_instance = nullptr;
QMutex RDCLogHandler::s_instanceMutex;
QtMessageHandler RDCLogHandler::s_previousHandler = nullptr;
#endif