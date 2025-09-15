#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "ustcscanmonitor.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(USTCscanMonitor *USTCSM0 ,QWidget *parent = nullptr);
    ~MainWindow();

public slots:
    void updateOSCLinkState(bool linked);
    void updateCOMLinkState(bool linked);
    void updateCOMMonitor_r(QString data);
    void updateCOMMonitor_s(QString data);
    void updatePos(MotorName motorName, float pos);

private slots://由窗口发来的信号的处理槽
    void on_pushButton_scan_clicked();

    void on_pushButton_linkOSC_clicked();

    void on_pushButton_linkCOM_clicked();

    void on_lineEdit_mMode_returnPressed();

    void on_lineEdit_vMode_returnPressed();

    void on_lineEdit_pdMode_returnPressed();

    void on_lineEdit_ptMode_returnPressed();

    void on_pushButton_motorDebugStop_clicked();

    void on_pushButton_motorSetZero_clicked();

    void on_pushButton_motorBangZero_clicked();

    void on_pushButton_go_XY_clicked();

    void on_pushButton_stop_clicked();

    void on_lineEdit_X_Max_editingFinished();

    void on_lineEdit_Y_Max_editingFinished();

    void on_lineEdit_Zup_editingFinished();

    void on_lineEdit_Zpressure_editingFinished();

    void on_pushButton_go_Zup_clicked();

    void on_pushButton_go_Zdown_clicked();

    void on_pushButton_homeXY_clicked();

    void on_pushButton_homeZ_clicked();

    void on_lineEdit_X_samp_interval_editingFinished();

    void on_lineEdit_Y_samp_interval_editingFinished();

    void on_lineEdit_FromX_editingFinished();

    void on_lineEdit_ToX_editingFinished();

    void on_lineEdit_FromY_editingFinished();

    void on_lineEdit_ToY_editingFinished();

    void on_pushButton_DrawRange_clicked();

    void on_pushButton_clr_stuck_clicked();

    void on_pushButton_Start_clicked();

    void on_pushButton_clear_browser_clicked();

    void on_pushButton_select_wavefiles_path_clicked();

    void on_pushButton_OSCSave_clicked();

    void on_pushButton_clicked();

public:
    USTCscanMonitor* USTCSM0;
private:
    Ui::MainWindow *ui;

private:
    void updateThingsAboutSampPoints();
};
#endif // MAINWINDOW_H
