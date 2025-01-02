#include "com.h"
#include <QCoreApplication>

#include <QSerialPortInfo>
#include <QDebug>
COM::COM() {
    connect(&qsp,&QSerialPort::readyRead,this,&COM::readData);
}

QList<PortName> COM::getPortNameList()
{
    QList<PortName> r;
    foreach (const QSerialPortInfo &info, QSerialPortInfo::availablePorts()) {
        qDebug() << "Port:" << info.portName() << "Description:" << info.description();
        r.append(info.portName());
    }
    return r;
}

bool COM::open(QString portName)
{
    qsp.setPortName(portName);
    qsp.setBaudRate(QSerialPort::Baud115200);
    qsp.setDataBits(QSerialPort::Data8);
    qsp.setParity(QSerialPort::NoParity);
    qsp.setStopBits(QSerialPort::OneStop);
    qsp.setFlowControl(QSerialPort::NoFlowControl);

    bool r =qsp.open(QIODevice::ReadWrite);
    if(r == false){
        qDebug() << "fail to open " << portName;
    }
    return r;
}
bool COM::getIsOpen(){
    bool r = qsp.isOpen();
    return r;
}
qint64 COM::write(QString data)
{
    emit dataSent(data);
    QByteArray qba = data.toLocal8Bit();
    char* cha = qba.data();
    return qsp.write(cha);
}

void COM::readData()
{
    const QByteArray byteData = qsp.readAll();
    QString data = QString::fromUtf8(byteData);
    lastReceived = data;
    //qDebug()<<"SerialPort get:"<<data;
    int start = 0;
    int index = 0;

    while ((index = data.indexOf('\r', start)) != -1) {
        // 将当前段落加上回车符分割保存
        emit dataReaded(data.mid(start, index - start + 1));
        start = index + 1; // 更新起始位置
    }
}

CompareWaiter::CompareWaiter(QRegularExpression pattern):
    pattern(pattern){}

void CompareWaiter::compare(QString respone){
    if(pattern.match(respone).hasMatch())
    {emit correctResponeGot(respone);}
}

bool CompareWaiter::waitRespone(COM* com, QRegularExpression pattern, uint overTime)
{
    QEventLoop loop;
    QTimer timer;
    CompareWaiter waiter(pattern);
    // 超时信号连接到事件循环退出
    timer.setSingleShot(true);
    QObject::connect(&timer, &QTimer::timeout, &loop, &QEventLoop::quit);

    // 目标信号连接到比对者
    QObject::connect(com, &COM::dataReaded, &waiter, &CompareWaiter::compare);

    // 比对者连接到事件循环退出
    QObject::connect(&waiter, &CompareWaiter::correctResponeGot, &loop, &QEventLoop::quit);

    timer.start(overTime);
    loop.exec();

    if(! timer.isActive()){return false;}//如果超时了
    return true;
}
