#include <QtTest/QtTest>
#include <QJsonObject>
#include <QJsonArray>
#include "../src/BIMMaterialLibrary.h"
#include "../src/BIMSceneBuilder.h"

class TestBIMComponents : public QObject
{
    Q_OBJECT

private slots:
    void testMaterialLibraryConstruction()
    {
        BIMMaterialLibrary lib;
        QVERIFY(lib.baseColor("concrete").isValid());
    }

    void testConcreteMaterial()
    {
        BIMMaterialLibrary lib;
        QCOMPARE(lib.roughness("concrete"), 0.85f);
        QCOMPARE(lib.metalness("concrete"), 0.0f);
        QCOMPARE(lib.opacity("concrete"), 1.0f);
    }

    void testGlassMaterial()
    {
        BIMMaterialLibrary lib;
        QCOMPARE(lib.roughness("glass"), 0.05f);
        QCOMPARE(lib.opacity("glass"), 0.3f);
    }

    void testSteelMaterial()
    {
        BIMMaterialLibrary lib;
        QCOMPARE(lib.metalness("steel"), 0.9f);
    }

    void testWoodMaterial()
    {
        BIMMaterialLibrary lib;
        QCOMPARE(lib.roughness("wood"), 0.75f);
    }

    void testDefaultMaterial()
    {
        BIMMaterialLibrary lib;
        // Unknown type returns default
        QVERIFY(lib.baseColor("unknown").isValid());
    }

    void testSceneBuilderConstruction()
    {
        BIMSceneBuilder builder;
        QCOMPARE(builder.elementCount(), 0);
    }

    void testBuildSceneEmpty()
    {
        BIMSceneBuilder builder;
        QJsonObject modelData;
        modelData["elements"] = QJsonArray();
        builder.buildScene(modelData);
        QCOMPARE(builder.elementCount(), 0);
    }

    void testBuildSceneWithElements()
    {
        BIMSceneBuilder builder;
        QJsonArray elements;
        QJsonObject wall;
        wall["id"] = "wall_0";
        wall["type"] = "wall";
        wall["material"] = "concrete";
        elements.append(wall);

        QJsonObject col;
        col["id"] = "col_0";
        col["type"] = "column";
        col["material"] = "steel";
        elements.append(col);

        QJsonObject modelData;
        modelData["elements"] = elements;
        builder.buildScene(modelData);
        QCOMPARE(builder.elementCount(), 2);
    }

    void testClearScene()
    {
        BIMSceneBuilder builder;
        QJsonArray elements;
        QJsonObject wall;
        wall["id"] = "wall_0";
        elements.append(wall);
        QJsonObject modelData;
        modelData["elements"] = elements;
        builder.buildScene(modelData);
        QCOMPARE(builder.elementCount(), 1);

        builder.clearScene();
        QCOMPARE(builder.elementCount(), 0);
    }

    void testGetElementById()
    {
        BIMSceneBuilder builder;
        QJsonArray elements;
        QJsonObject wall;
        wall["id"] = "test_wall";
        wall["type"] = "wall";
        elements.append(wall);
        QJsonObject modelData;
        modelData["elements"] = elements;
        builder.buildScene(modelData);

        QJsonObject found = builder.getElementById("test_wall");
        QCOMPARE(found["type"].toString(), QString("wall"));

        QJsonObject notFound = builder.getElementById("nonexistent");
        QVERIFY(notFound.isEmpty());
    }
};

QTEST_MAIN(TestBIMComponents)
#include "test_bim_components.moc"
