#ifndef BIMSCENEBUILDER_H
#define BIMSCENEBUILDER_H

#include <QObject>
#include <QJsonObject>
#include <QJsonArray>
#include <QQmlEngine>
#include <QVariantList>

class BIMSceneBuilder : public QObject
{
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(int elementCount READ elementCount NOTIFY elementCountChanged)
    Q_PROPERTY(QVariantList elements READ elements NOTIFY elementsChanged)

public:
    explicit BIMSceneBuilder(QObject *parent = nullptr);

    Q_INVOKABLE void buildScene(const QJsonObject &modelData);
    Q_INVOKABLE void clearScene();
    Q_INVOKABLE QJsonObject getElement(int index) const;
    Q_INVOKABLE QJsonObject getElementById(const QString &id) const;

    int elementCount() const { return m_elements.size(); }
    QVariantList elements() const;

signals:
    void sceneReady();
    void elementCountChanged();
    void elementsChanged();
    void elementAdded(int index, const QJsonObject &element);

private:
    QJsonArray m_elements;
    QJsonObject m_costData;
    QJsonObject m_scheduleData;
};

#endif // BIMSCENEBUILDER_H
