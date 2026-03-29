#include "BIMEntity.h"
#include <QJsonArray>
#include <QtMath>

BIMEntity::BIMEntity(QObject *parent)
    : QObject(parent)
{
}

QString BIMEntity::entityId() const { return m_entityId; }
void BIMEntity::setEntityId(const QString &id) {
    if (m_entityId != id) { m_entityId = id; emit entityIdChanged(); }
}

QString BIMEntity::type() const { return m_type; }
void BIMEntity::setType(const QString &type) {
    if (m_type != type) { m_type = type; emit typeChanged(); }
}

QString BIMEntity::name() const { return m_name; }
void BIMEntity::setName(const QString &name) {
    if (m_name != name) { m_name = name; emit nameChanged(); }
}

QVector3D BIMEntity::position() const { return m_position; }
void BIMEntity::setPosition(const QVector3D &pos) {
    if (m_position != pos) { m_position = pos; emit positionChanged(); }
}

QVector3D BIMEntity::rotation() const { return m_rotation; }
void BIMEntity::setRotation(const QVector3D &rot) {
    if (m_rotation != rot) { m_rotation = rot; emit rotationChanged(); }
}

QVector3D BIMEntity::dimensions() const { return m_dimensions; }
void BIMEntity::setDimensions(const QVector3D &dims) {
    if (m_dimensions != dims) { m_dimensions = dims; emit dimensionsChanged(); }
}

QVariantMap BIMEntity::properties() const { return m_properties; }
void BIMEntity::setProperties(const QVariantMap &props) {
    m_properties = props; emit propertiesChanged();
}

QStringList BIMEntity::connections() const { return m_connections; }
void BIMEntity::setConnections(const QStringList &conns) {
    if (m_connections != conns) { m_connections = conns; emit connectionsChanged(); }
}

QString BIMEntity::model3D() const { return m_model3D; }
void BIMEntity::setModel3D(const QString &path) {
    if (m_model3D != path) { m_model3D = path; emit model3DChanged(); }
}

QJsonObject BIMEntity::toJson() const
{
    QJsonObject obj;
    obj["id"] = m_entityId;
    obj["type"] = m_type;
    obj["name"] = m_name;
    obj["position"] = QJsonArray{m_position.x(), m_position.y(), m_position.z()};
    obj["rotation"] = QJsonArray{m_rotation.x(), m_rotation.y(), m_rotation.z()};
    obj["dimensions"] = QJsonArray{m_dimensions.x(), m_dimensions.y(), m_dimensions.z()};
    obj["model3D"] = m_model3D;

    // Properties
    QJsonObject propsObj;
    for (auto it = m_properties.constBegin(); it != m_properties.constEnd(); ++it)
        propsObj[it.key()] = QJsonValue::fromVariant(it.value());
    obj["properties"] = propsObj;

    // Connections
    QJsonArray connsArr;
    for (const auto &c : m_connections)
        connsArr.append(c);
    obj["connections"] = connsArr;

    return obj;
}

void BIMEntity::fromJson(const QJsonObject &json)
{
    setEntityId(json["id"].toString());
    setType(json["type"].toString());
    setName(json["name"].toString());
    setModel3D(json["model3D"].toString());

    if (json.contains("position")) {
        QJsonArray arr = json["position"].toArray();
        if (arr.size() >= 3)
            setPosition(QVector3D(arr[0].toDouble(), arr[1].toDouble(), arr[2].toDouble()));
    }
    if (json.contains("rotation")) {
        QJsonArray arr = json["rotation"].toArray();
        if (arr.size() >= 3)
            setRotation(QVector3D(arr[0].toDouble(), arr[1].toDouble(), arr[2].toDouble()));
    }
    if (json.contains("dimensions")) {
        QJsonArray arr = json["dimensions"].toArray();
        if (arr.size() >= 3)
            setDimensions(QVector3D(arr[0].toDouble(), arr[1].toDouble(), arr[2].toDouble()));
    }
    if (json.contains("properties")) {
        QJsonObject propsObj = json["properties"].toObject();
        QVariantMap map;
        for (auto it = propsObj.constBegin(); it != propsObj.constEnd(); ++it)
            map[it.key()] = it.value().toVariant();
        setProperties(map);
    }
    if (json.contains("connections")) {
        QJsonArray arr = json["connections"].toArray();
        QStringList list;
        for (const auto &v : arr)
            list.append(v.toString());
        setConnections(list);
    }
}

void BIMEntity::addConnection(const QString &targetId)
{
    if (!m_connections.contains(targetId)) {
        m_connections.append(targetId);
        emit connectionsChanged();
    }
}

void BIMEntity::removeConnection(const QString &targetId)
{
    if (m_connections.removeAll(targetId) > 0)
        emit connectionsChanged();
}

double BIMEntity::distanceTo(BIMEntity *other) const
{
    if (!other) return -1.0;
    return static_cast<double>(m_position.distanceToPoint(other->position()));
}
