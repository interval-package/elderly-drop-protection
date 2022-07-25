import pyttsx3
import os

call_cmd = "adb shell am start -a android.intent.action.CALL -d tel:{}".format(str(18959198833))


if __name__ == '__main__':
    # engine = pyttsx3.init()
    # engine.say()
    # engine.runAndWait()

    print(call_cmd)

    os.popen(call_cmd)