#ifndef BIMGEOMETRYPROVIDER_H
#define BIMGEOMETRYPROVIDER_H

#include <QQuick3DGeometry>
#include <QJsonObject>
#include <QQmlEngine>

class BIMGeometryProvider : public QQuick3DGeometry
{
    Q_OBJECT
    QML_ELEMENT

public:
    explicit BIMGeometryProvider(QQuick3DObject *parent = nullptr);

    Q_INVOKABLE void loadFromJSON(const QJsonObject &meshData);
    Q_INVOKABLE int vertexCount() const { return m_vertexCount; }
    Q_INVOKABLE int triangleCount() const { return m_triangleCount; }

private:
    void computeNormals(QByteArray &vertexData, const QByteArray &indexData, int vertCount);
    int m_vertexCount = 0;
    int m_triangleCount = 0;
};

#endif // BIMGEOMETRYPROVIDER_H
