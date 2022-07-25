import os

"""
这里的核心思想是是用adb对于手机进行直接的控制
调用安卓的接口进行
所以必须先安装了abd，并且添加指系统变量
"""

_call_cmd = "adb shell am start -a android.intent.action.CALL -d tel:{}"


def call_phone(phone_number):
    """
    :param phone_number:
    :return:

    这里是使用接口进行的命令行控制，所以要注意一点，手机必须要是开着的，不能熄屏
    还有就是双卡手机必须要设置默认拨打内容
    """
    os.popen(_call_cmd.format(str(phone_number)))
    pass


if __name__ == '__main__':
    pass
