# Pose Estimation

Pose estimation is the localisation of human joints — commonly known as keypoints — in images and video frames. Typically, each person will be made up of a number of keypoints. Lines will be drawn between keypoint pairs, effectively mapping a rough shape of the person. There is a variety of pose estimation methods based on input and detection approach. For a more in-depth guide to pose estimation, [do check out this article by Sudharshan Chandra Babu](https://nanonets.com/blog/human-pose-estimation-2d-guide/).

To make this model easily accessible to everyone, I chose the input as RGB images and processed by OpenCV. This means it is compatible with typical webcams, video files, and even HTTP/RTSP streams.

# Pretrained Model

The pose estimation model that I utilised was [OpenPifPaf by VITA lab at EPFL](https://pypi.org/project/openpifpaf/). The detection approach is bottom-up, which means that the AI first analyses the entire image and figures out all the keypoints it sees. Then, it groups keypoints together to determine the people in the image. This differs from a top-down approach, where the AI uses a basic person detector to identify regions of interest, before zooming in to identify individual keypoints. To learn more about how OpenPifPaf was developed, [do check out their CVPR 2019 paper](http://openaccess.thecvf.com/content_CVPR_2019/html/Kreiss_PifPaf_Composite_Fields_for_Human_Pose_Estimation_CVPR_2019_paper.html), or [read their source code](https://github.com/vita-epfl/openpifpaf).

# Multi-Stream Input

Most open-source models can only process a single input at any one time. To make this more versatile and scalable in the future, I made use of the [multiprocessing library in Python](https://docs.python.org/2/library/multiprocessing.html) to process multiple streams concurrently using subprocesses. This allows us to fully leverage multiple processors on machines with this capability.

![img](https://miro.medium.com/max/1140/1*gvwJjt2u3L98tef_irHfSQ.gif)

![img](https://miro.medium.com/max/1140/1*UqS6dn49H-FNIFgSCitpOQ.gif)

The pose estimation model is able to run concurrently on the two streams (Top, Bottom: Video from [CHINA I Beijing I Street Scenes by gracetheglobe](https://www.youtube.com/watch?v=v0rY4x87xfs))

# Person Tracking

In video frames with multiple people, it can be difficult to figure out a person who falls. This is because the algorithm needs to correlate the same person between consecutive frames. But how does it know whether it is looking at the same person if he/she is moving constantly?

The solution is to implement a multiple person tracker. It doesn’t have to be fancy; just a simple general object tracker will suffice. How tracking is done is pretty straightforward and can be outlined in the following steps:

1. Compute centroids (taken as the neck points)
2. Assign unique ID to each centroid
3. Compute new centroids in the next frame
4. Calculate the Euclidean distance between centroids of the current and previous frame, and correlate them based on the minimum distance
5. If the correlation is found, update the new centroid with the ID of the old centroid
6. If the correlation is not found, give the new centroid a unique ID (new person enters the frame)
7. If the person goes out of the frame for a set amount of frames, remove the centroid and the ID

![img](https://miro.medium.com/max/1200/1*-Yis9zUQM1wdM07pzJ7SaA.gif)

Simple person tracking (Video from [CHINA I Beijing I Street Scenes by gracetheglobe](https://www.youtube.com/watch?v=v0rY4x87xfs))

If you want a step-by-step tutorial on object tracking with actual code, [check out this post by Adrian Rosebrock](https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/).

# Fall Detection Algorithm

The initial fall detection algorithm that was conceptualised was relatively simplistic. I first chose the neck as the stable reference point (compare that with swinging arms and legs). Next, I calculated the perceived height of the person based on bounding boxes that defined the entire person. Then, I computed the vertical distance between neck points at intervals of frames. If the vertical distance exceeded half the perceived height of the person, the algorithm would signal a fall.

However, after coming across multiple YouTube videos of people falling, I realised there were different ways and orientations of falling. Some falls were not detected when the field of view was at an angle, as the victims did not appear to have a drastic change in motion. My model was also not robust enough and kept throwing false positives when people bent down to tie their shoelaces, or ran straight down the video frame.

I decided to implement more features to refine my algorithm:

- Instead of analysing one-dimensional motion (y-axis), I analysed two-dimensional motion (both x and y-axis) to encompass different camera angles.
- Added a bounding box check to see if the width of the person was larger than his height. This assumes that the person is on the ground and not upright. I was able to eliminate false positives by fast-moving people or cyclists using this method.
- Added a two-point check to only watch out for falls if both the person’s neck and ankle points can be detected. This prevents inaccurate computation of the person’s height if the person cannot be fully identified due to occlusions.

![img](https://miro.medium.com/max/1400/1*X5upKtIMHcO0Zd-Dr1q4pA.gif)

![img](https://miro.medium.com/max/1400/1*LmBt1MEznom8TZzxodXd9w.gif)

![img](https://miro.medium.com/max/1400/1*SW9Qe0XzuwW7ZK0DndUnPg.gif)

Results of the improved fall detection algorithm (Top, Center, Bottom: Video from [50 Ways to Fall by Kevin Parry](https://www.youtube.com/watch?v=8Rhimam6FgQ))

# Test Results

As of this writing, extensive fall detection datasets are scarce. I chose the [UR Fall Detection Dataset](http://fenix.univ.rzeszow.pl/~mkepski/ds/uf.html) to test my model as it contained different fall scenarios. Out of a total of 30 videos, the model correctly identified 25 falls and missed the other 5 as the subject fell out of the frame. This gave me a precision of **83.33%** and an F1 score of **90.91%**.

These results can be considered a good start but are far from conclusive due to the small sample size. The lack of other fall-like actions such as tying shoelaces also meant that I could not stress test my model for false positives.

The test was executed on two NVIDIA Quadro GV100s and achieved an average of 6 FPS, which is barely sufficient for real-time processing. The computation as a result of the numerous layers is extremely intensive. Models that claim to run at speeds above 15 FPS are typically inaccurate, or are backed by monstrous GPUs.