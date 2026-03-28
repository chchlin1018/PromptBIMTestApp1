#include "ZigmaLogger.h"
#include <QStandardPaths>
#include <iostream>

ZigmaLogger *ZigmaLogger::s_instance = nullptr;

ZigmaLogger::ZigmaLogger(QObject *parent)
    : QObject(parent)
{
    m_projectRoot = findProjectRoot();

    // Create debuglog directory
    QDir logDir(m_projectRoot + "/debuglog");
    if (!logDir.exists())
        logDir.mkpath(".");

    // Rotate old logs
    rotateOldLogs(logDir, 10);

    // Open new log file
    QString timestamp = QDateTime::currentDateTime().toString("yyyyMMdd_HHmmss");
    QString logPath = logDir.filePath(QString("zigma_%1.log").arg(timestamp));
    m_logFile.setFileName(logPath);
    if (m_logFile.open(QIODevice::WriteOnly | QIODevice::Text)) {
        m_stream.setDevice(&m_logFile);
        writeLine(QString("[%1] [INFO ] [ZigmaLogger ] Log started: %2")
                      .arg(QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz"), logPath));
        writeLine(QString("[%1] [INFO ] [ZigmaLogger ] Project root: %2")
                      .arg(QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz"), m_projectRoot));
    }
}

ZigmaLogger::~ZigmaLogger()
{
    if (m_logFile.isOpen()) {
        writeLine(QString("[%1] [INFO ] [ZigmaLogger ] Log closed")
                      .arg(QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz")));
        m_logFile.close();
    }
}

ZigmaLogger *ZigmaLogger::instance()
{
    if (!s_instance)
        s_instance = new ZigmaLogger();
    return s_instance;
}

void ZigmaLogger::install()
{
    instance(); // ensure created
    qInstallMessageHandler(ZigmaLogger::qtMessageHandler);
    ZLOG_INFO("ZigmaLogger", "Qt message handler installed");
}

void ZigmaLogger::log(Level level, const QString &category, const QString &message)
{
    QString ts = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz");
    QString line = QString("[%1] [%2] [%3] %4")
                       .arg(ts, levelString(level), padCategory(category), message);
    writeLine(line);
}

void ZigmaLogger::logFromQml(const QString &category, const QString &level, const QString &message)
{
    log(levelFromString(level), category, message);
}

void ZigmaLogger::logPythonStdout(const QString &line)
{
    log(INFO, "Python", line);
}

void ZigmaLogger::logPythonStderr(const QString &line)
{
    // Auto-detect level from content
    Level lvl = DEBUG;
    if (line.contains("ERROR", Qt::CaseInsensitive) || line.contains("Traceback", Qt::CaseInsensitive))
        lvl = ERROR;
    else if (line.contains("WARNING", Qt::CaseInsensitive) || line.contains("WARN", Qt::CaseInsensitive))
        lvl = WARN;
    else if (line.contains("INFO", Qt::CaseInsensitive))
        lvl = INFO;
    log(lvl, "Python", line);
}

void ZigmaLogger::qtMessageHandler(QtMsgType type, const QMessageLogContext &context, const QString &msg)
{
    Q_UNUSED(context)
    Level level;
    switch (type) {
    case QtDebugMsg:    level = DEBUG; break;
    case QtInfoMsg:     level = INFO;  break;
    case QtWarningMsg:  level = WARN;  break;
    case QtCriticalMsg: level = ERROR; break;
    case QtFatalMsg:    level = ERROR; break;
    }

    QString category = context.category ? QString(context.category) : "Qt";
    if (category == "default")
        category = "Qt";

    instance()->log(level, category, msg);
}

QString ZigmaLogger::findProjectRoot()
{
    QDir dir(QCoreApplication::applicationDirPath());

    // Walk up from app binary looking for CLAUDE.md
    for (int i = 0; i < 10; ++i) {
        if (dir.exists("CLAUDE.md") || dir.exists("SKILL.md"))
            return dir.absolutePath();
        if (!dir.cdUp())
            break;
    }

    // Fallback: current working dir
    return QDir::currentPath();
}

QString ZigmaLogger::padCategory(const QString &cat, int width)
{
    if (cat.length() >= width)
        return cat.left(width);
    return cat + QString(width - cat.length(), ' ');
}

QString ZigmaLogger::levelString(Level level)
{
    switch (level) {
    case TRACE: return "TRACE";
    case DEBUG: return "DEBUG";
    case INFO:  return "INFO ";
    case WARN:  return "WARN ";
    case ERROR: return "ERROR";
    }
    return "?????";
}

ZigmaLogger::Level ZigmaLogger::levelFromString(const QString &str)
{
    QString s = str.toUpper().trimmed();
    if (s == "TRACE") return TRACE;
    if (s == "DEBUG") return DEBUG;
    if (s == "INFO")  return INFO;
    if (s == "WARN" || s == "WARNING") return WARN;
    if (s == "ERROR") return ERROR;
    return INFO;
}

void ZigmaLogger::rotateOldLogs(const QDir &logDir, int maxKeep)
{
    QStringList logs = logDir.entryList({"zigma_*.log"}, QDir::Files, QDir::Name);
    while (logs.size() >= maxKeep) {
        QFile::remove(logDir.filePath(logs.takeFirst()));
    }
}

void ZigmaLogger::writeLine(const QString &formatted)
{
    QMutexLocker locker(&m_mutex);

    // Write to file
    if (m_logFile.isOpen()) {
        m_stream << formatted << "\n";
        m_stream.flush();
    }

    // Write to stderr (Terminal)
    std::cerr << formatted.toStdString() << std::endl;
}
