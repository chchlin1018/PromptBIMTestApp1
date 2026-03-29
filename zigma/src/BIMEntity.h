#ifndef BIMENTITY_H
#define BIMENTITY_H

#include <QObject>
#include <QVector3D>
#include <QVariantMap>
#include <QStringList>
#include <QJsonObject>
#include <QQmlEngine>

class BIMEntity : public QObject
{
    Q_OBJECT
    QML_ELEMENT

    Q_PROPERTY(QString entityId READ entityId WRITE setEntityId NOTIFY entityIdChanged)
    Q_PROPERTY(QString type READ type WRITE setType NOTIFY typeChanged)
    Q_PROPERTY(QString name READ name WRITE setName NOTIFY nameChanged)
    Q_PROPERTY(QVector3D position READ position WRITE setPosition NOTIFY positionChanged)
    Q_PROPERTY(QVector3D rotation READ rotation WRITE setRotation NOTIFY rotationChanged)
    Q_PROPERTY(QVector3D dimensions READ dimensions WRITE setDimensions NOTIFY dimensionsChanged)
    Q_PROPERTY(QVariantMap properties READ properties WRITE setProperties NOTIFY propertiesChanged)
    Q_PROPERTY(QStringList connections READ connections WRITE setConnections NOTIFY connectionsChanged)
    Q_PROPERTY(QString model3D READ model3D WRITE setModel3D NOTIFY model3DChanged)

public:
    explicit BIMEntity(QObject *parent = nullptr);
    ~BIMEntity() override = default;

    QString entityId() const;
    void setEntityId(const QString &id);

    QString type() const;
    void setType(const QString &type);

    QString name() const;
    void setName(const QString &name);

    QVector3D position() const;
    void setPosition(const QVector3D &pos);

    QVector3D rotation() const;
    void setRotation(const QVector3D &rot);

    QVector3D dimensions() const;
    void setDimensions(const QVector3D &dims);

    QVariantMap properties() const;
    void setProperties(const QVariantMap &props);

    QStringList connections() const;
    void setConnections(const QStringList &conns);

    QString model3D() const;
    void setModel3D(const QString &path);

    Q_INVOKABLE QJsonObject toJson() const;
    Q_INVOKABLE void fromJson(const QJsonObject &json);
    Q_INVOKABLE void addConnection(const QString &targetId);
    Q_INVOKABLE void removeConnection(const QString &targetId);
    Q_INVOKABLE double distanceTo(BIMEntity *other) const;

signals:
    void entityIdChanged();
    void typeChanged();
    void nameChanged();
    void positionChanged();
    void rotationChanged();
    void dimensionsChanged();
    void propertiesChanged();
    void connectionsChanged();
    void model3DChanged();

private:
    QString m_entityId;
    QString m_type;
    QString m_name;
    QVector3D m_position;
    QVector3D m_rotation;
    QVector3D m_dimensions;
    QVariantMap m_properties;
    QStringList m_connections;
    QString m_model3D;
};

#endif // BIMENTITY_H
