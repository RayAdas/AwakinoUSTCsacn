#include "OSC.h"
#include <QDebug>
#include <QMessageBox>
#include <QCoreApplication>
#include "stdio.h"
#include <QDateTime>
#include <QFile>
#include "findunusedfilename.h"
#include <QDir>
#include <QThread>
#include <cstring>
#include <vector>
OSC::OSC():
    isOpen(false)
    ,buf(new ViUInt8[1024*1024*100]) //申请100MB缓冲区
{
    // 获取上级目录
    QDir parentDir = QDir::current();
    parentDir.cdUp();
    parentDir.cdUp();
    parentDir.cdUp();
    // 将上级目录路径转换为QString
    QString parentDirPath = QDir::toNativeSeparators(parentDir.absolutePath());
    outputPath = parentDirPath + "\\OSCget\\";

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
    viSetAttribute(scope, VI_ATTR_TMO_VALUE, 5000);  // 超时设置为 5 秒
    return true;
}

bool OSC::write(QString command){
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

bool OSC::query(QString command){
    this->write(command);
    status = viRead(scope, buf, 1024*1024*100, &retCnt);
    if (status < VI_SUCCESS) {
        qDebug() << "Failed to read " << command;
        return false;
    }
    return true;
}

bool OSC::init(QString* sampleRate, QString* head2trigger){
    /* sampleRate为采样率
     * head2trigger为采样序列的开头到触发位置的时间，等于SCALe*5-OFFSet
     */
    this->write(":TRIGger:HOLDoff 0.010"); // 10ms触发释抑
    // 设置延迟时基偏移为 8μs, 设置主时基档位为 2μs
    this->write(":TIMebase:MAIN:OFFSet 0.000008");
    this->write(":TIMebase:MAIN:SCALe 0.000002");
    theoreticalPointsNum = 1e4;
    if (head2trigger != nullptr)
    {*head2trigger = "0.000002";}

    if(!this->query(":ACQ:SRATe?"))
    {return false;}

    std::string response(reinterpret_cast<const char*>(buf), retCnt);
    // 去掉结尾的换行符
    if (!response.empty() && response.back() == '\n') {
        response.pop_back();
    }
    if (head2trigger != nullptr)
    {*sampleRate = QString::fromStdString(response);}
    // 比对字符串
    if (response == "5.000000E+8") {
        return true;
    } else {
        qDebug() << "Unexpected response:" << QString::fromStdString(response);
        return false;
    }
}

QString OSC::saveWaveformData(){
    // 配置波形输出格式
    this->write(":WAVeform:SOUR CHAN1");    // 选择通道1
    this->write(":WAVeform:FORMat WORD");   // 设置数据格式为WORD（16位二进制）
    this->write(":WAVeform:MODE RAW");      // RAW模式
    this->write(":WAV:STAR 1"); /*设置波形数据读取的起始点为第 1 个波形点*/
    this->write(":WAVeform:STOP 10000"); /*设置波形数据读取的终止点为第 10000 个波形点(最后一个点)*/
    this->write(":SINGle");

    // 等待采集完成（*OPC? 只返回 "1\n"）
    while (true) {
        if (!this->query("*OPC?")) {
            qDebug() << "Failed to query *OPC?";
            return "Failed to query *OPC?";
        }
        QString opcResult = QString::fromUtf8(reinterpret_cast<const char*>(buf), retCnt).trimmed();
        if (opcResult == "1") {
            break; // 采集完成
        }
        QThread::msleep(10);
    }

    QString triggerStatus;
    
    // 等待触发完成
    do{
        QThread::msleep(10);

        if (!this->query(":TRIGger:STATus?")) {
            qDebug() << "Failed to read trigger status.";
            return "Failed to read trigger status.";
        }
        triggerStatus = QString::fromUtf8(reinterpret_cast<const char*>(buf), retCnt);
    }while(!triggerStatus.startsWith("STOP"));

    // 获取波形参数
    this->query(":WAV:XINC?");
    double x_increment = QString::fromUtf8(reinterpret_cast<const char*>(buf), retCnt).trimmed().toDouble();

    this->query(":WAV:XOR?");
    double x_origin = QString::fromUtf8(reinterpret_cast<const char*>(buf), retCnt).trimmed().toDouble();
    
    this->query(":WAV:YINC?");
    double y_increment = QString::fromUtf8(reinterpret_cast<const char*>(buf), retCnt).trimmed().toDouble();
    
    this->query(":WAV:YOR?");
    double y_origin = QString::fromUtf8(reinterpret_cast<const char*>(buf), retCnt).trimmed().toDouble();
    
    this->query(":WAV:YREF?");
    double y_reference = QString::fromUtf8(reinterpret_cast<const char*>(buf), retCnt).trimmed().toDouble();

    // 读取波形数据
    this->query(":WAV:DATA?");

    // 解析数据，跳过示波器的 header
    // VISA协议通常数据格式：#<N><NNNNN><data>
    ViUInt8* data_start = buf;
    size_t data_length = retCnt;
    
    if (buf[0] == '#') {
        int N = buf[1] - '0';
        if (N > 0 && N <= 9) {
            std::string length_str(reinterpret_cast<const char*>(buf + 2), N);
            data_length = std::stoul(length_str);
            data_start = buf + 2 + N;
        }
    }
    
    // 将二进制数据转为16位无符号整数向量
    size_t num_points = data_length / 2;  // WORD格式，每个点2字节
    if (num_points != theoreticalPointsNum){
        return QString("Error, receive %1, instead of %2 points").arg(data_length, theoreticalPointsNum);
    }
    // std::cout<<"num_points"<<num_points<<std::endl;
    std::vector<uint16_t> raw_data(num_points);
    std::memcpy(raw_data.data(), data_start, data_length);
    
    // 转换为电压值
    std::vector<double> voltages(num_points);
    for (size_t i = 0; i < num_points; i++) {
        voltages[i] = (static_cast<double>(raw_data[i]) - y_reference) * y_increment + y_origin;
    }

    // 获取当前时间并格式化为字符串
    QString timestamp = QDateTime::currentDateTime().toString("yyyyMMdd_hhmmss");
    QString baseFileName = outputPath + timestamp;  // 基础文件名
    QString fileName = FindUnusedFileName::getAvailableFileName(baseFileName, ".npy");
    
    try {
        // 保存电压数据

        unsigned long voltage_shape[] = {static_cast<unsigned long>(num_points)};
        npy::SaveArrayAsNumpy(fileName.toStdString(), false, 1, voltage_shape, voltages);
        
        return fileName;
    } catch (const std::exception& e) {
        qDebug() << "Error saving numpy arrays:" << e.what();
        return QString("Error saving numpy arrays: %1").arg(e.what());
    }
}

void OSC::close(){
    // 关闭连接
    viClose(scope);
    isOpen = false;
}

