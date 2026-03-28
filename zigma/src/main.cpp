#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QUrl>
#include <QDebug>

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    app.setApplicationName("Zigma PromptToBuild");
    app.setApplicationVersion("0.1.0");
    app.setOrganizationName("Zigma");

    QQmlApplicationEngine engine;

    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreationFailed,
        &app, []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);

    // Try known Qt6 QML module resource paths
    QStringList paths = {
        "qrc:/qt/qml/Zigma/qml/main.qml",
        "qrc:/qt/qml/Zigma/main.qml",
        "qrc:/Zigma/qml/main.qml",
        "qrc:/Zigma/main.qml",
    };

    for (const auto &p : paths) {
        engine.load(QUrl(p));
        if (!engine.rootObjects().isEmpty()) {
            qDebug() << "Loaded QML from:" << p;
            return app.exec();
        }
    }

    // Fallback: loadFromModule
    engine.loadFromModule("Zigma", "Main");
    if (!engine.rootObjects().isEmpty())
        return app.exec();

    qCritical() << "Failed to load main.qml from any path";
    return -1;
}
