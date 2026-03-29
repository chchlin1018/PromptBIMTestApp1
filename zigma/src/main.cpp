#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QUrl>
#include <QDebug>
#include "ZigmaLogger.h"
#include "BIMSceneGraph.h"
#include "BIMEntityModel.h"
#include "SceneGraphModel.h"
#include "AgentBridge.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    app.setApplicationName("Zigma PromptToBuild");
    app.setApplicationVersion("0.4.0");
    app.setOrganizationName("Zigma");

    // Install ZigmaLogger before anything else
    ZigmaLogger::install();
    ZLOG_INFO("Main", "Zigma PromptToBuild v0.4.0 starting");

    QQmlApplicationEngine engine;

    // Register context properties
    engine.rootContext()->setContextProperty("zigmaLogger", ZigmaLogger::instance());

    // Register BIMSceneGraph as global QML context
    auto *sceneGraph = new BIMSceneGraph(&engine);
    engine.rootContext()->setContextProperty("sceneGraph", sceneGraph);

    // Register BIMEntityModel — list model for QML binding
    auto *entityModel = new BIMEntityModel(&engine);
    entityModel->setSceneGraph(sceneGraph);
    engine.rootContext()->setContextProperty("entityModel", entityModel);

    // Register SceneGraphModel — tree model for hierarchy view
    auto *sceneTreeModel = new SceneGraphModel(&engine);
    sceneTreeModel->setSceneGraph(sceneGraph);
    engine.rootContext()->setContextProperty("sceneTreeModel", sceneTreeModel);

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

    // Wire AgentBridge ↔ SceneGraph after QML loads
    auto *rootObj = engine.rootObjects().first();
    auto *agentBridge = rootObj->findChild<AgentBridge*>();
    if (agentBridge) {
        agentBridge->setSceneGraph(sceneGraph);
        ZLOG_INFO("Main", "AgentBridge connected to SceneGraph");
    }

    ZLOG_INFO("Main", "Application ready");
    return app.exec();
}
