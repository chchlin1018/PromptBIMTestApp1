#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QUrl>
#include <QDebug>
#include "ZigmaLogger.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    app.setApplicationName("Zigma PromptToBuild");
    app.setApplicationVersion("0.2.0");
    app.setOrganizationName("Zigma");

    // Install ZigmaLogger before anything else
    ZigmaLogger::install();
    ZLOG_INFO("Main", "Zigma PromptToBuild v0.2.0 starting");

    QQmlApplicationEngine engine;

    // Register ZigmaLogger as QML context property
    engine.rootContext()->setContextProperty("zigmaLogger", ZigmaLogger::instance());

    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreationFailed,
        &app, []() {
            ZLOG_ERROR("Main", "QML object creation failed");
            QCoreApplication::exit(-1);
        },
        Qt::QueuedConnection);

    engine.load(QUrl(QStringLiteral("qrc:/Zigma/qml/main.qml")));

    if (engine.rootObjects().isEmpty()) {
        ZLOG_ERROR("Main", "No root objects loaded");
        return -1;
    }

    ZLOG_INFO("Main", "Application ready");
    return app.exec();
}
