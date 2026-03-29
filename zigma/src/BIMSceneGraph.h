#ifndef BIMSCENEGRAPH_H
#define BIMSCENEGRAPH_H

#include <QObject>
#include <QQmlEngine>
#include <QJsonObject>
#include <QJsonArray>
#include "BIMEntity.h"

class BIMSceneGraph : public QObject
{
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(int entityCount READ entityCount NOTIFY entityCountChanged)

public:
    explicit BIMSceneGraph(QObject *parent = nullptr);
    ~BIMSceneGraph() override = default;

    int entityCount() const;

    Q_INVOKABLE void addEntity(BIMEntity *entity);
    Q_INVOKABLE bool removeEntity(const QString &id);
    Q_INVOKABLE BIMEntity *findEntity(const QString &id) const;
    Q_INVOKABLE QVariantList queryByType(const QString &type) const;
    Q_INVOKABLE QVariantList queryByName(const QString &name) const;
    Q_INVOKABLE QVariantList nearbyEntities(const QString &id, double radius) const;
    Q_INVOKABLE QVariantList allEntities() const;

    Q_INVOKABLE bool moveEntity(const QString &id, const QVector3D &position);
    Q_INVOKABLE bool rotateEntity(const QString &id, const QVector3D &rotation);
    Q_INVOKABLE bool resizeEntity(const QString &id, const QVector3D &dimensions);
    Q_INVOKABLE bool connectEntities(const QString &fromId, const QString &toId);

    Q_INVOKABLE QJsonObject toJson() const;
    Q_INVOKABLE void fromJson(const QJsonObject &json);
    Q_INVOKABLE QJsonObject sceneInfo() const;
    Q_INVOKABLE void clear();
    Q_INVOKABLE void registerEntity(const QString &id, const QString &type, const QString &name,
                                     const QVector3D &position, const QVector3D &dimensions,
                                     const QVariantMap &properties);

signals:
    void entityCountChanged();
    void entityAdded(const QString &id);
    void entityRemoved(const QString &id);
    void entityMoved(const QString &id, const QVector3D &newPos);
    void entityRotated(const QString &id, const QVector3D &newRot);
    void entityResized(const QString &id, const QVector3D &newDims);

private:
    QMap<QString, BIMEntity*> m_entities;
};

#endif // BIMSCENEGRAPH_H
