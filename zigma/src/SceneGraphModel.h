#ifndef SCENEGRAPHMODEL_H
#define SCENEGRAPHMODEL_H

#include <QAbstractItemModel>
#include <QQmlEngine>
#include "BIMSceneGraph.h"

struct TreeNode {
    QString id;
    QString type;      // "site", "building", "category", or entity type
    QString name;
    TreeNode *parent = nullptr;
    QList<TreeNode*> children;
    BIMEntity *entity = nullptr;  // null for group nodes

    ~TreeNode() { qDeleteAll(children); }
};

class SceneGraphModel : public QAbstractItemModel
{
    Q_OBJECT
    QML_ELEMENT

public:
    enum Roles {
        NodeIdRole = Qt::UserRole + 1,
        NodeTypeRole,
        NodeNameRole,
        IsGroupRole,
        EntityIdRole,
        ChildCountRole
    };

    explicit SceneGraphModel(QObject *parent = nullptr);
    ~SceneGraphModel() override;

    void setSceneGraph(BIMSceneGraph *sg);

    QModelIndex index(int row, int column, const QModelIndex &parent = QModelIndex()) const override;
    QModelIndex parent(const QModelIndex &child) const override;
    int rowCount(const QModelIndex &parent = QModelIndex()) const override;
    int columnCount(const QModelIndex &parent = QModelIndex()) const override;
    QVariant data(const QModelIndex &index, int role) const override;
    QHash<int, QByteArray> roleNames() const override;

    Q_INVOKABLE void rebuild();

private:
    void buildTree();
    TreeNode *findOrCreateGroup(TreeNode *parent, const QString &id, const QString &name);

    BIMSceneGraph *m_sceneGraph = nullptr;
    TreeNode *m_root = nullptr;
};

#endif // SCENEGRAPHMODEL_H
