#include "findunusedfilename.h"
#include <QFile>
#include <QDir>

bool FindUnusedFileName::fileExists(const QString& path) {
    QFile file(path);
    QDir dir(path);
    return file.exists() || dir.exists(); // 同时判断文件和文件夹
}

// 获取未被占用的文件名
QString FindUnusedFileName::getAvailableFileName(const QString& baseFileName, const QString& fileExtension) {
    QString extension = fileExtension;
    if (extension.isEmpty()) {
        // 如果没有提供扩展名，则不添加扩展名
        extension = "";
    }
    else{
        // 确保扩展名以点开头
        extension = fileExtension.startsWith(".") ? fileExtension : "." + fileExtension;
    }

    QString fileName = baseFileName + extension;
    int index = 1;

    // 如果文件或文件夹存在，则递增索引
    while (fileExists(fileName)) {
        fileName = baseFileName + "_" + QString::number(index) + extension;
        index++;
    }

    return fileName;
}
