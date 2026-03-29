#include "SpatialParser.h"
#include <QRegularExpression>

SpatialParser::SpatialParser(QObject *parent)
    : QObject(parent)
{
}

QVector3D SpatialParser::parseDirection(const QString &text, double defaultDistance) const
{
    QString t = text.toLower().trimmed();
    float d = static_cast<float>(defaultDistance);

    // Chinese direction keywords
    if (t.contains("右") || t.contains("right"))
        return QVector3D(d, 0, 0);
    if (t.contains("左") || t.contains("left"))
        return QVector3D(-d, 0, 0);
    if (t.contains("前") || t.contains("front") || t.contains("north"))
        return QVector3D(0, 0, -d);
    if (t.contains("後") || t.contains("back") || t.contains("behind") || t.contains("south"))
        return QVector3D(0, 0, d);
    if (t.contains("上") || t.contains("above") || t.contains("top") || t.contains("up"))
        return QVector3D(0, d, 0);
    if (t.contains("下") || t.contains("below") || t.contains("bottom") || t.contains("down"))
        return QVector3D(0, -d, 0);
    if (t.contains("旁") || t.contains("beside") || t.contains("next") || t.contains("near"))
        return QVector3D(d, 0, 0);  // Default: to the right

    // No direction found — default to right side
    return QVector3D(d, 0, 0);
}

QVector3D SpatialParser::computeTarget(const QVector3D &refPos, const QString &direction, double distance) const
{
    QVector3D offset = parseDirection(direction, distance);
    return refPos + offset;
}

QString SpatialParser::extractDirection(const QString &text) const
{
    // Chinese patterns
    static const QRegularExpression zhPattern(
        "(右側|左側|前方|後方|上方|下方|旁邊|右邊|左邊|前面|後面|上面|下面)",
        QRegularExpression::UseUnicodePropertiesOption);

    auto match = zhPattern.match(text);
    if (match.hasMatch())
        return match.captured(1);

    // English patterns
    static const QRegularExpression enPattern(
        "\\b(right|left|front|back|behind|above|below|top|bottom|beside|next to|near)\\b",
        QRegularExpression::CaseInsensitiveOption);

    match = enPattern.match(text);
    if (match.hasMatch())
        return match.captured(1);

    return QString();
}
