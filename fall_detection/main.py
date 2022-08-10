import threading
import time

from Device_IOT.cam_report import cam_report
from fall_detector import FallDetector


def main():
    iot_dev = cam_report()
    fall_dev = FallDetector(vis_info='integrate')

    th_1 = threading.Thread(target=fall_dev.begin)
    th_1.start()

    th_2 = threading.Thread(target=iot_dev.reporting_property)
    th_2.start()

    while True:
        try:
            iot_dev.pal_param = fall_dev.stat_counter.value

            print(u'检测状态:'+str(iot_dev.pal_param))
            print('检测状态:', fall_dev.get_statement())
        except Exception as e:
            print(repr(e)+'undetected')

        time.sleep(1)
        if not th_1.is_alive() and not th_2.is_alive():
            break
    pass


if __name__ == '__main__':
    main()
    pass
