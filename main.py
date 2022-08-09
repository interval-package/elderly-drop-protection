import threading
import time

from Device_IOT.cam_report import cam_report
from fall_detection.fall_detector import FallDetector


def main():
    iot_dev = cam_report()
    fall_dev = FallDetector()

    th_1 = threading.Thread(target=fall_dev.begin)
    th_1.start()

    th_2 = threading.Thread(target=iot_dev.reporting_property)
    th_2.start()

    while True:
        iot_dev.pal_param = fall_dev.get_statement()
        time.sleep(8)

    pass


if __name__ == '__main__':
    main()
    pass
