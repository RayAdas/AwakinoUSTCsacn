#ifndef MOTOR_H
#define MOTOR_H
#include "COM.h"
enum AbsRela{relaPos = 0, absPos = 1};
struct MotorState{
    bool en;
    bool arrive;
    bool stuck;
    bool stuckProtect;
};

static QString id2QString(uint input)
{
    //转换为十六进制字符串
    QString hexString = QString::number(input, 16).toUpper(); // 使用大写形式的十六进制
    //检查位数，不足 6 位补 0
    while (hexString.length() < 6)
    {
        hexString.prepend("0");
    }
    return hexString;
}

class Motor
{
public:
    Motor(COM* COM0,uint CANID);
public:
    COM* COM0;
    void mMode(int 电流, bool 多机同步 = false, int 电流斜率 = 1000);
    void vMode(float 速度, bool 多机同步 = false, int 速度斜率 = 1000);

    //直通限速位置模式
    void pdMode(float pos, AbsRela ar, bool 多机同步 = false, float 最大速度 = 2000);
    //梯形曲线位置模式
    void ptMode(float pos, AbsRela ar, bool 多机同步 = false
                          , float 最大速度 = 2000, uint riseGrad = 1000, uint fallGrad = 1000);

    MotorState readMotorState();
    void setZero();
    void clearProtect();
    void stop(bool 多机同步 = false);
    void triggerHoming(bool 多机同步 = false);
    void clearStuck();
private:
    bool waitRespone(QString correctRespone, uint overTime = 5000);
    uint CANID;
};
#endif // MOTOR_H
