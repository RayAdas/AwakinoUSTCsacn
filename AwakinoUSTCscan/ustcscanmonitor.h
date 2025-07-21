#ifndef USTCSCANMONITOR_H
#define USTCSCANMONITOR_H
#include "OSC.h"
#include "motor.h"
#include "COM.h"

enum MotorName{MotorX=0, MotorY0=1, MotorY1=2, MotorZ=3};
class USTCscanMonitor:public QObject
{
    Q_OBJECT
public://function
    USTCscanMonitor();
    //explicit USTCscanMonitor(QObject *parent = nullptr);
    ~USTCscanMonitor();
    void syncStop();
    void goPos(float X, float Y, bool justRelease = false);//自动抬笔，到达后不落笔
    bool upZ(bool justRelease = false);
    void downZ();
    void homeXY();
    void homeZ();
    void drawRange(float x1, float x2, float y1, float y2);
    void autoMeasure(float fromX, float fromY, float toX, float toY, float intervalX, float intervalY);
    void cleatAllStuckProtect();
    void syncMove();
public://variable
    OSC OSC0;
    COM* COM0;
    Motor* Motors[4];
    const uint MotorName2CANIDMapping[4] = {1,2,3,4};
    const uint CANID2MotorNameMapping[5] = {9999,0,1,2,3};//你不该读到9999
    float Zup = 10, Zpressure = -800;
    float XMax = 550, YMax = 1100;

signals:
    void signal_motorPosUpdated(MotorName motorName, float pos);
    void signal_allMotorReach();
private:

    bool waitMotorReachD(MotorName motorName, uint overTime = 2000);
    bool waitMotorReachT(MotorName motorName, uint overTime = 2000);
    void askMotorPos();
private:
    float ratioX = 9, ratioY = 9;
    QTimer* timerToUpdatePos;
    QString patternPos = "T\\d{6}007360\\d[a-zA-Z0-9]{8}6B\\r";
    CompareWaiter monitorToUpdatePos = CompareWaiter(QRegularExpression(patternPos));
    uint motorCircle = 0;
    float posX = 0;
    float posY0 = 0;
    float posY1 = 0;
    float posZ = 0;
    float coderMask[4] = {-1,1,-1,1};
    uint syncCount;
    QString wavefilesPath = "C:\\Users\\Windy\\Desktop\\shit_monitor\\OSCget\\";;
private slots:
    void syncGotOne();
    void updatePos(QString data);

};

#endif // USTCSCANMONITOR_H
