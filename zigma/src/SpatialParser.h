#ifndef SPATIALPARSER_H
#define SPATIALPARSER_H

#include <QObject>
#include <QVector3D>
#include <QQmlEngine>

class SpatialParser : public QObject
{
    Q_OBJECT
    QML_ELEMENT

public:
    explicit SpatialParser(QObject *parent = nullptr);

    // Parse natural language direction to position offset
    // e.g., "右側" → (+10, 0, 0), "旁邊" → (+8, 0, 0), "上方" → (0, +5, 0)
    Q_INVOKABLE QVector3D parseDirection(const QString &text, double defaultDistance = 8.0) const;

    // Compute target position: reference position + direction offset
    Q_INVOKABLE QVector3D computeTarget(const QVector3D &refPos, const QString &direction, double distance = 8.0) const;

    // Extract direction keywords from natural language text
    Q_INVOKABLE QString extractDirection(const QString &text) const;
};

#endif // SPATIALPARSER_H
