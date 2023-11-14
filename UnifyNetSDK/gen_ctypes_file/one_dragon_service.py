# python调用clang-format.exe格式化C++代码
import re
import sys
from pathlib import Path

from UnifyNetSDK.gen_ctypes_file._3_replace.replace import delete_default_arguments_dahua, delete_default_arguments_haikang
from UnifyNetSDK.gen_ctypes_file.tools.clang_format.format import clangformat as _clangformat

curPyPath = Path(__file__).parent

notes = """
在进行脚本操作前我修改了两个源头文件内容
1.编码转换为UTF-8,因为clang-format不支持我这两个头文件的gb2312
2.在HK_NetSDK.h文件中14272行的LPBEHAVIOR_PRISON_MODE_TYPE前面添加一个*符号，很明显这是一个枚举指针，不过原作者忘了加了
"""


# clang格式化
def clangformat(fileName):
    print(f"clangformat {fileName} 开始")
    dh_org_headfile_path = str(curPyPath / "_1_original" / fileName)
    dh_fod_headfile_path = str(curPyPath / "_2_formatted" / fileName)
    _clangformat(dh_org_headfile_path, dh_fod_headfile_path, notes)
    print(f"clangformat结束 {fileName} ")


# 正则删除注释和空行
def delete_comment_and_emptyline(orgText):
    # 用正则删除三种注释
    # 1.多行注释 /* */                      2.单行注释 // 用了换行符 \        3.单行注释 //
    # (/*(.|\r\n|\n)*?\*/)        |        (//(.*\\\n)+.*)        |         (//.*)
    pattern = r"(/\*(.|\r\n|\n)*?\*/)|(\/\/(.*\\\n)+.*)|(\/\/.*)"
    processedText1 = re.sub(pattern, "", orgText, flags=re.M)
    # 正则删除所有空行
    pattern = "^\\s*(?=\r?$)\n"  # 这句是从网上“学习”来的，我也不知道怎么写的这么奇怪
    processedText2 = re.sub(pattern, "", processedText1, flags=re.M)
    return processedText2


# 删除注释和空行
def sanitizeText(fileName, copy2replaceDir: bool):
    """
    本函数是修改源文件的，如果copy2replaceDir为True还会将结果复制到_3_replace下
    """
    print(f"sanitizeText {fileName} 开始")
    input_headfile_path = str(curPyPath / "_2_formatted" / fileName)
    with open(input_headfile_path, "r", encoding="utf8") as fp:
        text = delete_comment_and_emptyline(fp.read())
    output_headfile_path = input_headfile_path
    with open(output_headfile_path, "w", encoding="utf8") as fp:
        fp.write(text)
    if copy2replaceDir is True:
        output_headfile_path = str(curPyPath / "_3_replace" / fileName)
        with open(output_headfile_path, "w", encoding="utf8") as fp:
            fp.write(text)
        print("相同内容已同时复制到在第三步文件夹中")  # 其实是又开了一个文件指针而不是shutil.copyfile()
        print(f"sanitizeText {fileName} 结束，注释已删除")


# 生成头文件的ctypes中间层

Log2FileTag = False


def generateCtypesWrapper_dahua(log2file: bool):
    print("generateCtypesWrapper_dahua开始")
    dahua_readyToGenCtypesWrapperFile = str((curPyPath / "_3_replace/DH_NetSDK.h").resolve())
    dahua_generatedCtypesWrapperFile = str((curPyPath / "_4_completed/DH_NetSDK.py").resolve())
    dahua_NetSdkDllFile = "Libs/win64/dhnetsdk.dll"
    print("指令列表为", [dahua_readyToGenCtypesWrapperFile, "-l", dahua_NetSdkDllFile, "-o", dahua_generatedCtypesWrapperFile])
    global Log2FileTag
    if Log2FileTag is True and log2file is True:  # 希望将错误报告输出到文件中，但是已经有一个头文件占用了Log2FileTag标识
        raise Exception("用log2file时，只能跑一个头文件，同时只能有一个错误报告能输出到文件中")
    elif Log2FileTag is False and log2file is True:  # 希望将错误报告输出到文件中，且Log2FileTag标识没有被占用
        Log2FileTag = True
        error_file = open('dahua_ctypesgen_log.txt', 'w')  # 解除注释就会使ctypesgen的错误报告输出到文件中，而不是stderr
        sys.stderr = error_file
        from UnifyNetSDK.gen_ctypes_file.tools.sub_ctypesgen.run import main as ctypesgenscript
        ctypesgenscript([dahua_readyToGenCtypesWrapperFile, "-l", dahua_NetSdkDllFile, "-o", dahua_generatedCtypesWrapperFile])
        error_file.close()
    elif Log2FileTag is False and log2file is False:  # 希望将错误报告输出到标准错误输出流中（默认就是终端）中
        from UnifyNetSDK.gen_ctypes_file.tools.sub_ctypesgen.run import main as ctypesgenscript
        ctypesgenscript([dahua_readyToGenCtypesWrapperFile, "-l", dahua_NetSdkDllFile, "-o", dahua_generatedCtypesWrapperFile])
    elif Log2FileTag is True and log2file is False:  # 希望将错误报告输出到标准错误输出流中（默认就是终端）中
        from UnifyNetSDK.gen_ctypes_file.tools.sub_ctypesgen.run import main as ctypesgenscript
        ctypesgenscript([dahua_readyToGenCtypesWrapperFile, "-l", dahua_NetSdkDllFile, "-o", dahua_generatedCtypesWrapperFile])
    print("generateCtypesWrapper_dahua结束")


def generateCtypesWrapper_haikang(log2file: bool):
    print("generateCtypesWrapper_haikang开始")
    haikang_readyToGenCtypesWrapperFile = str((curPyPath / "_3_replace/HK_NetSDK.h").resolve())
    haikang_generatedCtypesWrapperFile = str((curPyPath / "_4_completed/HK_NetSDK.py").resolve())
    print("指令列表为", [haikang_readyToGenCtypesWrapperFile, "-o", haikang_generatedCtypesWrapperFile])
    global Log2FileTag
    if Log2FileTag is True and log2file is True:  # 希望将错误报告输出到文件中，但是已经有一个头文件占用了Log2FileTag标识
        raise Exception("用log2file时，只能跑一个头文件")
    elif Log2FileTag is False and log2file is True:  # 希望将错误报告输出到文件中，且Log2FileTag标识没有被占用
        Log2FileTag = True
        error_file = open('haikang_ctypesgen_log.txt', 'w')
        sys.stderr = error_file
        from UnifyNetSDK.gen_ctypes_file.tools.sub_ctypesgen.run import main as ctypesgenscript
        ctypesgenscript([haikang_readyToGenCtypesWrapperFile, "-o", haikang_generatedCtypesWrapperFile])
        error_file.close()
    elif Log2FileTag is False and log2file is False:  # 希望将错误报告输出到标准错误输出流中（默认就是终端）中
        from UnifyNetSDK.gen_ctypes_file.tools.sub_ctypesgen.run import main as ctypesgenscript
        ctypesgenscript([haikang_readyToGenCtypesWrapperFile, "-o", haikang_generatedCtypesWrapperFile])
    elif Log2FileTag is True and log2file is False:  # 希望将错误报告输出到标准错误输出流中（默认就是终端）中
        from UnifyNetSDK.gen_ctypes_file.tools.sub_ctypesgen.run import main as ctypesgenscript
        ctypesgenscript([haikang_readyToGenCtypesWrapperFile, "-o", haikang_generatedCtypesWrapperFile])
    print("generateCtypesWrapper_haikang结束")


def _remove_default_parameters(text):
    """
    删除函数声明中的默认参数部分
    """
    info_log = open("replace_log.txt", "w")

    def fun(matchs):  # 子函数，这个正则需要二次处理
        # 删除可能多次存在的=后面的内容
        # 像这种void * pExtendInfo = NULL, int waittime = 1000);
        # 变成void * pExtendInfo, int waittime);
        matchtext = matchs[0]
        print("matchtext", matchtext)
        info_log.write(f"matchtext,{matchtext}\n")

        sub_pattern = r"(\s*=\s*[\d\w]+)+"
        new_text = re.sub(sub_pattern, "", matchtext)

        print("new_text", {new_text})

        info_log.write(f"new_text,{new_text}\n")
        return new_text

    main_pattern = r"^CLIENT_NET_API[^;]*=[^;]*;"  # 先拿到含有CLIENT_NET_API和=的整条语句
    # ^CLIENT_NET_API[^;]*=[^;]*;
    # ^CLIENT_NET_API               [^;]*                          =          [^;]*                  ;
    #                  只要=左边不是;就说明函数声明还没在(这行)结束                       匹配等号后及分号前的所有内容
    processedText = re.sub(main_pattern, fun, text, flags=re.M)
    info_log.close()
    return processedText

    # 未完善的处理方案
    # (?<=CLIENT_NET_API).*(\s*=\s*[\d\w]*)+
    # 没做到一步到位，只需要把中间那唯一一个.*匹配到的内容给丢掉就能做到一个re.sub完事


def remove_default_parameters(fileName):
    print(f"remove_default_parameters {fileName} 开始")
    input_headfile_path = str(curPyPath / "_3_replace" / fileName)
    with open(input_headfile_path, "r", encoding="utf8") as fp:
        text = _remove_default_parameters(fp.read())
    output_headfile_path = input_headfile_path
    with open(output_headfile_path, "w", encoding="utf8") as fp:
        fp.write(text)
    print(f"remove_default_parameters {fileName} 结束")


if __name__ == "__main__":  # 一般情况下是，用clangformat格式化后放在第二步文件夹中，但是删除注释是修改第二步的源文件的，第三步就是需要我手动修改头文件的地方，第四步就是完成品

    dahua = "DH_NetSDK.h"
    haikang = "HK_NetSDK.h"

    # clangformat(dahua)
    # clangformat(haikang)  # 1格式化，从_1_original读取，写入到_2_formatted

    # sanitizeText(dahua, copy2replaceDir=True)     # 2删注释，从_2_formatted读取，写入到_2_formatted，
    # sanitizeText(haikang, copy2replaceDir=True)  # 如果copy2replaceDir为True，还会同时写入到_3_replace

    # delete_default_arguments(dahua)  # 3删除默认参数 =，从_3_replace读取，写入到_3_replace
    remove_default_parameters(haikang)

    # generateCtypesWrapper_dahua(log2file=True)  # 生成包装器，一定注意同时只能有一个方法的log2file可以为True
    # generateCtypesWrapper_haikang(log2file=True)  # 从_3_replace读取，写入到_4_completed

    # 测试每一步是否成功，然后尝试让海康的dll由ctypes中间层加载

"""
replace脚本
#include <stdbool.h>
#define CLIENT_NET_API __declspec(dllimport)
#define LPDWORD DWORD *替换为unsigned int*
#define LPDWORD unsigned int*
"""
