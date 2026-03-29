#include <QTest>
#include <QGuiApplication>
#include "BIMEntity.h"
#include "BIMSceneGraph.h"
#include "BIMEntityModel.h"
#include "SceneGraphModel.h"
#include "SpatialParser.h"

class TestEntityModel : public QObject
{
    Q_OBJECT

private slots:
    void testBIMEntityModelBasic()
    {
        BIMSceneGraph sg;
        BIMEntityModel model;
        model.setSceneGraph(&sg);

        QCOMPARE(model.count(), 0);
        QCOMPARE(model.rowCount(), 0);

        // Register entities
        sg.registerEntity("chiller-A", "MEP.Chiller", "Chiller-A",
                          QVector3D(10, 0, 0), QVector3D(6, 6, 4), {{"cost_ntd", 2800000}});
        sg.registerEntity("column-C1", "Structural.Column", "Column-C1",
                          QVector3D(0, 0, 0), QVector3D(0.8, 16, 0.8), {});

        QCOMPARE(model.count(), 2);
        QCOMPARE(model.rowCount(), 2);
    }

    void testBIMEntityModelFilter()
    {
        BIMSceneGraph sg;
        BIMEntityModel model;
        model.setSceneGraph(&sg);

        sg.registerEntity("chiller-A", "MEP.Chiller", "Chiller-A",
                          QVector3D(10, 0, 0), QVector3D(6, 6, 4), {});
        sg.registerEntity("chiller-B", "MEP.Chiller", "Chiller-B",
                          QVector3D(20, 0, 0), QVector3D(6, 6, 4), {});
        sg.registerEntity("column-C1", "Structural.Column", "Column-C1",
                          QVector3D(0, 0, 0), QVector3D(0.8, 16, 0.8), {});

        QCOMPARE(model.count(), 3);

        model.setFilterType("Chiller");
        QCOMPARE(model.count(), 2);

        model.setFilterType("Column");
        QCOMPARE(model.count(), 1);

        model.setFilterType("");
        QCOMPARE(model.count(), 3);
    }

    void testBIMEntityModelGetData()
    {
        BIMSceneGraph sg;
        BIMEntityModel model;
        model.setSceneGraph(&sg);

        sg.registerEntity("chiller-A", "MEP.Chiller", "Chiller-A",
                          QVector3D(48, 3, -5), QVector3D(6, 6, 4), {{"cost_ntd", 2800000}});

        QVariantMap data = model.get(0);
        QCOMPARE(data["id"].toString(), QString("chiller-A"));
        QCOMPARE(data["type"].toString(), QString("MEP.Chiller"));
        QCOMPARE(data["name"].toString(), QString("Chiller-A"));
    }

    void testSceneGraphModelTree()
    {
        BIMSceneGraph sg;
        SceneGraphModel model;
        model.setSceneGraph(&sg);

        sg.registerEntity("chiller-A", "MEP.Chiller", "Chiller-A",
                          QVector3D(10, 0, 0), QVector3D(6, 6, 4), {});
        sg.registerEntity("column-C1", "Structural.Column", "Column-C1",
                          QVector3D(0, 0, 0), QVector3D(0.8, 16, 0.8), {});

        // Root should have 2 category groups: MEP, Structural
        QCOMPARE(model.rowCount(), 2);

        // Each group should have 1 entity
        QModelIndex mepIndex = model.index(0, 0);
        QVERIFY(mepIndex.isValid());
        QCOMPARE(model.rowCount(mepIndex), 1);

        QModelIndex structIndex = model.index(1, 0);
        QVERIFY(structIndex.isValid());
        QCOMPARE(model.rowCount(structIndex), 1);
    }

    void testSpatialParserChinese()
    {
        SpatialParser parser;

        QVector3D right = parser.parseDirection("右側", 10.0);
        QCOMPARE(right.x(), 10.0f);
        QCOMPARE(right.y(), 0.0f);

        QVector3D left = parser.parseDirection("左側", 10.0);
        QCOMPARE(left.x(), -10.0f);

        QVector3D above = parser.parseDirection("上方", 5.0);
        QCOMPARE(above.y(), 5.0f);

        QVector3D beside = parser.parseDirection("旁邊", 8.0);
        QCOMPARE(beside.x(), 8.0f);
    }

    void testSpatialParserEnglish()
    {
        SpatialParser parser;

        QVector3D right = parser.parseDirection("right side", 10.0);
        QCOMPARE(right.x(), 10.0f);

        QVector3D left = parser.parseDirection("to the left", 10.0);
        QCOMPARE(left.x(), -10.0f);

        QVector3D above = parser.parseDirection("above", 5.0);
        QCOMPARE(above.y(), 5.0f);
    }

    void testSpatialParserComputeTarget()
    {
        SpatialParser parser;
        QVector3D ref(48, 3, -5);
        QVector3D target = parser.computeTarget(ref, "右側", 10.0);

        QCOMPARE(target.x(), 58.0f);
        QCOMPARE(target.y(), 3.0f);
        QCOMPARE(target.z(), -5.0f);
    }

    void testSpatialParserExtractDirection()
    {
        SpatialParser parser;

        QCOMPARE(parser.extractDirection("把冰水主機移到右側柱子旁邊"), QString("右側"));
        QCOMPARE(parser.extractDirection("move to the right"), QString("right"));
        QCOMPARE(parser.extractDirection("place above the chiller"), QString("above"));
    }
};

QTEST_MAIN(TestEntityModel)
#include "test_entity_model.moc"
