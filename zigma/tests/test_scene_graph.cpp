#include <QTest>
#include <QSignalSpy>
#include <QJsonObject>
#include <QJsonArray>
#include "BIMSceneGraph.h"
#include "BIMEntity.h"

class TestSceneGraph : public QObject
{
    Q_OBJECT

private:
    BIMEntity *makeEntity(const QString &id, const QString &type, const QString &name,
                          const QVector3D &pos, QObject *parent = nullptr)
    {
        auto *e = new BIMEntity(parent);
        e->setEntityId(id);
        e->setType(type);
        e->setName(name);
        e->setPosition(pos);
        return e;
    }

private slots:
    void testAddRemove()
    {
        BIMSceneGraph sg;
        QSignalSpy addSpy(&sg, &BIMSceneGraph::entityAdded);
        QSignalSpy removeSpy(&sg, &BIMSceneGraph::entityRemoved);
        QSignalSpy countSpy(&sg, &BIMSceneGraph::entityCountChanged);

        QCOMPARE(sg.entityCount(), 0);

        auto *e = makeEntity("chiller-A", "MEP.Chiller", "冰水主機-A", QVector3D(48, 3, -5));
        sg.addEntity(e);
        QCOMPARE(sg.entityCount(), 1);
        QCOMPARE(addSpy.count(), 1);
        QCOMPARE(addSpy.first().first().toString(), "chiller-A");

        QVERIFY(sg.findEntity("chiller-A") != nullptr);
        QVERIFY(sg.findEntity("nonexistent") == nullptr);

        QVERIFY(sg.removeEntity("chiller-A"));
        QCOMPARE(sg.entityCount(), 0);
        QCOMPARE(removeSpy.count(), 1);

        QVERIFY(!sg.removeEntity("nonexistent"));
    }

    void testQueryByType()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("chiller-A", "MEP.Chiller", "冰水主機-A", QVector3D(48, 3, -5)));
        sg.addEntity(makeEntity("chiller-B", "MEP.Chiller", "冰水主機-B", QVector3D(55, 3, -5)));
        sg.addEntity(makeEntity("column-C1", "Structural.Column", "Column-C1", QVector3D(43, 8, -8)));

        QVariantList chillers = sg.queryByType("MEP.Chiller");
        QCOMPARE(chillers.size(), 2);

        QVariantList columns = sg.queryByType("Structural.Column");
        QCOMPARE(columns.size(), 1);

        QVariantList none = sg.queryByType("Nonexistent");
        QCOMPARE(none.size(), 0);
    }

    void testQueryByName()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("chiller-A", "MEP.Chiller", "冰水主機-A", QVector3D(48, 3, -5)));
        sg.addEntity(makeEntity("chiller-B", "MEP.Chiller", "冰水主機-B", QVector3D(55, 3, -5)));

        QVariantList results = sg.queryByName("冰水主機");
        QCOMPARE(results.size(), 2);

        results = sg.queryByName("主機-A");
        QCOMPARE(results.size(), 1);
    }

    void testNearby()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("a", "T", "A", QVector3D(0, 0, 0)));
        sg.addEntity(makeEntity("b", "T", "B", QVector3D(3, 4, 0))); // dist=5
        sg.addEntity(makeEntity("c", "T", "C", QVector3D(100, 0, 0))); // dist=100

        QVariantList nearby = sg.nearbyEntities("a", 10);
        QCOMPARE(nearby.size(), 1); // only b

        nearby = sg.nearbyEntities("a", 200);
        QCOMPARE(nearby.size(), 2); // b and c
    }

    void testMoveEntity()
    {
        BIMSceneGraph sg;
        QSignalSpy moveSpy(&sg, &BIMSceneGraph::entityMoved);

        sg.addEntity(makeEntity("chiller-A", "MEP.Chiller", "冰水主機-A", QVector3D(48, 3, -5)));
        QVector3D newPos(25, 0, 8);
        QVERIFY(sg.moveEntity("chiller-A", newPos));
        QCOMPARE(sg.findEntity("chiller-A")->position(), newPos);
        QCOMPARE(moveSpy.count(), 1);

        QVERIFY(!sg.moveEntity("nonexistent", QVector3D()));
    }

    void testRotateResize()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("stack-01", "MEP.ExhaustStack", "ExhaustStack-01", QVector3D(0, 0, 0)));

        QVERIFY(sg.rotateEntity("stack-01", QVector3D(0, 90, 0)));
        QCOMPARE(sg.findEntity("stack-01")->rotation(), QVector3D(0, 90, 0));

        QVERIFY(sg.resizeEntity("stack-01", QVector3D(2, 45, 2)));
        QCOMPARE(sg.findEntity("stack-01")->dimensions(), QVector3D(2, 45, 2));
    }

    void testConnect()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("chiller-A", "MEP.Chiller", "A", QVector3D(0, 0, 0)));
        sg.addEntity(makeEntity("pipe-01", "MEP.Pipe", "P", QVector3D(5, 0, 0)));

        QVERIFY(sg.connectEntities("chiller-A", "pipe-01"));
        QVERIFY(sg.findEntity("chiller-A")->connections().contains("pipe-01"));
        QVERIFY(sg.findEntity("pipe-01")->connections().contains("chiller-A"));

        QVERIFY(!sg.connectEntities("chiller-A", "nonexistent"));
    }

    void testSerializeRoundTrip()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("a", "T1", "Name-A", QVector3D(1, 2, 3)));
        sg.addEntity(makeEntity("b", "T2", "Name-B", QVector3D(4, 5, 6)));

        QJsonObject json = sg.toJson();
        QCOMPARE(json["count"].toInt(), 2);
        QCOMPARE(json["entities"].toArray().size(), 2);

        BIMSceneGraph sg2;
        sg2.fromJson(json);
        QCOMPARE(sg2.entityCount(), 2);
        QVERIFY(sg2.findEntity("a") != nullptr);
        QVERIFY(sg2.findEntity("b") != nullptr);
        QCOMPARE(sg2.findEntity("a")->name(), "Name-A");
    }

    void testSceneInfo()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("a", "MEP.Chiller", "A", QVector3D(0, 0, 0)));
        sg.addEntity(makeEntity("b", "MEP.Chiller", "B", QVector3D(1, 0, 0)));
        sg.addEntity(makeEntity("c", "Structural.Column", "C", QVector3D(2, 0, 0)));

        QJsonObject info = sg.sceneInfo();
        QCOMPARE(info["total_entities"].toInt(), 3);
        QJsonObject types = info["types"].toObject();
        QCOMPARE(types["MEP.Chiller"].toInt(), 2);
        QCOMPARE(types["Structural.Column"].toInt(), 1);
    }

    void testRegisterEntity()
    {
        BIMSceneGraph sg;
        QVariantMap props;
        props["capacity_rt"] = 500;

        sg.registerEntity("chiller-A", "MEP.Chiller", "冰水主機-A",
                          QVector3D(48, 3, -5), QVector3D(6, 6, 4), props);
        QCOMPARE(sg.entityCount(), 1);
        auto *e = sg.findEntity("chiller-A");
        QVERIFY(e != nullptr);
        QCOMPARE(e->type(), "MEP.Chiller");
        QCOMPARE(e->name(), "冰水主機-A");
        QCOMPARE(e->properties()["capacity_rt"].toInt(), 500);
    }

    void testClear()
    {
        BIMSceneGraph sg;
        sg.addEntity(makeEntity("a", "T", "A", QVector3D()));
        sg.addEntity(makeEntity("b", "T", "B", QVector3D()));
        QCOMPARE(sg.entityCount(), 2);

        sg.clear();
        QCOMPARE(sg.entityCount(), 0);
    }
};

QTEST_MAIN(TestSceneGraph)
#include "test_scene_graph.moc"
