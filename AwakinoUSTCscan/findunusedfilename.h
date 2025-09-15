#ifndef FINDUNUSEDFILENAME_H
#define FINDUNUSEDFILENAME_H
#include <QString>

class FindUnusedFileName
{
public:
    static bool fileExists(const QString& fileName);
    static QString getAvailableFileName(const QString& baseFileName, const QString& fileExtension);
};

#endif // FINDUNUSEDFILENAME_H
