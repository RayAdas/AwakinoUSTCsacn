#include "osc.h"
#include <QDebug>
#include <QMessageBox>
#include <QCoreApplication>
#include "stdio.h"
#include <QDateTime>
#include <QFile>
#include "findunusedfilename.h"
#include <QDir>
#include <QThread>
OSC::OSC():
    isOpen(false)
    ,buf(new ViUInt8[1024*1024*100])
{
    // 获取上级目录
    QDir parentDir = QDir::current();
    parentDir.cdUp();
    //parentDir.cdUp();
    //parentDir.cdUp();
    // 将上级目录路径转换为QString
    QString parentDirPath = QDir::toNativeSeparators(parentDir.absolutePath());
    outputPath = parentDirPath + "\\OSCget";

    ViStatus status;
    // 创建资源管理器
    status = viOpenDefaultRM(&rm);
    if (status < VI_SUCCESS) {
        QMessageBox::critical(nullptr, "Fatal:", "Failed to open VISA resource manager.");
        // 退出程序
        QCoreApplication::exit(1);  // 非零值表示异常退出
    }
}
QList<OSCdevName> OSC::getDevList(){
    // 列出所有可用设备
    ViStatus status;
    ViFindList findList;
    ViUInt32 numInstrs;
    char resourceString[256];
    QList<OSCdevName> r;
    status = viFindRsrc(rm, (char*)"?*::INSTR", &findList, &numInstrs, resourceString);
    if (status < VI_SUCCESS) {
        qDebug() << "Failed to find devices.";
        viClose(rm);
        return r;
    }
    qDebug() << "Available device: " << resourceString;
    r.append(QString::fromUtf8(resourceString));
    return r;
}

bool OSC::open(OSCdevName devName){
    if(isOpen)
    {return true;}
    ViStatus status;
    // 打开设备
    QByteArray qba = devName.toLocal8Bit();
    char* devNameChar = qba.data();
    status = viOpen(rm, devNameChar, VI_NULL, VI_NULL, &scope);
    if (status < VI_SUCCESS) {
        qDebug() << "Failed to open device.";
        viClose(rm);
        return false;
    }
    isOpen = true;
    return true;
}
bool OSC::sendCommand(QString command){
    // 发送 SCPI 指令
    ViStatus status;
    QByteArray qba = command.toLocal8Bit();
    char* commandChar = qba.data();
    status = viWrite(scope, (ViBuf)commandChar, (ViUInt32)strlen(commandChar), VI_NULL);
    if (status < VI_SUCCESS) {
        qDebug() << "Failed to send command.";
        return false;
    }
    return true;
}

// bool OSC::init(){
    // this->sendCommand(":TRIGger:HOLDoff 0.010"); // 10ms触发释抑
    // 设置延迟时基偏移为 8μs, 设置主时基档位为 2μs
    // this->sendCommand(":TIMebase:MAIN:OFFSet 0.000008");
    // this->sendCommand(":TIMebase:MAIN:SCALe 0.000002");

    // this->sendCommand(":ACQ:SRATe?");
    // viSetAttribute(scope, VI_ATTR_TMO_VALUE, 5000);  // 超时设置为 5 秒
    // ViUInt32 retCnt;
    // ViStatus status;
    // status = viRead(scope, buf, 1024*1024*100, &retCnt);
    // std::string response(reinterpret_cast<const char*>(buf), retCnt);
    // // 去掉结尾的换行符
    // if (!response.empty() && response.back() == '\n') {
    //     response.pop_back();
    // }

    // 比对字符串
    // if (response != "5.000000E+8") {
    //     printf("Error: got unexpected samplerate.\n");
    // }
// }

QString OSC::saveWaveformData(){
    this->sendCommand(":WAVeform:SOUR CHAN1");//通道源1
    this->sendCommand(":WAVeform:MODE NORM");//波形读取模式普通
    this->sendCommand(":WAVeform:FORMat ASCII");//设置数据类型
    this->sendCommand(":SINGle");
    QThread::msleep(50);

    viSetAttribute(scope, VI_ATTR_TMO_VALUE, 5000);  // 超时设置为 5 秒
    ViUInt32 retCnt;
    ViStatus status;

    this->sendCommand(":WAV:DATA?");//读取数据
    status = viRead(scope, buf, 1024*1024*100, &retCnt);
    if (status == VI_SUCCESS) {
        printf("Readed.\n");
        // 获取当前时间并格式化为字符串
        QString timestamp = QDateTime::currentDateTime().toString("yyyyMMdd_hhmmss");
        QString baseFileName = outputPath + timestamp + ".txt";  // 基础文件名
        // 获取未被占用的文件名
        QString fileName = FindUnusedFileName::getAvailableFileName(baseFileName);
        // 打开文件
        QFile file(fileName);
        if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
            qWarning() << "无法打开文件:" << fileName;
            return "无法打开文件:" + fileName;
        }
        // 写入数据
        file.write(reinterpret_cast<const char*>(buf), std::strlen(reinterpret_cast<const char*>(buf)));
        file.close();  // 关闭文件
        return fileName;
    } else if (status == VI_ERROR_TMO) {
        printf("Timeout: No data available.\n");
        return "Timeout: No data available.";
    } else {
        printf("Error reading from device.\n");
        return "Error reading from device.";
    }

}

void OSC::close(){
    // 关闭连接
    viClose(scope);
    isOpen = false;
}

