@echo off
setlocal enabledelayedexpansion

REM 参数
set "s_soc=%1"
set "s_armino_dir=%2"
set "s_armino_build_dir=%3"
set "s_project=%4"
set "s_bk_libs_dir=%s_armino_dir%\components\bk_libs"
set "s_matter_lib_dir=%s_armino_build_dir%\armino\matter_build\out\%s_soc%\lib"
set "s_armino_lib_dir=%s_armino_build_dir%\armino_as_lib"

REM === init_dir ===
if exist "%s_armino_lib_dir%\%s_soc%" rmdir /S /Q "%s_armino_lib_dir%\%s_soc%"
if not exist "%s_armino_lib_dir%" mkdir "%s_armino_lib_dir%"
if not exist "%s_armino_lib_dir%\%s_soc%" mkdir "%s_armino_lib_dir%\%s_soc%"
if not exist "%s_armino_lib_dir%\%s_soc%\config" mkdir "%s_armino_lib_dir%\%s_soc%\config"
if not exist "%s_armino_lib_dir%\%s_soc%\libs" mkdir "%s_armino_lib_dir%\%s_soc%\libs"

REM === generate_armino_as_lib ===

REM copy properties libs and sdkconfig.h
if exist "%s_bk_libs_dir%\%s_soc%\libs" (
    xcopy /E /Y /I "%s_bk_libs_dir%\%s_soc%\libs\*" "%s_armino_lib_dir%\%s_soc%\libs\"
)
if exist "%s_bk_libs_dir%\%s_soc%\config\sdkconfig.h" (
    copy /Y "%s_bk_libs_dir%\%s_soc%\config\sdkconfig.h" "%s_armino_lib_dir%\%s_soc%\config\sdkconfig.h.properties"
)

REM copy matter libs
if exist "%s_matter_lib_dir%" (
    for %%f in ("%s_matter_lib_dir%\*.a") do (
        if exist "%%f" copy /Y "%%f" "%s_armino_lib_dir%\%s_soc%\libs\"
    )
)

REM copy all other armino libs
if exist "%s_armino_build_dir%\armino" (
    for /D %%d in ("%s_armino_build_dir%\armino\*") do (
        if exist "%%d\*.a" (
            for %%f in ("%%d\*.a") do (
                copy /Y "%%f" "%s_armino_lib_dir%\%s_soc%\libs\"
            )
        )
    )
)

REM copy sdkconfig.h
if exist "%s_armino_build_dir%\config\sdkconfig.h" (
    copy /Y "%s_armino_build_dir%\config\sdkconfig.h" "%s_armino_lib_dir%\%s_soc%\config\"
)

REM copy global headers
if exist "%s_armino_dir%\include" (
    xcopy /E /Y /I "%s_armino_dir%\include" "%s_armino_lib_dir%\include"
)

echo Found all libs in %s_armino_lib_dir%

endlocal