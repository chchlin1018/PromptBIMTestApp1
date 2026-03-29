#ifndef BIMENTITYMODEL_H
#define BIMENTITYMODEL_H

#include <QAbstractListModel>
#include <QQmlEngine>
#include "BIMSceneGraph.h"

class BIMEntityModel : public QAbstractListModel
{
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(int count READ count NOTIFY countChanged)
    Q_PROPERTY(QString filterType READ filterType WRITE setFilterType NOTIFY filterTypeChanged)

public:
    enum Roles {
        EntityIdRole = Qt::UserRole + 1,
        TypeRole,
        NameRole,
        PositionRole,
        DimensionsRole,
        CostRole,
        EntityObjectRole
    };

    explicit BIMEntityModel(QObject *parent = nullptr);

    void setSceneGraph(BIMSceneGraph *sg);

    int rowCount(const QModelIndex &parent = QModelIndex()) const override;
    QVariant data(const QModelIndex &index, int role) const override;
    QHash<int, QByteArray> roleNames() const override;

    int count() const;
    QString filterType() const;
    void setFilterType(const QString &type);

    Q_INVOKABLE QVariantMap get(int row) const;

signals:
    void countChanged();
    void filterTypeChanged();

private slots:
    void onEntityAdded(const QString &id);
    void onEntityRemoved(const QString &id);
    void rebuild();

private:
    BIMSceneGraph *m_sceneGraph = nullptr;
    QString m_filterType;
    QList<BIMEntity*> m_filtered;

    void applyFilter();
};

#endif // BIMENTITYMODEL_H
