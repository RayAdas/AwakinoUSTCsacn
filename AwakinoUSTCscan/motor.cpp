#include "motor.h"
#include <QEventLoop>
#include <QTimer>

Motor::Motor(COM* COM0, uint CANID):
    COM0(COM0),
    CANID(CANID)
{}

void Motor::mMode(int 电流, bool 多机同步, int 电流斜率){
    QString s_frame_type = "T";
    QString s_id = id2QString(this->CANID);
    QString s_idx = "00";
    QString s_dlcLen = "8";
    QString s_cmd = "F5";

    QString s_sign;
    s_sign = 电流 < 0 ? "01" : "00";
    电流 = abs(电流);

    QString s_current = QString::number(电流, 16).toUpper();
    while (s_current.length() < 4)
    {s_current.prepend("0");}

    QString s_grad_current = QString::number(电流斜率, 16).toUpper();
    while (s_grad_current.length() < 4)
    {s_grad_current.prepend("0");}

    QString s_sync;
    s_sync = 多机同步 ? "01" : "00";
    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_sign
                       + s_grad_current + s_current + s_sync + s_ending + "\r";
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "003F5026B\r"));
    COM0->write(SLCANCMD);
    CompareWaiter::waitRespone(this->COM0, pattern);
}

void Motor::vMode(float 速度, bool 多机同步, int 速度斜率){
    QString s_frame_type = "T";
    QString s_id = id2QString(CANID);
    QString s_idx = "00";
    QString s_dlcLen = "8";
    QString s_cmd = "F6";
    QString s_sign;
    s_sign = 速度 < 0 ? "01" : "00";
    速度 = abs(速度);

    int v_int = trunc(速度*10);
    QString s_vel = QString::number(v_int, 16).toUpper();
    while (s_vel.length() < 4)
    {s_vel.prepend("0");}

    QString s_grad_vel = QString::number(速度斜率, 16).toUpper();
    while (s_grad_vel.length() < 4)
    {s_grad_vel.prepend("0");}

    QString s_sync;
    s_sync = 多机同步 ? "01" : "00";

    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd
                       + s_sign + s_grad_vel + s_vel + s_sync + s_ending + "\r";
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "003F6026B\r"));
    COM0->write(SLCANCMD);
    CompareWaiter::waitRespone(this->COM0, pattern);
}

void Motor::pdMode(float pos, AbsRela ar, bool 多机同步, float 最大速度){
    QString s_frame_type = "T";
    QString s_id = id2QString(CANID);
    QString s_idx = "00";
    QString s_dlcLen = "8";
    QString s_cmd = "FB";

    QString s_sign;
    s_sign = pos < 0 ? "01" : "00";
    pos = abs(pos);

    int v_int = trunc(最大速度*10);
    QString s_vel = QString::number(v_int, 16).toUpper();
    while (s_vel.length() < 4)
    {s_vel.prepend("0");}

    int pos_int = trunc(pos*10);
    QString s_pos = QString::number(pos_int, 16).toUpper();
    while (s_pos.length() < 8)
    {s_pos.prepend("0");}

    QString s_absrela;
    s_absrela = (ar == absPos) ? "01" : "00";

    QString s_sync;
    s_sync = 多机同步 ? "01" : "00";

    QString s_ending = "6B";

    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_sign + s_vel + s_pos + "\r";
    COM0->write(SLCANCMD);

    s_idx = "01";s_dlcLen = "4";
    SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_absrela + s_sync + s_ending + "\r";
    COM0->write(SLCANCMD);
}

void Motor::ptMode(float pos, AbsRela ar, bool 多机同步, float 最大速度, uint riseGrad, uint fallGrad){
    QString s_frame_type = "T";
    QString s_id = id2QString(CANID);
    QString s_idx = "00";
    QString s_dlcLen = "8";
    QString s_cmd = "FD";

    QString s_sign;
    s_sign = pos < 0 ? "01" : "00";
    pos = abs(pos);

    int v_int = trunc(最大速度*10);
    QString s_vel = QString::number(v_int, 16).toUpper();
    while (s_vel.length() < 4)
    {s_vel.prepend("0");}

    int pos_int = trunc(pos*10);
    QString s_pos = QString::number(pos_int, 16).toUpper();
    while (s_pos.length() < 8)
    {s_pos.prepend("0");}

    QString s_absrela;
    s_absrela = (ar == absPos) ? "01" : "00";

    QString s_sync;
    s_sync = 多机同步 ? "01" : "00";

    QString s_ending = "6B";

    QString s_riseGrad = QString::number(riseGrad, 16).toUpper();
    while (s_riseGrad.length() < 4)
    {s_riseGrad.prepend("0");}

    QString s_fallGrad = QString::number(fallGrad, 16).toUpper();
    while (s_fallGrad.length() < 4)
    {s_fallGrad.prepend("0");}

    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_sign + s_riseGrad + s_fallGrad + s_vel + "\r";
    COM0->write(SLCANCMD);

    s_idx = "01";s_dlcLen = "8";
    SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_pos + s_absrela + s_sync + s_ending + "\r";
    COM0->write(SLCANCMD);
}
MotorState Motor::readMotorState(){}
void Motor::setZero(){
    QString s_frame_type = "T";
    QString s_id = id2QString(CANID);
    QString s_idx = "00";
    QString s_dlcLen = "3";
    QString s_cmd = "0A6D";
    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_ending + "\r";
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "0030A026B\r"));
    COM0->write(SLCANCMD);
    CompareWaiter::waitRespone(this->COM0, pattern);
}
void Motor::clearProtect(){
    QString s_frame_type = "T";
    QString s_id = id2QString(CANID);
    QString s_idx = "00";
    QString s_dlcLen = "3";
    QString s_cmd = "0E52";
    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_ending + "\r";
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "0030E026B\r"));
    COM0->write(SLCANCMD);
    CompareWaiter::waitRespone(this->COM0, pattern);
}
void Motor::stop(bool 多机同步){
    QString s_frame_type = "T";
    QString s_id = id2QString(CANID);
    QString s_idx = "00";
    QString s_dlcLen = "4";
    QString s_cmd = "FE98";
    QString s_sync;
    s_sync = 多机同步 ? "01" : "00";
    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_sync + s_ending + "\r";
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "003FE026B\r"));
    COM0->write(SLCANCMD);
    CompareWaiter::waitRespone(this->COM0, pattern);
}
void Motor::triggerHoming(bool 多机同步){
    QString s_frame_type = "T";
    QString s_id = id2QString(CANID);
    QString s_idx = "00";
    QString s_dlcLen = "4";
    QString s_cmd = "9A02";
    QString s_sync;
    s_sync = 多机同步 ? "01" : "00";
    QString s_ending = "6B";
    QString SLCANCMD = s_frame_type + s_id + s_idx + s_dlcLen + s_cmd + s_sync + s_ending + "\r";
    QRegularExpression pattern(QRegularExpression::escape("T" + s_id + "0039A026B\r"));
    COM0->write(SLCANCMD);
    CompareWaiter::waitRespone(this->COM0, pattern);
}
