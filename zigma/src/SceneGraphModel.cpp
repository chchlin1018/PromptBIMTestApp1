#include "SceneGraphModel.h"
#include "ZigmaLogger.h"

SceneGraphModel::SceneGraphModel(QObject *parent)
    : QAbstractItemModel(parent)
    , m_root(new TreeNode{"root", "root", "TSMC Fab Site", nullptr, {}, nullptr})
{
}

SceneGraphModel::~SceneGraphModel()
{
    delete m_root;
}

void SceneGraphModel::setSceneGraph(BIMSceneGraph *sg)
{
    if (m_sceneGraph == sg) return;

    if (m_sceneGraph)
        disconnect(m_sceneGraph, nullptr, this, nullptr);

    m_sceneGraph = sg;

    if (m_sceneGraph) {
        connect(m_sceneGraph, &BIMSceneGraph::entityCountChanged, this, &SceneGraphModel::rebuild);
    }

    rebuild();
}

void SceneGraphModel::rebuild()
{
    beginResetModel();
    qDeleteAll(m_root->children);
    m_root->children.clear();
    buildTree();
    endResetModel();
}

void SceneGraphModel::buildTree()
{
    if (!m_sceneGraph) return;

    // Create hierarchy: Site → Category groups → Entities
    // Categories: Building, MEP, Structural, Infrastructure
    QMap<QString, TreeNode*> categoryNodes;

    QVariantList all = m_sceneGraph->allEntities();
    for (const auto &v : all) {
        QJsonObject json = v.toJsonObject();
        QString id = json["id"].toString();
        BIMEntity *entity = m_sceneGraph->findEntity(id);
        if (!entity) continue;

        // Extract category from type (e.g., "MEP.Chiller" → "MEP")
        QString fullType = entity->type();
        QString category = fullType.section('.', 0, 0);
        if (category.isEmpty()) category = "Other";

        // Find or create category node
        TreeNode *catNode = findOrCreateGroup(m_root, category, category);

        // Create entity leaf node
        auto *leaf = new TreeNode{entity->entityId(), fullType, entity->name(), catNode, {}, entity};
        catNode->children.append(leaf);
    }
}

TreeNode *SceneGraphModel::findOrCreateGroup(TreeNode *parent, const QString &id, const QString &name)
{
    for (auto *child : parent->children) {
        if (child->id == id && !child->entity)
            return child;
    }
    auto *node = new TreeNode{id, "category", name, parent, {}, nullptr};
    parent->children.append(node);
    return node;
}

QModelIndex SceneGraphModel::index(int row, int column, const QModelIndex &parent) const
{
    if (column != 0) return {};

    TreeNode *parentNode = parent.isValid()
        ? static_cast<TreeNode*>(parent.internalPointer())
        : m_root;

    if (row < 0 || row >= parentNode->children.size())
        return {};

    return createIndex(row, 0, parentNode->children.at(row));
}

QModelIndex SceneGraphModel::parent(const QModelIndex &child) const
{
    if (!child.isValid()) return {};

    auto *node = static_cast<TreeNode*>(child.internalPointer());
    TreeNode *parentNode = node->parent;

    if (!parentNode || parentNode == m_root)
        return {};

    // Find parent's row in grandparent
    TreeNode *grandparent = parentNode->parent ? parentNode->parent : m_root;
    int row = grandparent->children.indexOf(parentNode);
    if (row < 0) return {};

    return createIndex(row, 0, parentNode);
}

int SceneGraphModel::rowCount(const QModelIndex &parent) const
{
    TreeNode *node = parent.isValid()
        ? static_cast<TreeNode*>(parent.internalPointer())
        : m_root;
    return node->children.size();
}

int SceneGraphModel::columnCount(const QModelIndex &) const
{
    return 1;
}

QVariant SceneGraphModel::data(const QModelIndex &index, int role) const
{
    if (!index.isValid()) return {};

    auto *node = static_cast<TreeNode*>(index.internalPointer());

    switch (role) {
    case Qt::DisplayRole:
    case NodeNameRole: return node->name;
    case NodeIdRole: return node->id;
    case NodeTypeRole: return node->type;
    case IsGroupRole: return node->entity == nullptr;
    case EntityIdRole: return node->entity ? node->entity->entityId() : QString();
    case ChildCountRole: return node->children.size();
    default: return {};
    }
}

QHash<int, QByteArray> SceneGraphModel::roleNames() const
{
    return {
        {NodeIdRole, "nodeId"},
        {NodeTypeRole, "nodeType"},
        {NodeNameRole, "nodeName"},
        {IsGroupRole, "isGroup"},
        {EntityIdRole, "entityId"},
        {ChildCountRole, "childCount"}
    };
}
