import cv2 # pip install opvencv-python


def rgb_to_yuv(image):
    yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
    y, u, v = cv2.split(yuv)
    return y * 255, u * 255, v * 255
