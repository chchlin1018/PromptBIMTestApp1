#include "BIMGeometryProvider.h"
#include <QJsonArray>
#include <QVector3D>
#include <cmath>

BIMGeometryProvider::BIMGeometryProvider(QQuick3DObject *parent)
    : QQuick3DGeometry(parent)
{
}

void BIMGeometryProvider::loadFromJSON(const QJsonObject &meshData)
{
    clear();

    QJsonArray vertices = meshData["vertices"].toArray();
    QJsonArray indices = meshData["indices"].toArray();

    m_vertexCount = vertices.size();
    m_triangleCount = indices.size();

    if (m_vertexCount == 0) return;

    // Stride: 3 floats position + 3 floats normal = 24 bytes
    const int stride = 6 * sizeof(float);
    QByteArray vertexData(m_vertexCount * stride, 0);
    float *vPtr = reinterpret_cast<float *>(vertexData.data());

    QVector3D minBounds(1e9f, 1e9f, 1e9f);
    QVector3D maxBounds(-1e9f, -1e9f, -1e9f);

    for (int i = 0; i < m_vertexCount; ++i) {
        QJsonArray v = vertices[i].toArray();
        float x = static_cast<float>(v[0].toDouble());
        float y = static_cast<float>(v[1].toDouble());
        float z = static_cast<float>(v[2].toDouble());
        vPtr[i * 6 + 0] = x;
        vPtr[i * 6 + 1] = y;
        vPtr[i * 6 + 2] = z;
        // normals initialized to 0, computed below
        minBounds = QVector3D(std::min(minBounds.x(), x), std::min(minBounds.y(), y), std::min(minBounds.z(), z));
        maxBounds = QVector3D(std::max(maxBounds.x(), x), std::max(maxBounds.y(), y), std::max(maxBounds.z(), z));
    }

    // Index buffer
    QByteArray indexData(m_triangleCount * 3 * sizeof(uint32_t), 0);
    uint32_t *iPtr = reinterpret_cast<uint32_t *>(indexData.data());
    for (int i = 0; i < m_triangleCount; ++i) {
        QJsonArray tri = indices[i].toArray();
        iPtr[i * 3 + 0] = static_cast<uint32_t>(tri[0].toInt());
        iPtr[i * 3 + 1] = static_cast<uint32_t>(tri[1].toInt());
        iPtr[i * 3 + 2] = static_cast<uint32_t>(tri[2].toInt());
    }

    computeNormals(vertexData, indexData, m_vertexCount);

    setStride(stride);
    setVertexData(vertexData);
    setIndexData(indexData);
    setBounds(minBounds, maxBounds);

    setPrimitiveType(QQuick3DGeometry::PrimitiveType::Triangles);
    addAttribute(QQuick3DGeometry::Attribute::PositionSemantic, 0, QQuick3DGeometry::Attribute::F32Type);
    addAttribute(QQuick3DGeometry::Attribute::NormalSemantic, 3 * sizeof(float), QQuick3DGeometry::Attribute::F32Type);
    addAttribute(QQuick3DGeometry::Attribute::IndexSemantic, 0, QQuick3DGeometry::Attribute::U32Type);

    update();
}

void BIMGeometryProvider::computeNormals(QByteArray &vertexData, const QByteArray &indexData, int vertCount)
{
    float *vPtr = reinterpret_cast<float *>(vertexData.data());
    const uint32_t *iPtr = reinterpret_cast<const uint32_t *>(indexData.constData());
    int triCount = indexData.size() / (3 * sizeof(uint32_t));

    // Accumulate face normals per vertex
    for (int t = 0; t < triCount; ++t) {
        uint32_t i0 = iPtr[t * 3 + 0];
        uint32_t i1 = iPtr[t * 3 + 1];
        uint32_t i2 = iPtr[t * 3 + 2];

        QVector3D v0(vPtr[i0 * 6], vPtr[i0 * 6 + 1], vPtr[i0 * 6 + 2]);
        QVector3D v1(vPtr[i1 * 6], vPtr[i1 * 6 + 1], vPtr[i1 * 6 + 2]);
        QVector3D v2(vPtr[i2 * 6], vPtr[i2 * 6 + 1], vPtr[i2 * 6 + 2]);

        QVector3D normal = QVector3D::crossProduct(v1 - v0, v2 - v0);

        for (uint32_t idx : {i0, i1, i2}) {
            vPtr[idx * 6 + 3] += normal.x();
            vPtr[idx * 6 + 4] += normal.y();
            vPtr[idx * 6 + 5] += normal.z();
        }
    }

    // Normalize
    for (int i = 0; i < vertCount; ++i) {
        QVector3D n(vPtr[i * 6 + 3], vPtr[i * 6 + 4], vPtr[i * 6 + 5]);
        n.normalize();
        vPtr[i * 6 + 3] = n.x();
        vPtr[i * 6 + 4] = n.y();
        vPtr[i * 6 + 5] = n.z();
    }
}
