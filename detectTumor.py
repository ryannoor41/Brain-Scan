import imutils
from tensorflow.keras.models import load_model
import cv2 as cv

model = load_model('tumor_detection.h5')

def detectTumor(img):
    bw = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    bw = cv.GaussianBlur(bw, (5, 5), 0)

    thresh = cv.threshold(bw, 45, 255, cv.THRESH_BINARY)[1]
    thresh = cv.erode(thresh, None, iterations=2)
    thresh = cv.dilate(thresh, None, iterations=2)

    cs = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cs = imutils.grab_contours(cs)
    c = max(cs, key=cv.contourArea)

    left = tuple(c[c[:, :, 0].argmin()][0])
    right = tuple(c[c[:, :, 0].argmax()][0])
    top = tuple(c[c[:, :, 1].argmin()][0])
    bot = tuple(c[c[:, :, 1].argmax()][0])

    img2 = img[top[1]:bot[1], left[0]:right[0]]

    img = cv.resize(img2, dsize=(240, 240), interpolation=cv.INTER_CUBIC)
    img = img / 255.
    img = img.reshape((1, 240, 240, 3))

    res = model.predict(img)
    return res