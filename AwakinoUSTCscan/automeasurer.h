#ifndef AUTOMEASURER_H
#define AUTOMEASURER_H

#include <QObject>
#include "ustcscanmonitor.h"

class AutoMeasurer:public QObject
{
    Q_OBJECT
public:
    AutoMeasurer(USTCscanMonitor* USTCSM0);
public:
    USTCscanMonitor* USTCSM0;
};

#endif // AUTOMEASURER_H
