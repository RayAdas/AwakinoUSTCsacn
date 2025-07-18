#include "ustcscanmonitor.h"
#include <QDebug>
#include <QTimer>
#include <QEventLoop>
#include <qpoint.h>
#include <qdatetime.h>
#include <QThread>
#include "findunusedfilename.h"
#include <QDir>
#include <QSettings>

USTCscanMonitor::USTCscanMonitor():
    COM0(new COM()),
    timerToUpdatePos(new QTimer(this))
{
    Motors[MotorX] = new Motor(COM0,MotorName2CANIDMapping[MotorName::MotorX]);
    Motors[MotorY0] = new Motor(COM0,MotorName2CANIDMapping[MotorName::MotorY0]);
    Motors[MotorY1] = new Motor(COM0,MotorName2CANIDMapping[MotorName::MotorY1]);
    Motors[MotorZ] = new Motor(COM0,MotorName2CANIDMapping[MotorName::MotorZ]);
}

USTCscanMonitor::~USTCscanMonitor()
{
    for (int i = 0; i < 4; ++i) {
        if (Motors[i] != nullptr) {
            delete Motors[i];
            Motors[i] = nullptr;  // 避免悬空指针
        }
    }
    delete COM0;
}

void USTCscanMonitor::askMotorPos()
{
    if(!this->COM0->getIsOpen())//串口没开，不干活
    {return;}

    motorCircle = (motorCircle + 1) % 4;
    QString s_frame_type = "T";
    QString s_id = id2QString(MotorName2CANIDMapping[motorCircle]);
    QString s_idx = "00";
    QString s_dlcLen = "2";
    QString s_cmd = "36";
    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_ending + "\r";
    this->COM0->write(SLCANCMD);
}

bool USTCscanMonitor::waitMotorReachD(MotorName motorName, uint overTime){
    QString s_id = id2QString(MotorName2CANIDMapping[motorName]);
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "003FB9F6B\r"));
    return CompareWaiter::waitRespone(this->COM0, pattern, overTime);
}

bool USTCscanMonitor::waitMotorReachT(MotorName motorName, uint overTime){
    QString s_id = id2QString(MotorName2CANIDMapping[motorName]);
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "003FD9F6B\r"));
    return CompareWaiter::waitRespone(this->COM0, pattern, overTime);
}

void USTCscanMonitor::syncMove()
{
    QString s_frame_type = "T";
    QString s_id = id2QString(0);
    QString s_idx = "00";
    QString s_dlcLen = "3";
    QString s_cmd = "FF66";
    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_ending + "\r";
    this->COM0->write(SLCANCMD);

    QRegularExpression pattern(QRegularExpression("T\\d{6}003FD9F6B\\r"));

    QEventLoop loop;
    QTimer timer;
    CompareWaiter waiter(pattern);
    uint overTime = 5000;

    this->syncCount = 0;

    // 超时信号连接到事件循环退出
    timer.setSingleShot(true);
    QObject::connect(&timer, &QTimer::timeout, &loop, &QEventLoop::quit);

    // 目标信号连接到比对者
    QObject::connect(COM0, &COM::dataReaded, &waiter, &CompareWaiter::compare);

    // 比对者连接到计数器
    QObject::connect(&waiter, &CompareWaiter::correctResponeGot, this, &USTCscanMonitor::syncGotOne);

    QObject::connect(this, &USTCscanMonitor::signal_allMotorReach, &loop, &QEventLoop::quit);
    timer.start(overTime);
    loop.exec();//等三个电机都到位s
}

void USTCscanMonitor::syncStop(){
    for (int i = 0; i < 4; ++i) {
        if (Motors[i] != nullptr) {
            Motors[i]->stop(true);
        }
    }
    this->syncMove();
}

bool USTCscanMonitor::upZ(bool justRelease){
    if(justRelease)
    {
        Motors[MotorZ]->mMode(0, false);//假装抬笔
        return true;
    }
    else
    {
        Motors[MotorZ]->ptMode(this->Zup, AbsRela::absPos, false);//立即抬笔
        return waitMotorReachT(MotorZ, 1000);
    }


}

void USTCscanMonitor::downZ(){
    Motors[MotorZ]->mMode(this->Zpressure, false);//立即落笔
}

void USTCscanMonitor::goPos(float X, float Y, bool justRelease){
    if(X < 0 or Y < 0){
        qDebug()<<"只能在第一象限移动。";return;
    }
    else if(X > XMax or Y > YMax){
        qDebug()<<"超出范围上限。";return;
    }
    if(! upZ(justRelease))//抬笔失败
    {return;}
    Motors[MotorX]->ptMode(X*ratioX, AbsRela::absPos, true);
    Motors[MotorY0]->ptMode(Y*ratioY, AbsRela::absPos, true);
    Motors[MotorY1]->ptMode(Y*ratioY, AbsRela::absPos, true);
    QThread::msleep(100);
    syncMove();
}

void USTCscanMonitor::homeXY(){
    if(! upZ(false))//抬笔失败
    {return;}
    Motors[MotorX]->triggerHoming(true);
    Motors[MotorY0]->triggerHoming(true);
    Motors[MotorY1]->triggerHoming(true);
    syncMove();
}

void USTCscanMonitor::homeZ(){
    Motors[MotorZ]->triggerHoming(false);
}

void USTCscanMonitor::updatePos(QString data){
    //不知道能不能这么写
    bool ok;//并没有处理ok不ok，只是必须要有一个bool作为返回值
    MotorName motorName = (MotorName)CANID2MotorNameMapping[data.mid(1,6).toUInt(&ok, 16)];

    float sign;
    if(data[13] == "0")
    {sign = 1;}
    else
    {sign = -1;}
    QString abab = data.mid(14,8);
    uint unum = data.mid(14,8).toUInt(&ok, 16);
    float pos = sign * unum / 10.;
    switch(motorName){
    case MotorX:
        pos /= ratioX;
        pos *= coderMask[MotorX];
        this->posX = pos;
        break;
    case MotorY0:
        pos /= ratioY;
        pos *= coderMask[MotorY0];
        this->posY0 = pos;
        pos = (posY0 + posY1) / 2;
        break;
    case MotorY1:
        pos /= ratioY;
        pos *= coderMask[MotorY1];
        this->posY1 = pos;
        pos = (posY0 + posY1) / 2;
        break;
    case MotorZ:
        pos *= coderMask[MotorZ];
        this->posZ = pos;
        break;
    }

    emit signal_motorPosUpdated(motorName, pos);
}

void USTCscanMonitor::drawRange(float x1, float x2, float y1, float y2){
    if(!(x1 >= 0 && x1 <= XMax &&
          x2 >= 0 && x2 <= XMax &&
          y1 >= 0 && y1 <= YMax &&
          y2 >= 0 && y2 <= YMax))
    {qDebug()<<"超出范围。";return;}
    float points[4][2] = {{x1,y1},{x1,y2},{x2,y2},{x2,y1}};

    for(int i = 0; i < 4; i++){
        this->goPos(points[i][0], points[i][1]);
    }
}

void USTCscanMonitor::autoMeasure(float fromX, float fromY, float toX, float toY, float intervalX, float intervalY){
    if (intervalX < 0 || intervalY < 0) {//间隔必须为正数
        qDebug() << "Error: Interval values must be greater than 0.";
        return;
    }

    // 获取当前时间并格式化为字符串
    QString timestamp = QDateTime::currentDateTime().toString("yyyyMMdd_hhmmss");
    QString basePath = wavefilesPath + timestamp;  // 基础路径
    // 获取未被占用的路径名
    QString path = FindUnusedFileName::getAvailableFileName(basePath,"");
    // 创建本次采集文件夹
    QDir dir;
    if(!dir.mkdir(path))
    {qDebug()<<"创建文件夹失败"; return;}

    this->OSC0.outputPath = path + "\\";

    // 创建目录文件
    QSettings indexFile(path + "\\" + "index.ini", QSettings::IniFormat);

    // 确保扫描方向无论坐标顺序如何都能处理
    float minX = std::min(fromX, toX);
    float maxX = std::max(fromX, toX);
    float minY = std::min(fromY, toY);
    float maxY = std::max(fromY, toY);
    indexFile.setValue("Grid/minX", minX);
    indexFile.setValue("Grid/minY", minY);
    //具体的max范围将在后续根据间隔和min推断

    bool direction = true; // 用于控制 X 方向的 Z 字形
    int numX = static_cast<int>((maxX - minX) / intervalX) + 1; // X方向点数
    int numY = static_cast<int>((maxY - minY) / intervalY) + 1; // Y方向点数
    indexFile.setValue("Grid/maxX", minX+(numX-1)*intervalX);
    indexFile.setValue("Grid/maxY", minY+(numY-1)*intervalY);
    indexFile.setValue("Grid/numX", numX);
    indexFile.setValue("Grid/numY", numY);
    // OSC0.init();

    for (int j = 0; j < numY; ++j) {
        float y = minY + j * intervalY;
        if (direction) {
            for (int i = 0; i < numX; ++i) {
                float x = minX + i * intervalX;
                goPos(x, y, true);
                downZ();
                QThread::msleep(10);
                QString fn = OSC0.saveWaveformData();
                indexFile.setValue(QString::number(j) + "/" + QString::number(i), fn);
            }
        } else {
            for (int i = numX - 1; i >= 0; --i) {
                float x = minX + i * intervalX;
                goPos(x, y, true);
                downZ();
                QThread::msleep(10);
                QString fn = OSC0.saveWaveformData();
                indexFile.setValue(QString::number(j) + "/" + QString::number(i), fn);
            }
        }
        direction = !direction; // 反转方向
    }
}

void USTCscanMonitor::syncGotOne(){
    this->syncCount++;
    QString timestamp = QDateTime::currentDateTime().toString("hh:mm:ss.zzz");
    qDebug()<<"count["+timestamp+"]:"<<syncCount;
    if(syncCount >= 3)
    {emit signal_allMotorReach();}
}

void USTCscanMonitor::cleatAllStuckProtect(){
    for (int i = 0; i < 4; ++i) {
        if (Motors[i] != nullptr) {
            Motors[i]->clearProtect();
        }
    }
}
