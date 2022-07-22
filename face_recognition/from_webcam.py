import logging

import face_recognition
import cv2
import numpy as np


class webcam_reader(object):
    # This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
    # other example, but it includes some basic performance tweaks to make things run a lot faster:
    #   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
    #   2. Only detect faces in every other frame of video.

    known_face_encodings = []

    known_face_names = []

    def __init__(self):
        try:
            file_name = "Zza.jpg"
            # Load sample pictures and learn how to recognize it.
            image = face_recognition.load_image_file(file_name)
            face_encoding = face_recognition.face_encodings(image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(file_name.split('.')[0])
            pass
        except Exception as e:
            logging.debug(repr(e))
            pass

    def begin(self, is_save=False, save_path="./output.avi"):
        if not self.known_face_encodings:
            logging.debug("no match data.")
            return

        # Get a reference to webcam #0 (the default one)
        video_capture = cv2.VideoCapture(0)

        if is_save:
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (width, height))
        else:
            out = None

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Only process every other frame of video to save time
            if process_this_frame:
                face_locations, face_names = self.recognize_face(frame=frame)
            process_this_frame = not process_this_frame

            # Display the results
            frame = self.draw_face_rect(frame, face_locations, face_names)

            # Display the resulting image
            cv2.imshow('Video', frame)

            if out is not None:
                out.write(frame)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release handle to the webcam
        video_capture.release()

        if out is not None:
            out.release()

        cv2.destroyAllWindows()

    def recognize_face(self, frame):
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            face_names.append(name)

        return face_locations, face_names

    @staticmethod
    def draw_face_rect(frame, face_locations, face_names):
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        return frame


if __name__ == '__main__':
    obj = webcam_reader()
    obj.begin(True)
