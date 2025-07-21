#ifndef OSC_H
#define OSC_H

#include <QObject>
#include <vector>

#include "visa/visa.h"
#include "npy.hpp"

typedef QString OSCdevName;
class OSC:public QObject
{
    Q_OBJECT
public:
    OSC();
    bool open(OSCdevName devName);
    bool write(QString command);
    bool query(QString command);
    bool init(QString* sampleRate=nullptr, QString* head2trigger=nullptr);
    QString saveWaveformData();
    void close();
    bool getIsOpen(){return isOpen;};
    QList<OSCdevName> getDevList();
    QString outputPath;
    int theoreticalPointsNum = 1e4;

private:
    bool isOpen;
    ViSession rm, scope;

    // receive buffer
    ViUInt8 *buf;
    ViUInt32 retCnt;
    ViStatus status;
};

#endif // OSC_H
