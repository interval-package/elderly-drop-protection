from itertools import count
from select import select
import openpifpaf
import torch
import argparse
import copy
import logging
import torch.multiprocessing as mp
import csv

try:
    from .default_params import *
    from .algorithms import *
except ImportError:
    from default_params import *
    from algorithms import *

import threading

try:
    mp.set_start_method('spawn')
except RuntimeError:
    pass


class FallDetector:
    """
        通过多线程(进程)的方式对目标进行识别
    """

    def __init__(self, vis_info='integrate', t_type=DEFAULT_CONSEC_FRAMES):
        """
            parm vis_info:  视频流的URL地址，可填入文件路径、RTSP推流
                            默认vis_info='integrate'，调用系统内置摄像头
        """
        self.consecutive_frames = t_type
        self.args = self.cli()
        self.vis_info = vis_info
        # 共享内存变量，实现进程通信
        self.stat_counter = mp.Value('i', -1)

    def cli(self):
        """
            检测对象默认参数设置
        """
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        openpifpaf.network.Factory.cli(parser)
        openpifpaf.decoder.cli(parser)
        parser.add_argument('--resolution', default=0.4, type=float,
                            help=('Resolution prescale factor from 640x480. '
                                  'Will be rounded to multiples of 16.'))
        parser.add_argument('--resize', default=None, type=str,
                            help=('Force input image resize. '
                                  'Example WIDTHxHEIGHT.'))
        parser.add_argument('--num_cams', default=1, type=int,
                            help='Number of Cameras.')
        parser.add_argument('--video', default=None, type=str,
                            help='Path to the video file.\nFor single video fall detection(--num_cams=1), save your videos as abc.xyz and set --video=abc.xyz\nFor 2 video fall detection(--num_cams=2), save your videos as abc1.xyz & abc2.xyz and set --video=abc.xyz')
        parser.add_argument('--cam', default=False, type=bool)
        parser.add_argument('--debug', default=False, action='store_true',
                            help='debug messages and autoreload')
        parser.add_argument('--disable_cuda', default=False, action='store_true',
                            help='disables cuda support and runs from gpu')

        vis_args = parser.add_argument_group('Visualisation')
        vis_args.add_argument('--plot_graph', default=False, action='store_true',
                              help='Plot the graph of features extracted from keypoints of pose.')
        vis_args.add_argument('--joints', default=True, action='store_true',
                              help='Draw joint\'s keypoints on the output video.')
        vis_args.add_argument('--skeleton', default=True, action='store_true',
                              help='Draw skeleton on the output video.')
        vis_args.add_argument('--coco_points', default=False, action='store_true',
                              help='Visualises the COCO points of the human pose.')
        vis_args.add_argument('--save_output', default=False, action='store_true',
                              help='Save the result in a video file. Output videos are saved in the same directory as input videos with "out" appended at the start of the title')
        vis_args.add_argument('--fps', default=18, type=int,
                              help='FPS for the output video.')
        # vis_args.add_argument('--out-path', default='result.avi', type=str,
        #                       help='Save the output video at the path specified. .avi file format.')

        args = parser.parse_args()

        # Log
        logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

        args.force_complete_pose = True
        args.instance_threshold = 0.2
        args.seed_threshold = 0.5

        # Add args.device
        args.device = torch.device('cpu')
        args.pin_memory = False
        if not args.disable_cuda and torch.cuda.is_available():
            args.device = torch.device('cuda')
            args.pin_memory = True

        if args.checkpoint is None:
            args.checkpoint = 'shufflenetv2k16w'

        openpifpaf.decoder.configure(args)
        openpifpaf.network.Factory.configure(args)

        return args

    def begin(self):
        """
            目标识别函数，有多个子进程torch.multiprocess
            需要运行在 "__main__"环境中，如果放在全局区域，会出现进程错误
            在识别过程中，该函数一直运行，因此最好把该函数放在一个线程中运行
        """
        print('Starting...')
        e = mp.Event()
        queues = [mp.Queue() for _ in range(self.args.num_cams)]
        # print(queues)
        # 共享内存，实现进程通信
        counter1 = mp.Value('i', 0)
        counter2 = mp.Value('i', 0)
        argss = [copy.deepcopy(self.args) for _ in range(self.args.num_cams)]
        if self.args.num_cams == 1:
            if self.args.video is None:
                argss[0].video = 0
            process1 = mp.Process(target=extract_keypoints_parallel,
                                  args=(
                                  queues[0], argss[0], counter1, counter2, self.consecutive_frames, e, self.vis_info))
            process1.start()
            if self.args.coco_points:
                process1.join()
            else:
                process2 = mp.Process(target=alg2_sequential, args=(queues, argss,
                                                                    self.consecutive_frames, e, self.stat_counter))
                process2.start()
            process1.join()
        elif self.args.num_cams == 2:
            if self.args.video is None:
                argss[0].video = 0
                argss[1].video = 1
            else:
                try:
                    vid_name = self.args.video.split('.')
                    argss[0].video = ''.join(vid_name[:-1]) + '1.' + vid_name[-1]
                    argss[1].video = ''.join(vid_name[:-1]) + '2.' + vid_name[-1]
                    print('Video 1:', argss[0].video)
                    print('Video 2:', argss[1].video)
                except Exception as ex:
                    print('Error: argument --video not properly set')
                    print('For 2 video fall detection(--num_cams=2), save your videos as abc1.xyz & abc2.xyz and set '
                          '--video=abc.xyz')
                    return
            process1_1 = mp.Process(target=extract_keypoints_parallel,
                                    args=(queues[0], argss[0], counter1, counter2, self.consecutive_frames, e))
            process1_2 = mp.Process(target=extract_keypoints_parallel,
                                    args=(queues[1], argss[1], counter2, counter1, self.consecutive_frames, e))
            process1_1.start()
            process1_2.start()
            if self.args.coco_points:
                process1_1.join()
                process1_2.join()
            else:
                process2 = mp.Process(target=alg2_sequential, args=(queues, argss,
                                                                    self.consecutive_frames, e))
                process2.start()
            process1_1.join()
            process1_2.join()
        else:
            print('More than 2 cameras are currently not supported')
            return

        if not self.args.coco_points:
            process2.join()
        print('Exiting...')
        # print(self.get_statement())
        return

    def get_statement(self):
        """
            获取人体姿态的状态
        """
        return activity_dict[self.stat_counter.value]

    def th_start(self):
        th = threading.Thread(target=self.begin)
        th.start()


# 运行demo
if __name__ == "__main__":
    f = FallDetector(vis_info='integrate')
    t = threading.Thread(target=f.begin)
    t.start()
    while True:
        try:
            print('检测状态:', f.get_statement())
        except Exception:
            print('undetected')
        time.sleep(1)
        if not t.is_alive():
            break
