set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(toolchain_path "$ENV{TOOLCHAIN_DIR}")

if(WIN32)
    set(CMAKE_AR ${toolchain_path}/arm-none-eabi-ar.exe)
    set(CMAKE_C_COMPILER ${toolchain_path}/arm-none-eabi-gcc.exe)
    set(CMAKE_CXX_COMPILER ${toolchain_path}/arm-none-eabi-g++.exe)
    set(CMAKE_ASM_COMPILER ${toolchain_path}/arm-none-eabi-gcc.exe)
    set(armino_objcopy ${toolchain_path}/arm-none-eabi-objcopy.exe)
    set(armino_readelf ${toolchain_path}/arm-none-eabi-readelf.exe)
    set(armino_nm ${toolchain_path}/arm-none-eabi-nm.exe)
    set(armino_objdump ${toolchain_path}/arm-none-eabi-objdump.exe)
    set(armino_toolchain_size ${toolchain_path}/arm-none-eabi-size.exe)
else()
    set(CMAKE_AR ${toolchain_path}/arm-none-eabi-ar)
    set(CMAKE_C_COMPILER ${toolchain_path}/arm-none-eabi-gcc)
    set(CMAKE_CXX_COMPILER ${toolchain_path}/arm-none-eabi-g++)
    set(CMAKE_ASM_COMPILER ${toolchain_path}/arm-none-eabi-gcc)
    set(armino_objcopy ${toolchain_path}/arm-none-eabi-objcopy)
    set(armino_readelf ${toolchain_path}/arm-none-eabi-readelf)
    set(armino_nm ${toolchain_path}/arm-none-eabi-nm)
    set(armino_objdump ${toolchain_path}/arm-none-eabi-objdump)
    set(armino_toolchain_size ${toolchain_path}/arm-none-eabi-size)
endif()


#add the libs in toolchain
link_libraries(libm.a) #contian sin() cos() ...
link_libraries(libgcc.a) #contian __riscv_restore_2  __riscv_save_3 ...
link_libraries(libc.a)#contain memset() memcopy() ....
link_libraries(libnosys.a)#contain _write() ...

set(c_link_options "-mcpu=cortex-m33+nodsp -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mcmse")

set(CMAKE_C_FLAGS "${c_link_options} -DWIFI_BLE_COEXIST -DCONFIG_CMAKE=1 -DBK_MAC=1 -Wl,--gc-sections -nostdlib -Wl,-wrap,malloc  -Wl,-wrap,gettimeofday -Wl,-wrap,_malloc_r -Wl,-wrap,free -Wl,-wrap,_free_r -Wl,-wrap,zalloc -Wl,-wrap,calloc -Wl,-wrap,realloc  -Wl,-wrap,_realloc_r -Wl,-wrap,printf -Wl,-wrap,vsnprintf -Wl,-wrap,snprintf -Wl,-wrap,sprintf -Wl,-wrap,puts -Wl,-wrap,__assert_func")
# Modified by TUYA Start
set(CMAKE_CXX_FLAGS "${c_link_options} -DWIFI_BLE_COEXIST -DCONFIG_CMAKE=1 -DBK_MAC=1 -Wl,--gc-sections -nostdlib -Wl,-wrap,malloc -Wl,-wrap,_malloc_r -Wl,-wrap,free -Wl,-wrap,_free_r -Wl,-wrap,zalloc -Wl,-wrap,calloc -Wl,-wrap,realloc  -Wl,-wrap,_realloc_r -Wl,-wrap,printf -Wl,-wrap,vsnprintf -Wl,-wrap,snprintf -Wl,-wrap,sprintf -Wl,-wrap,puts -Wl,-wrap,__assert_func")
# Modified by TUYA End
