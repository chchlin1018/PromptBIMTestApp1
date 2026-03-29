#include "BIMEntityModel.h"

BIMEntityModel::BIMEntityModel(QObject *parent)
    : QAbstractListModel(parent)
{
}

void BIMEntityModel::setSceneGraph(BIMSceneGraph *sg)
{
    if (m_sceneGraph == sg) return;

    if (m_sceneGraph) {
        disconnect(m_sceneGraph, nullptr, this, nullptr);
    }

    m_sceneGraph = sg;

    if (m_sceneGraph) {
        connect(m_sceneGraph, &BIMSceneGraph::entityAdded, this, &BIMEntityModel::onEntityAdded);
        connect(m_sceneGraph, &BIMSceneGraph::entityRemoved, this, &BIMEntityModel::onEntityRemoved);
        connect(m_sceneGraph, &BIMSceneGraph::entityCountChanged, this, &BIMEntityModel::rebuild);
    }

    rebuild();
}

int BIMEntityModel::rowCount(const QModelIndex &parent) const
{
    if (parent.isValid()) return 0;
    return m_filtered.size();
}

QVariant BIMEntityModel::data(const QModelIndex &index, int role) const
{
    if (!index.isValid() || index.row() < 0 || index.row() >= m_filtered.size())
        return {};

    BIMEntity *e = m_filtered.at(index.row());
    switch (role) {
    case EntityIdRole: return e->entityId();
    case TypeRole: return e->type();
    case NameRole: return e->name();
    case PositionRole: return QVariant::fromValue(e->position());
    case DimensionsRole: return QVariant::fromValue(e->dimensions());
    case CostRole: return e->properties().value("cost_ntd", 0);
    case EntityObjectRole: return QVariant::fromValue(e);
    default: return {};
    }
}

QHash<int, QByteArray> BIMEntityModel::roleNames() const
{
    return {
        {EntityIdRole, "entityId"},
        {TypeRole, "type"},
        {NameRole, "name"},
        {PositionRole, "position"},
        {DimensionsRole, "dimensions"},
        {CostRole, "cost"},
        {EntityObjectRole, "entityObject"}
    };
}

int BIMEntityModel::count() const { return m_filtered.size(); }

QString BIMEntityModel::filterType() const { return m_filterType; }

void BIMEntityModel::setFilterType(const QString &type)
{
    if (m_filterType == type) return;
    m_filterType = type;
    emit filterTypeChanged();
    applyFilter();
}

QVariantMap BIMEntityModel::get(int row) const
{
    if (row < 0 || row >= m_filtered.size()) return {};
    BIMEntity *e = m_filtered.at(row);
    QJsonObject json = e->toJson();
    return json.toVariantMap();
}

void BIMEntityModel::onEntityAdded(const QString &)
{
    applyFilter();
}

void BIMEntityModel::onEntityRemoved(const QString &)
{
    applyFilter();
}

void BIMEntityModel::rebuild()
{
    applyFilter();
}

void BIMEntityModel::applyFilter()
{
    beginResetModel();
    m_filtered.clear();

    if (m_sceneGraph) {
        QVariantList all = m_sceneGraph->allEntities();
        // Get actual entity pointers from scene graph
        for (const auto &v : all) {
            QJsonObject json = v.toJsonObject();
            QString id = json["id"].toString();
            BIMEntity *e = m_sceneGraph->findEntity(id);
            if (!e) continue;

            if (m_filterType.isEmpty() || e->type().contains(m_filterType, Qt::CaseInsensitive)) {
                m_filtered.append(e);
            }
        }
    }

    endResetModel();
    emit countChanged();
}
