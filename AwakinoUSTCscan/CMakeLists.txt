cmake_minimum_required(VERSION 3.16)

project(AwakinoUSTCscan VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets SerialPort)

set(PROJECT_SOURCES
        main.cpp
        mainwindow.cpp
        mainwindow.h
        mainwindow.ui
)

qt_add_executable(AwakinoUSTCscan
    MANUAL_FINALIZATION
    ${PROJECT_SOURCES}
    visa/visa.h
    visa/visatype.h
    ustcscanmonitor.h ustcscanmonitor.cpp
    com.h com.cpp


    osc.h osc.cpp
    motor.h motor.cpp
    findunusedfilename.h findunusedfilename.cpp
)

target_link_libraries(AwakinoUSTCscan PRIVATE Qt6::Widgets Qt6::SerialPort ${CMAKE_SOURCE_DIR}/visa/visa64.lib)

# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.

set(BUNDLE_ID_OPTION MACOSX_BUNDLE_GUI_IDENTIFIER com.example.AwakinoUSTCscan)

set_target_properties(AwakinoUSTCscan PROPERTIES
    ${BUNDLE_ID_OPTION}
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

include(GNUInstallDirs)
install(TARGETS AwakinoUSTCscan
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_finalize_executable(AwakinoUSTCscan)
endif()
