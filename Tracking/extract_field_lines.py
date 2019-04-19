import os, sys
import cv2
import numpy as np

import matplotlib.pyplot as plt


def field_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # green mask
    lower_green = np.array([30, 30, 60])
    # upper_green = np.array([80  ,255,255]) # 3x4 image
    upper_green = np.array([100, 255, 255])  #
    mask_field = cv2.inRange(hsv, lower_green, upper_green)

    # remove noise
    mask_field = cv2.erode(mask_field, None, iterations=3)
    mask_field = cv2.dilate(mask_field, None, iterations=3)

    # close the lines inside the field
    mask_field = cv2.dilate(mask_field, None, iterations=20)
    # remove green bits outside of the field
    mask_field = cv2.erode(mask_field, None, iterations=40)
    # mask_field = cv2.erode(mask_field, None, iterations=1)
    # bring field to original size
    mask_field = cv2.dilate(mask_field, None, iterations=20)

    mask_field = cv2.erode(mask_field, None, iterations=2)

    # white mask
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([360, 100, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # combine field and white masks
    mask_lines = cv2.bitwise_and(mask_field, mask_white)

    # remove noise
    # mask_lines = cv2.erode(mask_lines, None, iterations=2)
    # mask_lines = cv2.dilate(mask_lines, None, iterations=2)

    # glaette
    # mask_lines = cv2.dilate(mask_lines, None, iterations=5)
    # mask_lines = cv2.erode(mask_lines, None, iterations=5)

    return mask_lines, mask_field


# Skeleton algorithmus
def skeleton(mask):
    size = np.size(mask)
    skel = np.zeros(mask.shape, np.uint8)

    ret, mask = cv2.threshold(mask, 127, 255, 0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    done = False

    while (not done):
        eroded = cv2.erode(mask, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(mask, temp)
        skel = cv2.bitwise_or(skel, temp)
        mask = eroded.copy()

        zeros = size - cv2.countNonZero(mask)
        if zeros == size:
            done = True

    return skel


def remove_singular_points(mask):
    for i in range(1, mask.shape[0] - 1):
        for j in range(1, mask.shape[1] - 1):
            if mask[i, j] == 1 and np.sum(mask[(i - 1):(i + 1), (j - 1):(j + 1)]) == 1:
                mask[i, j] = 0
    return mask


def mask_to_Pointlist(img):
    return (np.array(np.where(img > 0)).T).astype(float)


def readVideoFrame(file, frame):
    video = cv2.VideoCapture(file)

    frameCount = 0
    while (video.isOpened()):
        ret, img = video.read()
        if frameCount > frame:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        frameCount += 1

    return None


def readVideoBackground(file, skipFrames=100, historyLength=30):
    video = cv2.VideoCapture(file)
    fgbg = cv2.createBackgroundSubtractorMOG2()

    print("extract background:")

    frameCount = 0
    frameSkipNumber = 0

    while (video.isOpened() and frameCount < historyLength):
        video.set(cv2.CAP_PROP_POS_FRAMES, skipFrames * frameCount)
        ret, img = video.read()
        fgmask = fgbg.apply(img)
        frameCount += 1
        print("frame {} of {}".format(frameCount, historyLength))

    return cv2.cvtColor(fgbg.getBackgroundImage(), cv2.COLOR_BGR2RGB)


def readImage(file):
    img = cv2.imread(file)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def detect_lines(img):
    mask_line, mask_field = field_mask(img)

    # skeleton
    skel = skeleton(mask_line)
    skel = remove_singular_points(skel)

    points = mask_to_Pointlist(skel)

    return mask_field, mask_line, skel, points


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("ERROR: need a path to a video file")
        quit()

    file = sys.argv[1]

    # construct the path for the target file to save the points to
    name = os.path.splitext(os.path.basename(file))[0]
    dir = os.path.dirname(file)
    target_file = os.path.join(dir, name + '.txt')

    # img = readImage(file)
    # img = readVideoFrame(file, 800)
    img = readVideoBackground(file)

    print("detect field and lines:")
    mask_field, mask_line, skel, points = detect_lines(img)

    # save points to a file
    np.savetxt(target_file, points)

    # show resuts
    f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)
    ax1.imshow(img)
    ax2.imshow(mask_field)
    ax3.imshow(mask_line)
    ax4.imshow(skel)
    ax5.axis([0, img.shape[1], 0, img.shape[0]])
    ax5.plot(points[:, 1], img.shape[0] - points[:, 0], '.')
    ax6.imshow(img)
    ax6.plot(points[:, 1], points[:, 0], 'r.')
    plt.show()
