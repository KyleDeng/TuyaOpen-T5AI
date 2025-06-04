@echo off
setlocal enabledelayedexpansion

REM 参数
set "ARMINO_DIR=%1"
set "PROJECT_DIR=%2"
set "BUILD_DIR=%3"
set "BUILD_TARGET=%4"

set "ARMINO_TOOL=%ARMINO_DIR%\tools\build_tools\armino"
set "BUILD_TARGET_PREFIX=%BUILD_TARGET:~0,5%"

set "need_build_properties_lib=0"
set "need_build_soc=0"
set "need_clean=0"
set "need_doc=0"

REM 判断前缀
if "%BUILD_TARGET_PREFIX%"=="libbk" (
    set "ARMINO_SOC=%BUILD_TARGET:~3%"
    set "need_build_properties_lib=1"
    set "BUILD_DIR=build\properties_libs\%ARMINO_SOC%"
    set "PROJECT_DIR=projects\properties_libs"
    echo build armino %ARMINO_SOC% properties libs only
    set "LIB_HASH=NULL"
) else if "%BUILD_TARGET_PREFIX%"=="relbk" (
    set "ARMINO_SOC=%BUILD_TARGET:~3%"
    set "BUILD_DIR=build\%BUILD_DIR%\%ARMINO_SOC%"
    set "need_build_properties_lib=0"
    set "need_build_soc=1"
    echo build armino %ARMINO_SOC% only
    set "LIB_HASH=NULL"
) else if "%BUILD_TARGET_PREFIX%"=="clean" (
    set "ARMINO_SOC=%BUILD_TARGET:~5%"
    set "BUILD_DIR=build\%BUILD_DIR%\%ARMINO_SOC%"
    set "need_clean=1"
) else if "%BUILD_TARGET_PREFIX%"=="docbk" (
    set "ARMINO_SOC=%BUILD_TARGET:~3%"
    set "BUILD_DIR=build\%BUILD_DIR%\%ARMINO_SOC%"
    echo build armino %ARMINO_SOC% doc only
    set "need_doc=1"
) else (
    set "ARMINO_SOC=%BUILD_TARGET%"
    set "BUILD_DIR=%BUILD_DIR%\%ARMINO_SOC%"
    set "need_build_soc=1"
    REM 这里省略 has_properties_lib_src 检查，直接设为0
    set "need_build_properties_lib=0"
    set "LIB_HASH=NULL"
)

set "PROPERTIES_LIB_BUILD_DIR=%ARMINO_DIR%\build\properties_libs\%ARMINO_SOC%"
set "PROPERTIES_LIB_DIR=%PROPERTIES_PROJECT_DIR%"

REM 清理
if "%need_clean%"=="1" (
    echo remove %ARMINO_DIR%\components\bk_libs\%ARMINO_SOC%
    if exist "%ARMINO_DIR%\components\bk_libs\%ARMINO_SOC%" rmdir /S /Q "%ARMINO_DIR%\components\bk_libs\%ARMINO_SOC%"
    echo remove %ARMINO_DIR%\%BUILD_DIR%
    if exist "%ARMINO_DIR%\%BUILD_DIR%" rmdir /S /Q "%ARMINO_DIR%\%BUILD_DIR%"
    echo remove %PROPERTIES_LIB_BUILD_DIR%
    if exist "%PROPERTIES_LIB_BUILD_DIR%" rmdir /S /Q "%PROPERTIES_LIB_BUILD_DIR%"
    if exist "%ARMINO_DIR%\tools\build_tools\armino_doc.py" (
        python "%ARMINO_DIR%\tools\build_tools\armino_doc.py" clean %ARMINO_SOC%
    )
    exit /b 0
)

REM 文档
if "%need_doc%"=="1" (
    python "%ARMINO_TOOL%" -B ".\%BUILD_DIR%" -P ".\%PROJECT_DIR%" doc %ARMINO_SOC%
    exit /b 0
)

REM 构建 properties lib
if "%need_build_properties_lib%"=="1" (
    echo build properties lib for %ARMINO_SOC%
    if exist "%PROPERTIES_LIB_BUILD_DIR%\sdkconfig" rmdir /S /Q "%PROPERTIES_LIB_BUILD_DIR%\sdkconfig"
    python "%ARMINO_TOOL%" -B "%PROPERTIES_LIB_BUILD_DIR%" -P "%PROPERTIES_LIB_DIR%" set-target %ARMINO_SOC%
    python "%ARMINO_TOOL%" -B "%PROPERTIES_LIB_BUILD_DIR%" -P "%PROPERTIES_LIB_DIR%" build
    call "%ARMINO_DIR%\tools\build_tools\copy_internal_libs.bat" %ARMINO_SOC% %ARMINO_DIR% %PROPERTIES_LIB_BUILD_DIR% %PROJECT%
)

REM 构建 soc
if "%need_build_soc%"=="1" (
    if /I "%ARMINO_SOC%"=="bk7258" (
        echo build T5
    ) else if /I "%ARMINO_SOC%"=="bk7258_cp1" (
        echo build T5_CPU1
    ) else if /I "%ARMINO_SOC%"=="bk7258_cp2" (
        echo build T5_CPU2
    ) else (
        echo build %ARMINO_SOC%
    )
    if exist "%ARMINO_DIR%\%BUILD_DIR%\sdkconfig" rmdir /S /Q "%ARMINO_DIR%\%BUILD_DIR%\sdkconfig"
    set ARMINO_PATH=%ARMINO_DIR%
    python "%ARMINO_TOOL%" -B "%ARMINO_DIR%\%BUILD_DIR%" -P "%ARMINO_DIR%\%PROJECT_DIR%" set-target %ARMINO_SOC%
    python "%ARMINO_TOOL%" -B "%ARMINO_DIR%\%BUILD_DIR%" -P "%ARMINO_DIR%\%PROJECT_DIR%" build
    call "%ARMINO_DIR%\tools\build_tools\armino_as_lib.bat" %ARMINO_SOC% %ARMINO_DIR% "%ARMINO_DIR%\%BUILD_DIR%" %PROJECT%
)

endlocal