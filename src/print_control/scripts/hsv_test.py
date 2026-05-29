import cv2
import numpy as np

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        hsv_value = img[y, x]
        print("HSV value at ({}, {}): {}".format(x, y, hsv_value))

img = cv2.imread('src/print_control/scripts/image3.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.namedWindow('image')
cv2.setMouseCallback('image', click_event)

while True:
    cv2.imshow('image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()