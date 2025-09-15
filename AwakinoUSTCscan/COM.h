#ifndef COM_H
#define COM_H
#include <QString>
#include <QList>
#include <QSerialPort>
#include <QEventLoop>
#include <QTimer>
#include <qregularexpression.h>

typedef QString PortName;

class COM:public QObject
{
    Q_OBJECT
public:
    COM();
    bool open(QString portName);
    qint64 write(QString data);
    QList<PortName> getPortNameList();
    bool getIsOpen();

public:
    QString lastReceived;

signals:
    void dataSent(QString data);
    void dataReaded(QString data);

private slots:
    void readData();

private:
    QSerialPort qsp;
    QString dataBuffer; // 用于存储不完整的数据包
};
class CompareWaiter:public QObject{
    Q_OBJECT
public:
    CompareWaiter(QRegularExpression pattern);
    static bool waitRespone(COM* com, QRegularExpression pattern, uint overTime = 1000);
private:
    const QRegularExpression pattern;
signals:
    void correctResponeGot(QString respone);
public slots:
    void compare(QString respone);
};

#endif // COM_H
