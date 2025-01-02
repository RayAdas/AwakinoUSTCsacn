#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <qdatetime.h>

MainWindow::MainWindow(USTCscanMonitor *USTCSM0, QWidget *parent)
    : USTCSM0(USTCSM0)
    , QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->textBrowser_COM->document()->setMaximumBlockCount (1000);
    QPalette pe;
    pe.setColor(QPalette::WindowText,Qt::red);
    this->ui->label_OSC->setPalette(pe);
    this->ui->label_COM->setPalette(pe);
    QString xmax = QString::number(this->USTCSM0->XMax);
    QString ymax = QString::number(this->USTCSM0->YMax);
    this->ui->lineEdit_X_Max->setText(xmax);
    this->ui->lineEdit_Y_Max->setText(ymax);
    updateThingsAboutSampPoints();
    this->ui->progressBar->setMinimum(0);
    this->ui->progressBar->setMaximum(1);
    this->ui->progressBar->setValue(0);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_pushButton_scan_clicked(){
    QList<QString> OSCList = this->USTCSM0->OSC0.getDevList();
    this->ui->comboBox_OSC->clear();
    this->ui->comboBox_OSC->addItems(OSCList);

    QList<QString> COMList = this->USTCSM0->COM0->getPortNameList();
    this->ui->comboBox_COM->clear();
    this->ui->comboBox_COM->addItems(COMList);
}

void MainWindow::on_pushButton_linkOSC_clicked(){
    QString devName = this->ui->comboBox_OSC->currentText();
    if(devName.isEmpty())
    {return;}

    if(!this->USTCSM0->OSC0.getIsOpen())
    {
        bool isSuccess = this->USTCSM0->OSC0.open(devName);
        this->updateOSCLinkState(isSuccess);
    }
}

void MainWindow::on_pushButton_linkCOM_clicked(){
    QString devName = this->ui->comboBox_COM->currentText();
    if(devName.isEmpty())
    {return;}

    if(!this->USTCSM0->COM0->getIsOpen())
    {
        //打开串口和CAN通道
        bool isSuccess = this->USTCSM0->COM0->open(devName);
        isSuccess &= (this->USTCSM0->COM0->write("S6\r") != -1);//设置CAN波特率为500 kbps
        isSuccess &= (this->USTCSM0->COM0->write("O\r") != -1);//打开CAN通道
        this->updateCOMLinkState(isSuccess);
    }
}

void MainWindow::updateOSCLinkState(bool linked){
    QPalette pe;
    QString text;
    if(linked)
    {
        pe.setColor(QPalette::WindowText,Qt::green);
        text = "断开";
        this->ui->pushButton_linkOSC->setEnabled(false);
    }
    else
    {
        pe.setColor(QPalette::WindowText,Qt::red);
        text = "连接";
        this->ui->pushButton_linkOSC->setEnabled(true);
    }
    this->ui->label_OSC->setPalette(pe);
    this->ui->pushButton_linkOSC->setText(text);
}

void MainWindow::updateCOMLinkState(bool linked){
    QPalette pe;
    QString text;
    if(linked)
    {
        pe.setColor(QPalette::WindowText,Qt::green);
        text = "断开";
        this->ui->pushButton_linkCOM->setEnabled(false);
    }
    else
    {
        pe.setColor(QPalette::WindowText,Qt::red);
        text = "连接";
        this->ui->pushButton_linkCOM->setEnabled(true);
    }
    this->ui->label_COM->setPalette(pe);
    this->ui->pushButton_linkCOM->setText(text);
}

void MainWindow::on_lineEdit_mMode_returnPressed()
{
    int m = this->ui->lineEdit_mMode->text().toInt();
    this->USTCSM0->Motors[this->ui->comboBox_selectMotor->currentIndex()]->mMode(m);
}


void MainWindow::on_lineEdit_vMode_returnPressed()
{
    float v = this->ui->lineEdit_vMode->text().toFloat();
    this->USTCSM0->Motors[this->ui->comboBox_selectMotor->currentIndex()]->vMode(v);
}

void MainWindow::on_lineEdit_pdMode_returnPressed()
{
    float p = this->ui->lineEdit_pdMode->text().toFloat();
    this->USTCSM0->Motors[this->ui->comboBox_selectMotor->currentIndex()]->pdMode(p,AbsRela::relaPos);
}

void MainWindow::on_lineEdit_ptMode_returnPressed()
{
    float p = this->ui->lineEdit_ptMode->text().toFloat();
    this->USTCSM0->Motors[this->ui->comboBox_selectMotor->currentIndex()]->ptMode(p,AbsRela::relaPos);
}


void MainWindow::on_pushButton_motorDebugStop_clicked()
{
    uint idx = this->ui->comboBox_selectMotor->currentIndex();
    this->USTCSM0->Motors[idx]->stop();
}

void MainWindow::on_pushButton_motorSetZero_clicked()
{
    this->USTCSM0->Motors[this->ui->comboBox_selectMotor->currentIndex()]->setZero();
}


void MainWindow::on_pushButton_motorBangZero_clicked()
{
    this->USTCSM0->Motors[this->ui->comboBox_selectMotor->currentIndex()]->triggerHoming();
}

void MainWindow::updateCOMMonitor_r(QString data){
    QString timestamp = QDateTime::currentDateTime().toString("hh:mm:ss.zzz");
    this->ui->textBrowser_COM->append("[" + timestamp + "]" + "r:" + data + "\n");
}

void MainWindow::updateCOMMonitor_s(QString data){
    QString timestamp = QDateTime::currentDateTime().toString("hh:mm:ss.zzz");
    this->ui->textBrowser_COM->append("[" + timestamp + "]" + "s:" + data + "\n");
}

void MainWindow::on_pushButton_go_XY_clicked()
{
    float X = this->ui->lineEdit_X->text().toFloat();
    float Y = this->ui->lineEdit_Y->text().toFloat();
    this->USTCSM0->goPos(X, Y);
}

void MainWindow::on_pushButton_stop_clicked()
{
    this->USTCSM0->syncStop();
}


void MainWindow::on_lineEdit_X_Max_editingFinished()
{
    this->USTCSM0->XMax = this->ui->lineEdit_X_Max->text().toFloat();
}

void MainWindow::on_lineEdit_Y_Max_editingFinished()
{
    this->USTCSM0->YMax = this->ui->lineEdit_Y_Max->text().toFloat();
}

void MainWindow::on_lineEdit_Zup_editingFinished()
{
    this->USTCSM0->Zup = this->ui->lineEdit_Zup->text().toFloat();
}

void MainWindow::on_lineEdit_Zpressure_editingFinished()
{
    this->USTCSM0->Zpressure = this->ui->lineEdit_Zpressure->text().toFloat();
}

void MainWindow::on_pushButton_go_Zup_clicked(){
    this->USTCSM0->upZ();
}

void MainWindow::on_pushButton_go_Zdown_clicked(){
    this->USTCSM0->downZ();
}

void MainWindow::on_pushButton_homeXY_clicked()
{
    this->USTCSM0->homeXY();
}

void MainWindow::on_pushButton_homeZ_clicked()
{
    this->USTCSM0->homeZ();
}

void MainWindow::updatePos(MotorName motorName, float pos){

    switch(motorName){
    case MotorX:
        this->ui->label_X->setText("X:" + QString::number(pos));
        break;
    case MotorY0:
    case MotorY1:
        this->ui->label_Y->setText("Y:" + QString::number(pos));
        break;
    case MotorZ:
        this->ui->label_Z->setText("Z:" + QString::number(pos));
        break;
    }
}
void MainWindow::updateThingsAboutSampPoints(){
    float x_s = this->ui->lineEdit_FromX->text().toFloat();
    float y_s = this->ui->lineEdit_FromY->text().toFloat();
    float x_e = this->ui->lineEdit_ToX->text().toFloat();
    float y_e = this->ui->lineEdit_ToY->text().toFloat();
    float x_interval = this->ui->lineEdit_X_samp_interval->text().toFloat();
    float y_interval = this->ui->lineEdit_Y_samp_interval->text().toFloat();
    int x_num = std::floor(std::abs(x_s - x_e) / x_interval);
    int y_num = std::floor(std::abs(y_s - y_e) / y_interval);
    int total = x_num * y_num;
    this->ui->label_X_sample_num->setText(QString::number(x_num));
    this->ui->label_Y_sample_num->setText(QString::number(y_num));
    this->ui->label_total_sample_num->setText(QString::number(total));
    this->ui->progressBar->setMaximum(total);
}

void MainWindow::on_lineEdit_X_samp_interval_editingFinished()
{
    updateThingsAboutSampPoints();
}


void MainWindow::on_lineEdit_Y_samp_interval_editingFinished()
{
    updateThingsAboutSampPoints();
}


void MainWindow::on_lineEdit_FromX_editingFinished()
{
    updateThingsAboutSampPoints();
}


void MainWindow::on_lineEdit_ToX_editingFinished()
{
    updateThingsAboutSampPoints();
}


void MainWindow::on_lineEdit_FromY_editingFinished()
{
    updateThingsAboutSampPoints();
}


void MainWindow::on_lineEdit_ToY_editingFinished()
{
    updateThingsAboutSampPoints();
}


void MainWindow::on_pushButton_DrawRange_clicked()
{
    float x1 = this->ui->lineEdit_FromX->text().toFloat();
    float y1 = this->ui->lineEdit_FromY->text().toFloat();
    float x2 = this->ui->lineEdit_ToX->text().toFloat();
    float y2 = this->ui->lineEdit_ToY->text().toFloat();
    this->USTCSM0->drawRange(x1,x2,y1,y2);
}


void MainWindow::on_pushButton_clr_stuck_clicked()
{
    this->USTCSM0->cleatAllStuckProtect();
}


void MainWindow::on_pushButton_Start_clicked()
{
    float x1 = this->ui->lineEdit_FromX->text().toFloat();
    float y1 = this->ui->lineEdit_FromY->text().toFloat();
    float x2 = this->ui->lineEdit_ToX->text().toFloat();
    float y2 = this->ui->lineEdit_ToY->text().toFloat();
    float xi = this->ui->lineEdit_X_samp_interval->text().toFloat();
    float yi = this->ui->lineEdit_Y_samp_interval->text().toFloat();
    this->USTCSM0->autoMeasure(x1,y1,x2,y2,xi,yi);
}


void MainWindow::on_pushButton_clear_browser_clicked()
{
    this->ui->textBrowser_COM->clear();
}


void MainWindow::on_pushButton_clicked()
{
    this->USTCSM0->Motors[MotorX]->ptMode(100,AbsRela::absPos);
    // this->USTCSM0->Motors[MotorX]->ptMode(100,AbsRela::absPos,true);
    // this->USTCSM0->syncMove();
}


void MainWindow::on_pushButton_2_clicked()
{
    this->USTCSM0->Motors[MotorX]->ptMode(300,AbsRela::absPos);
    // this->USTCSM0->Motors[MotorX]->ptMode(300,AbsRela::absPos,true);
    // this->USTCSM0->syncMove();
}



void MainWindow::on_pushButton_select_wavefiles_path_clicked()
{

}

