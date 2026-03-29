#include <QTest>
#include <QSignalSpy>
#include <QJsonObject>
#include <QJsonArray>
#include <QVector3D>
#include "BIMEntity.h"

class TestBIMEntity : public QObject
{
    Q_OBJECT

private slots:
    void testDefaultConstruction()
    {
        BIMEntity e;
        QVERIFY(e.entityId().isEmpty());
        QVERIFY(e.type().isEmpty());
        QVERIFY(e.name().isEmpty());
        QCOMPARE(e.position(), QVector3D());
        QCOMPARE(e.rotation(), QVector3D());
        QCOMPARE(e.dimensions(), QVector3D());
        QVERIFY(e.properties().isEmpty());
        QVERIFY(e.connections().isEmpty());
        QVERIFY(e.model3D().isEmpty());
    }

    void testSetProperties()
    {
        BIMEntity e;
        QSignalSpy idSpy(&e, &BIMEntity::entityIdChanged);
        QSignalSpy typeSpy(&e, &BIMEntity::typeChanged);
        QSignalSpy nameSpy(&e, &BIMEntity::nameChanged);
        QSignalSpy posSpy(&e, &BIMEntity::positionChanged);

        e.setEntityId("chiller-A");
        e.setType("MEP.Chiller");
        e.setName("冰水主機-A");
        e.setPosition(QVector3D(48, 3, -5));

        QCOMPARE(e.entityId(), "chiller-A");
        QCOMPARE(e.type(), "MEP.Chiller");
        QCOMPARE(e.name(), "冰水主機-A");
        QCOMPARE(e.position(), QVector3D(48, 3, -5));

        QCOMPARE(idSpy.count(), 1);
        QCOMPARE(typeSpy.count(), 1);
        QCOMPARE(nameSpy.count(), 1);
        QCOMPARE(posSpy.count(), 1);
    }

    void testNoSpuriousSignals()
    {
        BIMEntity e;
        e.setEntityId("test");
        QSignalSpy spy(&e, &BIMEntity::entityIdChanged);
        e.setEntityId("test"); // same value
        QCOMPARE(spy.count(), 0);
    }

    void testConnections()
    {
        BIMEntity e;
        QSignalSpy spy(&e, &BIMEntity::connectionsChanged);

        e.addConnection("pipe-01");
        QCOMPARE(e.connections().size(), 1);
        QCOMPARE(spy.count(), 1);

        e.addConnection("pipe-01"); // duplicate
        QCOMPARE(e.connections().size(), 1);
        QCOMPARE(spy.count(), 1);

        e.addConnection("pipe-02");
        QCOMPARE(e.connections().size(), 2);

        e.removeConnection("pipe-01");
        QCOMPARE(e.connections().size(), 1);
        QVERIFY(e.connections().contains("pipe-02"));
    }

    void testToJson()
    {
        BIMEntity e;
        e.setEntityId("tower-01");
        e.setType("MEP.CoolingTower");
        e.setName("CoolingTower-01");
        e.setPosition(QVector3D(43, 6, 30));
        e.setDimensions(QVector3D(6, 12, 6));
        QVariantMap props;
        props["capacity_rt"] = 600;
        e.setProperties(props);
        e.addConnection("chiller-A");

        QJsonObject json = e.toJson();
        QCOMPARE(json["id"].toString(), "tower-01");
        QCOMPARE(json["type"].toString(), "MEP.CoolingTower");
        QCOMPARE(json["name"].toString(), "CoolingTower-01");

        QJsonArray posArr = json["position"].toArray();
        QCOMPARE(posArr.size(), 3);
        QCOMPARE(posArr[0].toDouble(), 43.0);

        QJsonObject propsObj = json["properties"].toObject();
        QCOMPARE(propsObj["capacity_rt"].toInt(), 600);

        QJsonArray conns = json["connections"].toArray();
        QCOMPARE(conns.size(), 1);
        QCOMPARE(conns[0].toString(), "chiller-A");
    }

    void testFromJson()
    {
        QJsonObject json;
        json["id"] = "stack-01";
        json["type"] = "MEP.ExhaustStack";
        json["name"] = "ExhaustStack-01";
        json["position"] = QJsonArray{-20, 17.5, -35};
        json["dimensions"] = QJsonArray{2, 35, 2};
        QJsonObject props;
        props["height_m"] = 35;
        json["properties"] = props;
        json["connections"] = QJsonArray{"duct-01"};

        BIMEntity e;
        e.fromJson(json);

        QCOMPARE(e.entityId(), "stack-01");
        QCOMPARE(e.type(), "MEP.ExhaustStack");
        QCOMPARE(e.position(), QVector3D(-20, 17.5, -35));
        QCOMPARE(e.dimensions(), QVector3D(2, 35, 2));
        QCOMPARE(e.properties()["height_m"].toInt(), 35);
        QCOMPARE(e.connections().size(), 1);
    }

    void testDistanceTo()
    {
        BIMEntity a, b;
        a.setPosition(QVector3D(0, 0, 0));
        b.setPosition(QVector3D(3, 4, 0));
        QCOMPARE(a.distanceTo(&b), 5.0);
        QCOMPARE(a.distanceTo(nullptr), -1.0);
    }

    void testRoundTrip()
    {
        BIMEntity original;
        original.setEntityId("comp-01");
        original.setType("MEP.Compressor");
        original.setName("Compressor-01");
        original.setPosition(QVector3D(50, 2.5, 5));
        original.setRotation(QVector3D(0, 90, 0));
        original.setDimensions(QVector3D(3, 5, 3));

        QJsonObject json = original.toJson();

        BIMEntity copy;
        copy.fromJson(json);

        QCOMPARE(copy.entityId(), original.entityId());
        QCOMPARE(copy.type(), original.type());
        QCOMPARE(copy.name(), original.name());
        QCOMPARE(copy.position(), original.position());
        QCOMPARE(copy.rotation(), original.rotation());
        QCOMPARE(copy.dimensions(), original.dimensions());
    }
};

QTEST_MAIN(TestBIMEntity)
#include "test_bim_entity.moc"
