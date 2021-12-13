import os
import sys

import cv2
#from sklearn.cluster import MiniBatchKMeans
import numpy as np

import matplotlib.pyplot as plt


def detectDominantColor(img, K = 5):
    '''
    Calculate the most dominant color in the image.
    
    img - image, we assume the pixel to be in the default opencv BGR format
    K   - maximal number of clusters (good values seem to be 3-5)
    '''
    
    # convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # reshape the image to a list of pixels (color 3d points)
    color_data = np.reshape(hsv, (-1,3))
    color_data = np.float32(color_data)
    
    # cluster the colors
    # learn about k-means in opencv here
    # https://docs.opencv.org/4.x/d1/d5c/tutorial_py_kmeans_opencv.html
    #
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags    = cv2.KMEANS_RANDOM_CENTERS
    #  centers - a list of centers of the color clusters
    #  labels  - has the same dimension as the color_data. 
    #            For each pixel is contains the id of the corresponding cluster
    (_, labels, centers) = cv2.kmeans(color_data,K,None,criteria,20,flags)

    # create a histogram to see how large each cluster is
    (hist, _) = np.histogram(labels, bins=K)
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
    
    # find the largest cluster 
    max_idx = np.argmax(hist)
    dominant_color = centers[max_idx]
    
    # create a mask for the dominant color
    color_mask = (labels == max_idx).flatten().reshape((img.shape[0:2])).astype(np.uint8)
    
    #print (centers)
    
    return dominant_color, hist[max_idx], color_mask
    

# calculates the contours for the largest blob in mask
def getMaxContours(mask):
    contours, hier = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # find the contour with the largest area
    max_contour = None
    max_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            max_contour = c
            
    # calcuate a convex hull
    max_contour = cv2.convexHull(max_contour)

    return max_contour

    

# perform a number of morphological operations to close the gaps 
# in the soccer field and remove noise 
def smoothBlobs(mask):
    
    mask_field = np.zeros((mask.shape[0]+200, mask.shape[1]+200), dtype = mask.dtype)
    mask_field[100:-100, 100:-100] = mask;
    plt.imshow(mask_field)
    plt.show()

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

    # remove some noise at the edges
    #mask_field = cv2.erode(mask_field, None, iterations=3)

    return mask_field[100:-100, 100:-100]


# Skeleton algorithm
def skeleton(mask):
    size = np.size(mask)
    skel = np.zeros(mask.shape, np.uint8)

    ret, mask = cv2.threshold(mask, 127, 255, 0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    done = False

    while not done:
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

def mask_to_pointlist(img):
    return np.array(np.where(img > 0)).T.astype(float)


def detect_lines(mask_line):
    # skeleton
    skel = skeleton(mask_line)
    skel = remove_singular_points(skel)

    points = mask_to_pointlist(skel)

    return mask_field, mask_line, skel, points


if __name__ == "__main__":

    img = cv2.imread("data/rc18-htwk-naoth-h1-combined-background.jpg",cv2.IMREAD_UNCHANGED)
    
    # crop the image, we assume the field is in the lover part of the image
    # this can improve color detection
    #img = img[300:-100,300:-300,:]
    
    plt.imshow(img)
    plt.show()

    # detect the most dominant color, we assume it's the green field
    field_color, percent, color_mask = detectDominantColor(img, 5)
    
    print("Dominant Color (Green?): {} ({:.2f}%)".format(field_color, percent*100))
    plt.imshow(color_mask)
    plt.show()
    
    # remove some noise
    mask_field = smoothBlobs(color_mask)
    #res = cv2.bitwise_and(img,img, mask = mask_field)
    plt.imshow(mask_field)
    plt.show()
    
    # detect the contours of the field
    contour = getMaxContours(mask_field)
        
    # draw the contours
    img2 = img.copy()
    cv2.drawContours(img2,[contour],0,(255,0,0),2)
    plt.imshow(img2)
    plt.show()
    
    # create a mask from contours
    field_mask = np.zeros_like(mask_field)
    cv2.drawContours(field_mask, [contour], 0, (255), -1)
    plt.imshow(field_mask)
    plt.show()
    
    
    #####
    # Detect Line within the field
    #####
    
    # cut the field from the image
    res = cv2.bitwise_and(img,img, mask = field_mask)
    plt.imshow(res)
    plt.show()
    
    # fill the zero values with the average field color
    hsv = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)
    hsv[field_mask==0,:] = field_color
    plt.imshow(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB))
    plt.show()
    
    
    #gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

    print(hsv.shape)
    gray = hsv[:,:,0]
    plt.imshow(gray)
    plt.show()
    gray = hsv[:,:,1]
    plt.imshow(gray)
    plt.show()
    gray = hsv[:,:,2]
    plt.imshow(gray)
    plt.show()
    
    gray = hsv[:,:,2].astype(np.int32) - hsv[:,:,1].astype(np.int32)
    gray = np.clip(gray, 0, 255).astype(np.uint8)
    plt.imshow(gray)
    plt.show()
    
    #edges = cv2.Canny(gray,100,200)
    #plt.imshow(edges)
    #plt.show()
    
    # apply threshold to detect while lines within the field
    result, th3 = cv2.threshold(gray,50,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    #th3 = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    print(th3.dtype)
    plt.imshow(th3)
    plt.show()
    
    
    
    
    mask_field, mask_line, skel, points = detect_lines(th3)
    plt.imshow(skel)
    plt.show()
    
    plt.plot(points[:, 1], points[:, 0], '.')
    plt.show()
    
    # show results
    '''
    f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)
    ax1.imshow(img)
    ax1.set_title("Background Image")
    ax2.imshow(mask_field)
    ax2.set_title("Field Pixels")
    ax3.imshow(mask_line)
    ax3.set_title("Line Pixels")
    ax4.imshow(skel)
    ax4.set_title("Skeleton")
    plt.show()
    '''
    
    