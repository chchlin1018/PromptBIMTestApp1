#include "BIMSceneGraph.h"
#include "ZigmaLogger.h"
#include <QtMath>

BIMSceneGraph::BIMSceneGraph(QObject *parent)
    : QObject(parent)
{
}

int BIMSceneGraph::entityCount() const { return m_entities.size(); }

void BIMSceneGraph::addEntity(BIMEntity *entity)
{
    if (!entity || entity->entityId().isEmpty()) return;

    const QString id = entity->entityId();
    if (m_entities.contains(id)) {
        ZLOG_WARN("SceneGraph", QString("Entity %1 already exists, replacing").arg(id));
        m_entities[id]->deleteLater();
    }

    entity->setParent(this);
    m_entities[id] = entity;
    emit entityAdded(id);
    emit entityCountChanged();
    ZLOG_DEBUG("SceneGraph", QString("Added entity: %1 (%2)").arg(id, entity->name()));
}

bool BIMSceneGraph::removeEntity(const QString &id)
{
    auto it = m_entities.find(id);
    if (it == m_entities.end()) return false;

    (*it)->deleteLater();
    m_entities.erase(it);
    emit entityRemoved(id);
    emit entityCountChanged();
    return true;
}

BIMEntity *BIMSceneGraph::findEntity(const QString &id) const
{
    return m_entities.value(id, nullptr);
}

QVariantList BIMSceneGraph::queryByType(const QString &type) const
{
    QVariantList result;
    for (auto *e : m_entities) {
        if (e->type() == type || e->type().contains(type, Qt::CaseInsensitive))
            result.append(QVariant::fromValue(e->toJson()));
    }
    return result;
}

QVariantList BIMSceneGraph::queryByName(const QString &name) const
{
    QVariantList result;
    for (auto *e : m_entities) {
        if (e->name().contains(name, Qt::CaseInsensitive))
            result.append(QVariant::fromValue(e->toJson()));
    }
    return result;
}

QVariantList BIMSceneGraph::nearbyEntities(const QString &id, double radius) const
{
    QVariantList result;
    BIMEntity *center = findEntity(id);
    if (!center) return result;

    for (auto *e : m_entities) {
        if (e->entityId() == id) continue;
        double dist = center->distanceTo(e);
        if (dist >= 0 && dist <= radius) {
            QJsonObject obj = e->toJson();
            obj["distance"] = dist;
            result.append(QVariant::fromValue(obj));
        }
    }
    return result;
}

QVariantList BIMSceneGraph::allEntities() const
{
    QVariantList result;
    for (auto *e : m_entities)
        result.append(QVariant::fromValue(e->toJson()));
    return result;
}

bool BIMSceneGraph::moveEntity(const QString &id, const QVector3D &position)
{
    BIMEntity *e = findEntity(id);
    if (!e) return false;
    e->setPosition(position);
    emit entityMoved(id, position);
    ZLOG_INFO("SceneGraph", QString("Moved %1 to (%2,%3,%4)").arg(id)
        .arg(position.x()).arg(position.y()).arg(position.z()));
    return true;
}

bool BIMSceneGraph::rotateEntity(const QString &id, const QVector3D &rotation)
{
    BIMEntity *e = findEntity(id);
    if (!e) return false;
    e->setRotation(rotation);
    emit entityRotated(id, rotation);
    return true;
}

bool BIMSceneGraph::resizeEntity(const QString &id, const QVector3D &dimensions)
{
    BIMEntity *e = findEntity(id);
    if (!e) return false;
    e->setDimensions(dimensions);
    emit entityResized(id, dimensions);
    return true;
}

bool BIMSceneGraph::connectEntities(const QString &fromId, const QString &toId)
{
    BIMEntity *from = findEntity(fromId);
    BIMEntity *to = findEntity(toId);
    if (!from || !to) return false;
    from->addConnection(toId);
    to->addConnection(fromId);
    return true;
}

QJsonObject BIMSceneGraph::toJson() const
{
    QJsonObject obj;
    QJsonArray arr;
    for (auto *e : m_entities)
        arr.append(e->toJson());
    obj["entities"] = arr;
    obj["count"] = m_entities.size();
    return obj;
}

void BIMSceneGraph::fromJson(const QJsonObject &json)
{
    clear();
    QJsonArray arr = json["entities"].toArray();
    for (const auto &v : arr) {
        auto *entity = new BIMEntity(this);
        entity->fromJson(v.toObject());
        m_entities[entity->entityId()] = entity;
    }
    emit entityCountChanged();
}

QJsonObject BIMSceneGraph::sceneInfo() const
{
    QJsonObject info;
    info["total_entities"] = m_entities.size();

    QMap<QString, int> typeCounts;
    for (auto *e : m_entities)
        typeCounts[e->type()]++;

    QJsonObject types;
    for (auto it = typeCounts.constBegin(); it != typeCounts.constEnd(); ++it)
        types[it.key()] = it.value();
    info["types"] = types;

    QJsonArray entityList;
    for (auto *e : m_entities) {
        QJsonObject brief;
        brief["id"] = e->entityId();
        brief["type"] = e->type();
        brief["name"] = e->name();
        brief["position"] = QJsonArray{e->position().x(), e->position().y(), e->position().z()};
        entityList.append(brief);
    }
    info["entities"] = entityList;

    return info;
}

void BIMSceneGraph::clear()
{
    for (auto *e : m_entities)
        e->deleteLater();
    m_entities.clear();
    emit entityCountChanged();
}

void BIMSceneGraph::registerEntity(const QString &id, const QString &type, const QString &name,
                                    const QVector3D &position, const QVector3D &dimensions,
                                    const QVariantMap &properties)
{
    auto *entity = new BIMEntity(this);
    entity->setEntityId(id);
    entity->setType(type);
    entity->setName(name);
    entity->setPosition(position);
    entity->setDimensions(dimensions);
    entity->setProperties(properties);
    addEntity(entity);
}
