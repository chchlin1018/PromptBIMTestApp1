#include "BIMMaterialLibrary.h"
#include "ZigmaLogger.h"

BIMMaterialLibrary::BIMMaterialLibrary(QObject *parent)
    : QObject(parent)
{
    m_materials["concrete"] = {QColor::fromRgbF(0.6, 0.6, 0.6), 0.85f, 0.0f, 1.0f};
    m_materials["glass"]    = {QColor::fromRgbF(0.7, 0.85, 1.0), 0.05f, 0.0f, 0.3f};
    m_materials["steel"]    = {QColor::fromRgbF(0.8, 0.8, 0.82), 0.35f, 0.9f, 1.0f};
    m_materials["wood"]     = {QColor::fromRgbF(0.55, 0.35, 0.15), 0.75f, 0.0f, 1.0f};
    m_materials["default"]  = {QColor::fromRgbF(0.5, 0.5, 0.5), 0.5f, 0.0f, 1.0f};
}

QColor BIMMaterialLibrary::baseColor(const QString &materialType) const
{
    return m_materials.value(materialType, m_materials["default"]).baseColor;
}

float BIMMaterialLibrary::roughness(const QString &materialType) const
{
    return m_materials.value(materialType, m_materials["default"]).roughness;
}

float BIMMaterialLibrary::metalness(const QString &materialType) const
{
    return m_materials.value(materialType, m_materials["default"]).metalness;
}

float BIMMaterialLibrary::opacity(const QString &materialType) const
{
    return m_materials.value(materialType, m_materials["default"]).opacity;
}
