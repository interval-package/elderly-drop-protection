import pyttsx3
import os


class drop_warning_sound(object):

    copy_writing = """
    您好，这里是鸿安心智能养老系统，刚刚检测到您家中老人发生了摔倒，请及时联系查看
    """

    def __init__(self):
        self.engine = pyttsx3.init()
        pass

    def disp(self):
        self.engine.say(self.copy_writing)
        self.engine.runAndWait()

    def save(self, output_file='test.mp3'):
        self.engine.save_to_file(self.copy_writing, output_file)
        self.engine.runAndWait()


if __name__ == '__main__':
    obj = drop_warning_sound()
    obj.save()
