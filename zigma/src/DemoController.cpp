#include "DemoController.h"
#include "ZigmaLogger.h"
#include <QJsonDocument>
#include <QtMath>

DemoController::DemoController(QObject *parent)
    : QObject(parent)
{
}

void DemoController::setSceneGraph(BIMSceneGraph *sg) { m_sceneGraph = sg; }
void DemoController::setSpatialParser(SpatialParser *sp) { m_spatialParser = sp; }

bool DemoController::isAnimating() const { return m_animating; }
QString DemoController::lastAction() const { return m_lastAction; }

QJsonObject DemoController::moveEntity(const QString &entityId, const QVector3D &targetPos)
{
    QJsonObject result;
    result["action"] = "move";
    result["entity_id"] = entityId;

    if (!m_sceneGraph) {
        result["error"] = "No scene graph";
        return result;
    }

    BIMEntity *entity = m_sceneGraph->findEntity(entityId);
    if (!entity) {
        result["error"] = "Entity not found: " + entityId;
        return result;
    }

    // Record before state
    QVector3D fromPos = entity->position();
    double costBefore = m_sceneGraph->totalCost();

    // Execute move
    m_sceneGraph->moveEntity(entityId, targetPos);

    // Check clashes
    QJsonArray clashes = checkClash(entityId);

    // Calculate cost delta (pipe lengths may change)
    QJsonObject delta = costDelta(costBefore);

    // Build result
    result["success"] = true;
    result["from"] = QJsonArray{fromPos.x(), fromPos.y(), fromPos.z()};
    result["to"] = QJsonArray{targetPos.x(), targetPos.y(), targetPos.z()};
    result["distance"] = static_cast<double>(fromPos.distanceToPoint(targetPos));
    result["clashes"] = clashes;
    result["clash_count"] = clashes.size();
    result["cost_delta"] = delta;

    m_lastAction = QString("Moved %1 from (%2,%3,%4) to (%5,%6,%7)")
        .arg(entityId)
        .arg(fromPos.x(), 0, 'f', 1).arg(fromPos.y(), 0, 'f', 1).arg(fromPos.z(), 0, 'f', 1)
        .arg(targetPos.x(), 0, 'f', 1).arg(targetPos.y(), 0, 'f', 1).arg(targetPos.z(), 0, 'f', 1);
    emit lastActionChanged();

    emit entityMoved(entityId, fromPos, targetPos);
    if (!clashes.isEmpty())
        emit clashDetected(entityId, clashes);
    emit costChanged(delta);
    emit actionComplete(result);

    ZLOG_INFO("DemoCtrl", m_lastAction);
    return result;
}

QJsonObject DemoController::moveEntityNear(const QString &entityId, const QString &referenceId, const QString &direction)
{
    if (!m_sceneGraph || !m_spatialParser) {
        QJsonObject err;
        err["error"] = "Missing dependencies";
        return err;
    }

    BIMEntity *ref = m_sceneGraph->findEntity(referenceId);
    if (!ref) {
        QJsonObject err;
        err["error"] = "Reference entity not found: " + referenceId;
        return err;
    }

    QVector3D targetPos = m_spatialParser->computeTarget(ref->position(), direction, 8.0);
    return moveEntity(entityId, targetPos);
}

QJsonObject DemoController::addEntity(const QString &type, const QVector3D &position, const QString &name)
{
    QJsonObject result;
    result["action"] = "add";

    if (!m_sceneGraph) {
        result["error"] = "No scene graph";
        return result;
    }

    double costBefore = m_sceneGraph->totalCost();

    QString id = QString("%1-%2").arg(type.section('.', 1, 1).toLower()).arg(m_nextEntityNum++);
    QString displayName = name.isEmpty() ? id : name;

    // Default properties based on type
    QVariantMap props;
    if (type.contains("Chiller")) props["cost_ntd"] = 2800000;
    else if (type.contains("CoolingTower")) props["cost_ntd"] = 1200000;
    else if (type.contains("Compressor")) props["cost_ntd"] = 800000;
    else if (type.contains("ExhaustStack")) props["cost_ntd"] = 600000;
    else if (type.contains("Column")) props["cost_ntd"] = 150000;

    QVector3D dims(6, 6, 4); // default
    if (type.contains("CoolingTower")) dims = QVector3D(6, 12, 6);
    else if (type.contains("Compressor")) dims = QVector3D(3, 5, 3);
    else if (type.contains("Column")) dims = QVector3D(0.8, 16, 0.8);

    m_sceneGraph->registerEntity(id, type, displayName, position, dims, props);

    QJsonObject delta = costDelta(costBefore);

    result["success"] = true;
    result["entity_id"] = id;
    result["type"] = type;
    result["name"] = displayName;
    result["position"] = QJsonArray{position.x(), position.y(), position.z()};
    result["cost_delta"] = delta;

    m_lastAction = QString("Added %1 (%2) at (%3,%4,%5)")
        .arg(displayName, type)
        .arg(position.x(), 0, 'f', 1).arg(position.y(), 0, 'f', 1).arg(position.z(), 0, 'f', 1);
    emit lastActionChanged();
    emit costChanged(delta);
    emit actionComplete(result);

    ZLOG_INFO("DemoCtrl", m_lastAction);
    return result;
}

QJsonObject DemoController::deleteEntity(const QString &entityId)
{
    QJsonObject result;
    result["action"] = "delete";
    result["entity_id"] = entityId;

    if (!m_sceneGraph) {
        result["error"] = "No scene graph";
        return result;
    }

    double costBefore = m_sceneGraph->totalCost();

    BIMEntity *entity = m_sceneGraph->findEntity(entityId);
    if (!entity) {
        result["error"] = "Entity not found: " + entityId;
        return result;
    }

    QString name = entity->name();
    m_sceneGraph->removeEntity(entityId);

    QJsonObject delta = costDelta(costBefore);

    result["success"] = true;
    result["removed_name"] = name;
    result["cost_delta"] = delta;

    m_lastAction = QString("Deleted %1 (%2)").arg(name, entityId);
    emit lastActionChanged();
    emit costChanged(delta);
    emit actionComplete(result);

    ZLOG_INFO("DemoCtrl", m_lastAction);
    return result;
}

QJsonArray DemoController::checkClash(const QString &entityId) const
{
    QJsonArray clashes;
    if (!m_sceneGraph) return clashes;

    BIMEntity *target = m_sceneGraph->findEntity(entityId);
    if (!target) return clashes;

    QVariantList all = m_sceneGraph->allEntities();
    for (const auto &v : all) {
        QJsonObject json = v.toJsonObject();
        QString otherId = json["id"].toString();
        if (otherId == entityId) continue;

        BIMEntity *other = m_sceneGraph->findEntity(otherId);
        if (!other) continue;

        if (isOverlapping(target, other)) {
            QJsonObject clash;
            clash["entity_id"] = otherId;
            clash["entity_name"] = other->name();
            clash["distance"] = target->distanceTo(other);
            clashes.append(clash);
        }
    }

    return clashes;
}

bool DemoController::isOverlapping(BIMEntity *a, BIMEntity *b) const
{
    // Simple AABB overlap check
    QVector3D aMin = a->position() - a->dimensions() * 0.5f;
    QVector3D aMax = a->position() + a->dimensions() * 0.5f;
    QVector3D bMin = b->position() - b->dimensions() * 0.5f;
    QVector3D bMax = b->position() + b->dimensions() * 0.5f;

    return (aMin.x() <= bMax.x() && aMax.x() >= bMin.x()) &&
           (aMin.y() <= bMax.y() && aMax.y() >= bMin.y()) &&
           (aMin.z() <= bMax.z() && aMax.z() >= bMin.z());
}

QJsonObject DemoController::costDelta(double previousTotal) const
{
    QJsonObject delta;
    double currentTotal = m_sceneGraph ? m_sceneGraph->totalCost() : 0;
    delta["previous_total_ntd"] = previousTotal;
    delta["current_total_ntd"] = currentTotal;
    delta["delta_ntd"] = currentTotal - previousTotal;
    delta["delta_percent"] = previousTotal > 0 ? ((currentTotal - previousTotal) / previousTotal * 100.0) : 0;

    // Format for display
    QString sign = (currentTotal >= previousTotal) ? "+" : "";
    delta["display"] = QString("NT$ %1%2").arg(sign).arg(
        QString::number(currentTotal - previousTotal, 'f', 0));
    return delta;
}

QJsonObject DemoController::sceneCostSummary() const
{
    QJsonObject summary;
    if (!m_sceneGraph) return summary;

    double equipmentCost = m_sceneGraph->totalCost();
    double pipingCost = m_sceneGraph->totalPipeCost();

    summary["equipment_cost_ntd"] = equipmentCost;
    summary["piping_cost_ntd"] = pipingCost;
    summary["total_cost_ntd"] = equipmentCost + pipingCost;
    summary["entity_count"] = m_sceneGraph->entityCount();

    // Cost breakdown by type
    QJsonObject breakdown;
    QVariantList all = m_sceneGraph->allEntities();
    QMap<QString, double> typeCosts;
    for (const auto &v : all) {
        QJsonObject json = v.toJsonObject();
        QString type = json["type"].toString();
        double cost = 0;
        if (json.contains("properties")) {
            cost = json["properties"].toObject()["cost_ntd"].toDouble();
        }
        typeCosts[type] += cost;
    }
    for (auto it = typeCosts.constBegin(); it != typeCosts.constEnd(); ++it) {
        breakdown[it.key()] = it.value();
    }
    summary["breakdown"] = breakdown;

    return summary;
}
