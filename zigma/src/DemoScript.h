#ifndef DEMOSCRIPT_H
#define DEMOSCRIPT_H

#include <QObject>
#include <QJsonObject>
#include <QJsonArray>
#include <QTimer>
#include <QQmlEngine>
#include "DemoController.h"

struct DemoStep {
    QString userPrompt;    // NL command
    QString action;        // move/add/resize/generate
    QString entityId;
    QString referenceId;
    QString direction;
    QString type;
    QVector3D value;       // position or dimensions
};

class DemoScript : public QObject
{
    Q_OBJECT
    QML_ELEMENT

    Q_PROPERTY(int currentStep READ currentStep NOTIFY currentStepChanged)
    Q_PROPERTY(int totalSteps READ totalSteps CONSTANT)
    Q_PROPERTY(bool playing READ isPlaying NOTIFY playingChanged)
    Q_PROPERTY(QString currentPrompt READ currentPrompt NOTIFY currentStepChanged)

public:
    explicit DemoScript(QObject *parent = nullptr);

    void setDemoController(DemoController *ctrl);

    int currentStep() const;
    int totalSteps() const;
    bool isPlaying() const;
    QString currentPrompt() const;

    Q_INVOKABLE void start();         // Start auto-play
    Q_INVOKABLE void stop();          // Stop auto-play
    Q_INVOKABLE void reset();         // Reset to step 0
    Q_INVOKABLE void executeStep(int step);  // Execute specific step
    Q_INVOKABLE QJsonObject executeNL(const QString &text);  // Parse and execute NL command

    Q_INVOKABLE QJsonArray allSteps() const;

signals:
    void currentStepChanged();
    void playingChanged();
    void stepStarted(int step, const QString &prompt);
    void stepCompleted(int step, const QJsonObject &result);
    void scriptCompleted();
    void nlResult(const QString &input, const QJsonObject &result);

private slots:
    void playNext();

private:
    void initSteps();
    QJsonObject parseAndExecuteNL(const QString &text);

    DemoController *m_controller = nullptr;
    QList<DemoStep> m_steps;
    int m_currentStep = -1;
    bool m_playing = false;
    QTimer *m_autoTimer = nullptr;
};

#endif // DEMOSCRIPT_H
