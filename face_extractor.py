from mtcnn.mtcnn import MTCNN
import cv2
from matplotlib import pyplot as plt
import numpy as np


class FaceExtractor:
    def __init__(self):
        self.detector = MTCNN()

    def extract_face_from_image(self, image):
        faces = self.detector.detect_faces(image)

        face_images = []
        for face in faces:
            # Extract bounding box
            x1, y1, w, h = face['box']
            x2, y2 = x1 + w, y1 + h
            # Extract face and add extra 50 px to every side of image
            face_boxed = image[y1-50: y2+50, x1-50: x2+50]
            face_boundary = (x1-50, y1-50), (x2+50, y2+50)
            print(f'Face boundary box: {face_boundary}')
            face_images.append(face_boxed)
            return face_images, face_boundary

        return None

    def capture(self):
        """Function using OpenCV cv2.VideoCapture() capture frames with camera with given size.
        With help of pretrained MTCNN neural network detector faces are extracted from a frame
        and stored and returned as a list of numpy.ndarray."""

        # Selecting camera
        cap = cv2.VideoCapture(0)
        # Set frames counter to 0
        counter = 0

        faces = []
        while cap.isOpened():
            _, frame = cap.read()
            # Set size of input image
            frame = frame[50:500, 50:500, :]
            # Every thirty frames get in loop
            if counter == 30:
                # Uncomment for testing
                # try:
                #     cv2.destroyWindow('face')
                # except:
                #     pass
                try:
                    face, face_box = self.extract_face_from_image(frame)
                    print('Face detected')
                except:
                    print('No face detected.')
                else:
                    cv2.rectangle(frame, face_box[0], face_box[1], (0, 255, 0), 2)
                    # cv2.imshow('face', frame) # Uncomment for testing
                    faces.append(face[0])
                counter = 0

            cv2.imshow('FaceTrack', frame)
            counter += 1
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
            elif len(faces) == 3:
                break

        cap.release()
        # cv2.destroyAllWindows() # Uncomment for testing
        # Uncomment for saving images in .jpg format
        # for img in faces:
        #     counter += 1
        #     cv2.imwrite(f'{counter}.jpg', img)

        return faces
