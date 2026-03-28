#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QUrl>

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

    // Qt6 qt_add_qml_module puts files at :/qt/qml/{URI}/{relative_path}
    const QUrl url(QStringLiteral("qrc:/qt/qml/Zigma/qml/main.qml"));

    // Try multiple resource paths for compatibility
    QStringList paths = {
        "qrc:/qt/qml/Zigma/qml/main.qml",
        "qrc:/qt/qml/Zigma/main.qml",
        "qrc:/Zigma/qml/main.qml",
        "qrc:/Zigma/main.qml",
    };

    bool loaded = false;
    for (const auto &p : paths) {
        QUrl u(p);
        engine.load(u);
        if (!engine.rootObjects().isEmpty()) {
            loaded = true;
            break;
        }
    }

    if (!loaded) {
        qCritical() << "Failed to load main.qml from any resource path";
        qCritical() << "Available resources:";
        QDirIterator it(":", QDirIterator::Subdirectories);
        while (it.hasNext()) {
            QString path = it.next();
            if (path.contains("qml", Qt::CaseInsensitive) || path.contains("Zigma"))
                qCritical() << "  " << path;
        }
        return -1;
    }

    return app.exec();
}
