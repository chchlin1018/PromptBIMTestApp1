#ifndef BIMMATERIALLIBRARY_H
#define BIMMATERIALLIBRARY_H

#include <QObject>
#include <QColor>
#include <QQmlEngine>

struct BIMMaterial {
    QColor baseColor;
    float roughness;
    float metalness;
    float opacity;
};

class BIMMaterialLibrary : public QObject
{
    Q_OBJECT
    QML_ELEMENT

public:
    explicit BIMMaterialLibrary(QObject *parent = nullptr);

    Q_INVOKABLE QColor baseColor(const QString &materialType) const;
    Q_INVOKABLE float roughness(const QString &materialType) const;
    Q_INVOKABLE float metalness(const QString &materialType) const;
    Q_INVOKABLE float opacity(const QString &materialType) const;

private:
    QHash<QString, BIMMaterial> m_materials;
};

#endif // BIMMATERIALLIBRARY_H
