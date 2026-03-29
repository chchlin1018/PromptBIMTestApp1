#ifndef DEMOCONTROLLER_H
#define DEMOCONTROLLER_H

#include <QObject>
#include <QVector3D>
#include <QJsonObject>
#include <QJsonArray>
#include <QQmlEngine>
#include "BIMSceneGraph.h"
#include "SpatialParser.h"

class DemoController : public QObject
{
    Q_OBJECT
    QML_ELEMENT

    Q_PROPERTY(bool animating READ isAnimating NOTIFY animatingChanged)
    Q_PROPERTY(QString lastAction READ lastAction NOTIFY lastActionChanged)

public:
    explicit DemoController(QObject *parent = nullptr);

    void setSceneGraph(BIMSceneGraph *sg);
    void setSpatialParser(SpatialParser *sp);

    bool isAnimating() const;
    QString lastAction() const;

    // Move entity with full chain: move → clash check → cost delta
    Q_INVOKABLE QJsonObject moveEntity(const QString &entityId, const QVector3D &targetPos);

    // Move by NL direction: "把 chiller-A 移到 column-C3 右側"
    Q_INVOKABLE QJsonObject moveEntityNear(const QString &entityId, const QString &referenceId, const QString &direction);

    // Add entity from catalog
    Q_INVOKABLE QJsonObject addEntity(const QString &type, const QVector3D &position, const QString &name);

    // Delete entity
    Q_INVOKABLE QJsonObject deleteEntity(const QString &entityId);

    // Clash detection — bounding box overlap
    Q_INVOKABLE QJsonArray checkClash(const QString &entityId) const;

    // Cost delta — before/after comparison
    Q_INVOKABLE QJsonObject costDelta(double previousTotal) const;

    // Full scene cost summary
    Q_INVOKABLE QJsonObject sceneCostSummary() const;

    // Auto-arrange: find open position near existing entities of same type
    Q_INVOKABLE QVector3D autoArrangePosition(const QString &type) const;

    // Add entity with auto-arrange
    Q_INVOKABLE QJsonObject addEntityAutoArrange(const QString &type, const QString &name);

signals:
    void animatingChanged();
    void lastActionChanged();
    void entityMoved(const QString &id, const QVector3D &from, const QVector3D &to);
    void clashDetected(const QString &entityId, const QJsonArray &clashes);
    void costChanged(const QJsonObject &delta);
    void actionComplete(const QJsonObject &result);

private:
    bool isOverlapping(BIMEntity *a, BIMEntity *b) const;

    BIMSceneGraph *m_sceneGraph = nullptr;
    SpatialParser *m_spatialParser = nullptr;
    bool m_animating = false;
    QString m_lastAction;
    int m_nextEntityNum = 100;
};

#endif // DEMOCONTROLLER_H
