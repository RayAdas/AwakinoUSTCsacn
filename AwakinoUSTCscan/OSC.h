#ifndef OSC_H
#define OSC_H

#include <QObject>

#include "visa/visa.h"

typedef QString OSCdevName;
class OSC:public QObject
{
    Q_OBJECT
public:
    OSC();
    bool open(OSCdevName devName);
    bool sendCommand(QString command);
    // bool init();
    QString saveWaveformData();
    void close();
    bool getIsOpen(){return isOpen;};
    QList<OSCdevName> getDevList();
    QString outputPath;

private:
    bool isOpen;
    ViSession rm, scope;
    ViUInt8 *buf;
};

#endif // OSC_H
