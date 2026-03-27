#include "BIMSceneBuilder.h"
#include <QJsonDocument>

BIMSceneBuilder::BIMSceneBuilder(QObject *parent)
    : QObject(parent)
{
}

void BIMSceneBuilder::buildScene(const QJsonObject &modelData)
{
    clearScene();

    m_elements = modelData["elements"].toArray();
    if (modelData.contains("cost"))
        m_costData = modelData["cost"].toObject();
    if (modelData.contains("schedule"))
        m_scheduleData = modelData["schedule"].toObject();

    for (int i = 0; i < m_elements.size(); ++i) {
        emit elementAdded(i, m_elements[i].toObject());
    }

    emit elementCountChanged();
    emit elementsChanged();
    emit sceneReady();
}

void BIMSceneBuilder::clearScene()
{
    m_elements = QJsonArray();
    m_costData = QJsonObject();
    m_scheduleData = QJsonObject();
    emit elementCountChanged();
    emit elementsChanged();
}

QJsonObject BIMSceneBuilder::getElement(int index) const
{
    if (index >= 0 && index < m_elements.size())
        return m_elements[index].toObject();
    return {};
}

QJsonObject BIMSceneBuilder::getElementById(const QString &id) const
{
    for (const auto &elem : m_elements) {
        QJsonObject obj = elem.toObject();
        if (obj["id"].toString() == id)
            return obj;
    }
    return {};
}

QVariantList BIMSceneBuilder::elements() const
{
    QVariantList list;
    for (const auto &elem : m_elements) {
        list.append(elem.toObject().toVariantMap());
    }
    return list;
}
