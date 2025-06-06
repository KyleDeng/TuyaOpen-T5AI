#!/usr/bin/env python3
# coding=utf-8

import os
import sys
import shutil

from tools.util import (
    get_system_name, do_subprocess
)


def _get_tuya_libs_flag(param_data):
    libs_dir = param_data["OPEN_LIBS_DIR"]
    flag_str = f"-L{libs_dir}"

    libs = param_data["PLATFORM_NEED_LIBS"]
    libs_list = libs.split()
    for lib in libs_list:
        flag_str += f" -l{lib}"

    return flag_str


def _compile_project_elf_src_c(gcc, assets_root, build_root):
    project_elf_src_c = os.path.join(assets_root, "project_elf_src.c")
    obj_file = os.path.join(build_root, "project_elf_src.c.obj")
    ld_flags_file = os.path.join(assets_root, "flags", "ld_flags.txt")

    cmd = f"{gcc} @{ld_flags_file}"
    cmd += f" -c {project_elf_src_c}"
    cmd += f" -o {obj_file}"

    ret = do_subprocess(cmd)

    if ret != 0:
        print("Error: _compile_project_elf_src_c.")
        return False
    return True


def _gen_elf(gcc, assets_root, build_root, target, tuya_libs_flag=""):
    assets_root = os.path.join(assets_root, f"{target}")
    build_root = os.path.join(build_root, f"{target}")

    if not _compile_project_elf_src_c(gcc, assets_root, build_root):
        return False
    ld_flags_file = os.path.join(assets_root, "flags", "ld_flags.txt")
    libs_dir = os.path.join(assets_root, "libs")
    libs_flags_file = os.path.join(assets_root, "flags", "libs_flags.txt")
    elf_file = os.path.join(build_root, "app.elf")
    elf_src_c_o = os.path.join(build_root, "project_elf_src.c.obj")
    ld_file = os.path.join(assets_root, "flags", f"{target}_out.ld")

    cmd = f"{gcc} @{ld_flags_file}"
    cmd += f" {elf_src_c_o}"
    cmd += " -fno-rtti -fno-lto"
    cmd += " -Wl,--start-group"
    cmd += f" -L{libs_dir} @{libs_flags_file}"
    if len(tuya_libs_flag):
        cmd += f" {tuya_libs_flag}"
    cmd += " -Wl,--end-group"
    cmd += f" -T {ld_file}"
    cmd += f" -o {elf_file}"

    ret = do_subprocess(cmd)
    if ret != 0:
        print("Error: _gen_elf.")
        return False

    if not os.path.exists(elf_file):
        print(f"Error: Not found {elf_file}.")
        return False

    return True


def gen_elf_file(gcc, target, assets_root, build_root, param_data):
    tuya_libs_flag = _get_tuya_libs_flag(param_data)

    # cp0
    if not _gen_elf(gcc, assets_root, build_root, f"{target}"):
        return False

    # cp1
    if not _gen_elf(gcc, assets_root, build_root, f"{target}_cp1",
                    tuya_libs_flag):
        return False
    return True


def _elf_2_bin(objcopy, target, build_root):
    build_root = os.path.join(build_root, target)
    elf_file = os.path.join(build_root, "app.elf")
    bin_file = os.path.join(build_root, "app.bin")

    cmd = f"{objcopy} -O binary {elf_file} {bin_file}"

    ret = do_subprocess(cmd)
    if ret != 0:
        print("Error: _elf_2_bin.")
        return False

    if not os.path.exists(bin_file):
        print(f"Error: Not found {bin_file}.")
        return False

    return True


def elf2bin(objcopy, target, build_root):
    # cp0
    if not _elf_2_bin(objcopy, target, build_root):
        return False

    # cp1
    if not _elf_2_bin(objcopy, f"{target}_cp1", build_root):
        return False
    return True


def copy_bin_file(build_root, target):
    from_app1_bin = os.path.join(build_root, f"{target}_cp1", "app.bin")
    to__app1_bin = os.path.join(build_root, f"{target}", "app1.bin")
    shutil.copy(from_app1_bin, to__app1_bin)
    return True


def _get_packager_tools(assets_root):
    packager_root = os.path.join(assets_root, "packager-tools")
    # "linux", "darwin_x86", "darwin_arm64", "windows"
    sys_name = get_system_name()

    if "linux" == sys_name:
        tool_gen_image = os.path.join(
            packager_root, "linux", "cmake_Gen_image")
        tool_encrypt_crc = os.path.join(
            packager_root, "linux", "cmake_encrypt_crc")
    elif "darwin_x86" == sys_name:
        tool_gen_image = os.path.join(
            packager_root, "mac", "x86_64", "cmake_Gen_image")
        tool_encrypt_crc = os.path.join(
            packager_root, "mac", "x86_64", "cmake_encrypt_crc")
    elif "darwin_arm64" == sys_name:
        tool_gen_image = os.path.join(
            packager_root, "mac", "arm64", "cmake_Gen_image")
        tool_encrypt_crc = os.path.join(
            packager_root, "mac", "arm64", "cmake_encrypt_crc")
    else:
        tool_gen_image = os.path.join(
            packager_root, "windows", "cmake_Gen_image.exe")
        tool_encrypt_crc = os.path.join(
            packager_root, "windows", "cmake_encrypt_crc.exe")

    return tool_gen_image, tool_encrypt_crc


def gen_app_all_bin(root, build_root, target, assets_root):
    build_root = os.path.join(build_root, target)
    partitions_file = os.path.join(
        assets_root, target, "flags", "configuration.json")
    bootload_bin = os.path.join(
        root, "t5_os", "bk_idk", "components", "bk_libs",
        "bk7258", "bootloader", "normal_bootloader",
        "bootloader.bin")
    app_bin = os.path.join(build_root, "app.bin")
    app1_bin = os.path.join(build_root, "app1.bin")
    app_all_bin = os.path.join(build_root, "app-all.bin")

    tool_gen_image, tool_encrypt_crc = _get_packager_tools(assets_root)

    cmd = f"{tool_gen_image} genfile -injsonfile {partitions_file}"
    cmd += f" -infile {bootload_bin} {app_bin} {app1_bin}"
    cmd += f" -outfile {app_all_bin}"

    ret = do_subprocess(cmd)
    if ret != 0:
        print("Error: gen app-all.bin")
        return False

    cmd = f"{tool_encrypt_crc} -crc {app_all_bin}"

    ret = do_subprocess(cmd)
    if ret != 0:
        print("Error: crc app-all.bin")
        return False

    return True


def do_with_assets(root, build_root, user_cmd,
                   target, param_data):
    build_root = os.path.join(build_root, "build")
    assets_root = os.path.join(root, "tools", "vendor-t5_for_open")
    open_root = param_data["OPEN_ROOT"]
    toolchain_root = os.path.join(open_root, "platform", "tools",
                                  "gcc-arm-none-eabi-10.3-2021.10",
                                  "bin")
    toolchain_prefix = "arm-none-eabi-"

    if "windows" == get_system_name():
        gcc = os.path.join(toolchain_root,
                           f"{toolchain_prefix}gcc.exe")
        objcopy = os.path.join(toolchain_root,
                               f"{toolchain_prefix}objcopy.exe")
    else:
        gcc = os.path.join(toolchain_root,
                           f"{toolchain_prefix}gcc")
        objcopy = os.path.join(toolchain_root,
                               f"{toolchain_prefix}objcopy")

    # gen elf: cp0 and cp1
    if not gen_elf_file(gcc, target, assets_root, build_root, param_data):
        sys.exit(1)

    # elf to bin: cp0 and cp1
    if not elf2bin(objcopy, target, build_root):
        sys.exit(1)

    copy_bin_file(build_root, target)

    # gen app-all.bin
    if not gen_app_all_bin(root, build_root, target, assets_root):
        sys.exit(1)

    pass
