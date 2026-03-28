#ifndef ZIGMALOGGER_H
#define ZIGMALOGGER_H

#include <QObject>
#include <QFile>
#include <QTextStream>
#include <QMutex>
#include <QDir>
#include <QDateTime>
#include <QCoreApplication>
#include <QQmlEngine>

// Convenience macros
#define ZLOG_TRACE(cat, msg) ZigmaLogger::instance()->log(ZigmaLogger::TRACE, cat, msg)
#define ZLOG_DEBUG(cat, msg) ZigmaLogger::instance()->log(ZigmaLogger::DEBUG, cat, msg)
#define ZLOG_INFO(cat, msg)  ZigmaLogger::instance()->log(ZigmaLogger::INFO,  cat, msg)
#define ZLOG_WARN(cat, msg)  ZigmaLogger::instance()->log(ZigmaLogger::WARN,  cat, msg)
#define ZLOG_ERROR(cat, msg) ZigmaLogger::instance()->log(ZigmaLogger::ERROR, cat, msg)

class ZigmaLogger : public QObject
{
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON

public:
    enum Level { TRACE = 0, DEBUG, INFO, WARN, ERROR };
    Q_ENUM(Level)

    static ZigmaLogger *instance();
    static void install();

    void log(Level level, const QString &category, const QString &message);

    Q_INVOKABLE void logFromQml(const QString &category, const QString &level, const QString &message);
    void logPythonStdout(const QString &line);
    void logPythonStderr(const QString &line);

private:
    explicit ZigmaLogger(QObject *parent = nullptr);
    ~ZigmaLogger() override;

    static void qtMessageHandler(QtMsgType type, const QMessageLogContext &context, const QString &msg);
    static QString findProjectRoot();
    static QString padCategory(const QString &cat, int width = 12);
    static QString levelString(Level level);
    static Level levelFromString(const QString &str);
    void rotateOldLogs(const QDir &logDir, int maxKeep = 10);
    void writeLine(const QString &formatted);

    static ZigmaLogger *s_instance;
    QFile m_logFile;
    QTextStream m_stream;
    QMutex m_mutex;
    QString m_projectRoot;
};

#endif // ZIGMALOGGER_H
