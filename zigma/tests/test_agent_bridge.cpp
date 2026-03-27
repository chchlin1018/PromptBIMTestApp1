#include <QtTest/QtTest>
#include <QJsonObject>
#include <QJsonDocument>
#include <QJsonArray>
#include <QSignalSpy>
#include "../src/AgentBridge.h"

class TestAgentBridge : public QObject
{
    Q_OBJECT

private slots:
    void testConstruction()
    {
        AgentBridge bridge;
        QVERIFY(!bridge.isConnected());
        QVERIFY(!bridge.isBusy());
    }

    void testConnectedPropertyDefault()
    {
        AgentBridge bridge;
        QCOMPARE(bridge.isConnected(), false);
    }

    void testBusyPropertyDefault()
    {
        AgentBridge bridge;
        QCOMPARE(bridge.isBusy(), false);
    }

    void testSignalsExist()
    {
        AgentBridge bridge;
        // Verify signals can be connected
        QSignalSpy connSpy(&bridge, &AgentBridge::connectedChanged);
        QSignalSpy busySpy(&bridge, &AgentBridge::busyChanged);
        QSignalSpy resultSpy(&bridge, &AgentBridge::resultReady);
        QSignalSpy statusSpy(&bridge, &AgentBridge::statusUpdate);
        QSignalSpy deltaSpy(&bridge, &AgentBridge::deltaReady);
        QSignalSpy errorSpy(&bridge, &AgentBridge::errorOccurred);
        QVERIFY(connSpy.isValid());
        QVERIFY(busySpy.isValid());
        QVERIFY(resultSpy.isValid());
        QVERIFY(statusSpy.isValid());
        QVERIFY(deltaSpy.isValid());
        QVERIFY(errorSpy.isValid());
    }

    void testStopPythonSafe()
    {
        // stopPython should be safe to call even if never started
        AgentBridge bridge;
        bridge.stopPython();
        QVERIFY(!bridge.isConnected());
    }

    void testJsonRequestFormat()
    {
        // Verify our JSON format matches the protocol
        QJsonObject req;
        req["type"] = "generate";
        req["prompt"] = "Build a factory";
        QJsonObject land;
        land["width"] = 100;
        land["depth"] = 80;
        req["land"] = land;

        QJsonDocument doc(req);
        QByteArray data = doc.toJson(QJsonDocument::Compact);
        QVERIFY(data.contains("\"type\":\"generate\""));
        QVERIFY(data.contains("\"prompt\":\"Build a factory\""));
        QVERIFY(data.contains("\"width\":100"));
    }

    void testJsonResponseParsing()
    {
        // Verify we can parse a response JSON
        QByteArray response = R"({"type":"result","model":{"elements":[]},"cost":{},"schedule":{}})";
        QJsonDocument doc = QJsonDocument::fromJson(response);
        QVERIFY(!doc.isNull());
        QJsonObject obj = doc.object();
        QCOMPARE(obj["type"].toString(), QString("result"));
        QVERIFY(obj.contains("model"));
    }

    void testStatusResponseParsing()
    {
        QByteArray response = R"({"type":"status","message":"Processing...","progress":0.5})";
        QJsonDocument doc = QJsonDocument::fromJson(response);
        QVERIFY(!doc.isNull());
        QJsonObject obj = doc.object();
        QCOMPARE(obj["type"].toString(), QString("status"));
        QCOMPARE(obj["progress"].toDouble(), 0.5);
    }
};

QTEST_MAIN(TestAgentBridge)
#include "test_agent_bridge.moc"
