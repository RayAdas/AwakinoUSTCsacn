#include "mainwindow.h"

#include <QApplication>
#include "USTCscanMonitor.h"
#include <QStyleFactory>
#include <QThread>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    QApplication::setStyle(QStyleFactory::create("Fusion"));
    USTCscanMonitor USTCSM0;
    QThread* thread_USTCSM0;
    thread_USTCSM0 = new QThread;
    USTCSM0.moveToThread(thread_USTCSM0);
    //USTCSM0.COM0->moveToThread(thread_USTCSM0);
    USTCSM0.OSC0.moveToThread(thread_USTCSM0);
    thread_USTCSM0->start();
    MainWindow w(&USTCSM0);
    QObject::connect(USTCSM0.COM0, &COM::dataReaded, &w, &MainWindow::updateCOMMonitor_r);
    QObject::connect(USTCSM0.COM0, &COM::dataSent, &w, &MainWindow::updateCOMMonitor_s);
    QObject::connect(&USTCSM0, &USTCscanMonitor::signal_motorPosUpdated, &w, &MainWindow::updatePos);
    w.show();
    return a.exec();
}
