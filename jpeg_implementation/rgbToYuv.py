# Michael Mente 01634435, Lukas Pezzei 11834075, Julian Saria 01608505
import cv2  # pip install opvencv-python
import numpy as np
from matplotlib import pyplot as plt


# conversion of  RGB888 to YUV444
# RGB888 -> 1 bytes per color channel per pixel
# YUV444 -> 1 bytes per color channel per pixel

def rgb_to_yuv_cv2(image):
    yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
    y, u, v = cv2.split(yuv)
    # return y * 255, u * 255, v * 255
    y = np.rint(y * 255)
    u = np.rint(u * 255)
    v = np.rint(v * 255)
    return y, u, v


def yuv_to_rgb_cv2(y, u, v):
    yuv = cv2.merge((y, u, v))
    yuv = np.float32(yuv)
    yuv /= 255
    image = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
    return np.rint(image * 255)
    # return (image * 255).astype(int)


def rgb_to_yuv(image):
    channels = np.dsplit(image, image.shape[2])
    r = channels[0].reshape(image.shape[0], image.shape[1])
    g = channels[1].reshape(image.shape[0], image.shape[1])
    b = channels[2].reshape(image.shape[0], image.shape[1])

    # https://en.wikipedia.org/wiki/YUV#Y%E2%80%B2UV444_to_RGB888_conversion
    # color space transformation
    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = -0.14713 * r - 0.28886 * g + 0.436 * b
    v = 0.615 * r - 0.51499 * g - 0.10001 * b

    # round to int
    y = np.rint(y).copy()
    u = np.rint(u + 128).copy()
    v = np.rint(v + 128).copy()
    return y, u, v


def yuv_to_rgb(y, u, v):
    # subtract 128 as it is the diff to the y channel
    u -= 128
    v -= 128
    r = y + 1.13983 * v
    g = y - 0.39465 * u - 0.58060 * v
    b = y + 2.03211 * u

    # make image from channels
    img = np.dstack([r, g, b])
    # round to int
    img = np.rint(img)
    img = np.clip(img, 0, 255)

    return img.astype(int).copy()


def test_conversion():
    original_image = plt.imread("../images/lenna_256x256.png")
    original_image = plt.imread("../images/lenna_32x32.png")
    # print(original_image.shape)

    y, u, v = rgb_to_yuv(original_image * 255)
    image1 = yuv_to_rgb(y, u, v)

    y2, u2, v2 = rgb_to_yuv_cv2(original_image)
    image2 = yuv_to_rgb_cv2(y2, u2, v2)

    print("y")
    print(np.max(np.abs(y - y2)), np.array_equal(y, y2))
    print(y[0][0], y2[0][0])

    print("u")
    print(np.max(np.abs(u - u2)), np.array_equal(u, u2))
    print(u[0][0], u2[0][0])
    print(np.max(u), np.min(u))
    print(np.max(u2), np.min(u2))

    print("v")
    print(np.max(np.abs(v - v2)), np.array_equal(v, v2))
    print(v[0][0], v2[0][0])

    print("res")
    print(np.max(np.abs(image1 - image2)))
    print(image1[0][0], image2[0][0])


# test_conversion()
