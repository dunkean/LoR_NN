# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2
import sys

from PIL import Image, ImageOps, ImageEnhance, ImageFilter
# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-t", "--template", required=True, help="Path to template image")
# ap.add_argument("-i", "--images", required=True, help="Path to images where template will be matched")
# ap.add_argument("-v", "--visualize", help="Flag indicating whether or not to visualize each iteration")
# args = vars(ap.parse_args())


# load the image image, convert it to grayscale, and detect edges
pattern_img = Image.open('tmp/mana3.png') 
template = np.array(pattern_img.convert('L'))
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
cv2.imshow("Template", template)

# loop over the images to find the template in
# load the image, convert it to grayscale, and initialize the
# bookkeeping variable to keep track of the matched region
image = cv2.imread('tmp/Sample10.png')
(cH, cW) = image.shape[:2]
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
found = None


# src_scale = 1080 / cH
src_scale = 1
# print(cH)

# loop over the scales of the image
for scale in np.linspace(src_scale * 0.9, src_scale * 1.1, 10)[::-1]:
    # resize the image according to the scale, and keep track
    # of the ratio of the resizing
    resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
    r = gray.shape[1] / float(resized.shape[1])
    # if the resized image is smaller than the template, then break
    # from the loop
    if resized.shape[0] < tH or resized.shape[1] < tW:
        break

    # detect edges in the resized, grayscale image and apply template
    # matching to find the template in the image
    edged = cv2.Canny(resized, 50, 200)
    result = cv2.matchTemplate(edged, template, cv2.TM_SQDIFF_NORMED)
    (min_val, maxVal, _, maxLoc) = cv2.minMaxLoc(result)


    clone = np.dstack([edged, edged, edged])
    print(min_val, maxVal)
    # create threshold from min val, find where sqdiff is less than thresh
    match_locations = np.where(result<=0.9)
    # print(scale, len(match_locations))

    for (x, y) in zip(match_locations[1], match_locations[0]):
        print("Here", scale, x, y)
        cv2.rectangle(clone, (x, y), (x + tW, y + tH), (0, 0, 255), 2)

    # result2 = np.reshape(result, result.shape[0]*result.shape[1]) 
    # # print(result2)
    # sort = np.argsort(result2)
    # # print(len(sort))
    # for i in range(len(match_locations)):
    # #     print(sort[i])
    #     (y1, x1) = np.unravel_index(sort[i], result.shape)
    #     cv2.rectangle(clone, (x1, y1), (x1 + tW, y1 + tH), (0, 0, 255), 2)
    cv2.imshow("Visualize", clone)
    cv2.waitKey(0)

    # if we have found a new maximum correlation value, then update
    # the bookkeeping variable
    if found is None or maxVal > found[0]:
        found = (maxVal, maxLoc, r)
# unpack the bookkeeping variable and compute the (x, y) coordinates
# of the bounding box based on the resized ratio
# (_, maxLoc, r) = found
# (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
# (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
# # draw a bounding box around the detected result and display the image
# cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
# cv2.imshow("Image", image)
# cv2.waitKey(0)





# import numpy as np
# import cv2 as cv
# import matplotlib.pyplot as plt
# img1 = cv.imread('tmp/pattern2.png',0)          # queryImage
# img2 = cv.imread('tmp/Sample4.png',0) # trainImage
# # Initiate SIFT detector
# sift = cv.xfeatures2d.SIFT_create()
# # find the keypoints and descriptors with SIFT
# kp1, des1 = sift.detectAndCompute(img1,None)
# kp2, des2 = sift.detectAndCompute(img2,None)
# # FLANN parameters
# FLANN_INDEX_KDTREE = 1
# index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
# search_params = dict(checks=50)   # or pass empty dictionary
# flann = cv.FlannBasedMatcher(index_params,search_params)
# matches = flann.knnMatch(des1,des2,k=2)
# # Need to draw only good matches, so create a mask
# matchesMask = [[0,0] for i in range(len(matches))]
# # ratio test as per Lowe's paper
# for i,(m,n) in enumerate(matches):
#     if m.distance < 0.7*n.distance:
#         matchesMask[i]=[1,0]
# draw_params = dict(matchColor = (0,255,0),
#                    singlePointColor = (255,0,0),
#                    matchesMask = matchesMask,
#                    flags = cv.DrawMatchesFlags_DEFAULT)
# img3 = cv.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)
# plt.imshow(img3,),plt.show()

# import cv2
# from matplotlib import pyplot as plt
# import sklearn

# MIN_MATCH_COUNT = 10

# img1 = cv2.imread('tmp/pattern2.png',0)          # queryImage
# img2 = cv2.imread('tmp/Sample4.png',0) # trainImage


# # img1 = cv2.imread('box.png', 0)  # queryImage
# # img2 = cv2.imread('box1.png', 0) # trainImage

# orb = cv2.ORB_create(10000, 1.2, nlevels=8, edgeThreshold = 5)

# # find the keypoints and descriptors with ORB
# kp1, des1 = orb.detectAndCompute(img1, None)
# kp2, des2 = orb.detectAndCompute(img2, None)

# import numpy as np
# from sklearn.cluster import MeanShift, estimate_bandwidth

# x = np.array([kp2[0].pt])

# for i in range(len(kp2)):
#     x = np.append(x, [kp2[i].pt], axis=0)

# x = x[1:len(x)]

# bandwidth = estimate_bandwidth(x, quantile=0.1, n_samples=500)

# ms = MeanShift(bandwidth=bandwidth, bin_seeding=True, cluster_all=True)
# ms.fit(x)
# labels = ms.labels_
# cluster_centers = ms.cluster_centers_

# labels_unique = np.unique(labels)
# n_clusters_ = len(labels_unique)
# print("number of estimated clusters : %d" % n_clusters_)

# s = [None] * n_clusters_
# for i in range(n_clusters_):
#     l = ms.labels_
#     d, = np.where(l == i)
#     print(d.__len__())
#     s[i] = list(kp2[xx] for xx in d)

# des2_ = des2

# for i in range(n_clusters_):

#     kp2 = s[i]
#     l = ms.labels_
#     d, = np.where(l == i)
#     des2 = des2_[d, ]

#     FLANN_INDEX_KDTREE = 0
#     index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
#     search_params = dict(checks = 50)

#     flann = cv2.FlannBasedMatcher(index_params, search_params)

#     des1 = np.float32(des1)
#     des2 = np.float32(des2)

#     matches = flann.knnMatch(des1, des2, 2)

#     # store all the good matches as per Lowe's ratio test.
#     good = []
#     for m,n in matches:
#         if m.distance < 0.7*n.distance:
#             good.append(m)

#     if len(good)>3:
#         src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
#         dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

#         M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 2)

#         if M is None:
#             print ("No Homography")
#         else:
#             matchesMask = mask.ravel().tolist()

#             h,w = img1.shape
#             pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
#             dst = cv2.perspectiveTransform(pts,M)

#             img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)

#             draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
#                                singlePointColor=None,
#                                matchesMask=matchesMask,  # draw only inliers
#                                flags=2)

#             img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

#             plt.imshow(img3, 'gray'), plt.show()

#     else:
#         print ("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
#         matchesMask = None

# # import numpy as np
# # import cv2
# # from matplotlib import pyplot as plt
# # import numpy as np
# # from PIL import Image, ImageOps, ImageEnhance, ImageFilter


# # def ocr_filter_img(im):
# #     if im == None:
# #         return im
# #     dat = im.getdata()
# #     f = []
# #     for d in dat:
# #         if d[0] >= 254 and d[1] >= 254 and d[2] >= 254: #chp catk
# #             f.append((0,0,0))
# #         elif d[0] <= 28 and d[1] == 255 and d[2] <= 80: #chp catk boost
# #             f.append((0,0,0))
# #         elif d[0] == 255 and d[1] <=2 and d[2] <=2: #chp catk malus
# #             f.append((0,0,0))
# #         elif d[0] <= 179 and d[0] >= 164 and d[1] <= 230 and d[1] >= 211 and d[2] >= 233: #smana
# #             f.append((0,0,0))
# #         elif d[0] <= 205 and d[0] >= 175 and d[1] <= 220 and d[1] >= 190 and d[2] <= 235 and d[2] >= 215: #mana
# #             f.append((0,0,0))
# #         elif d[0] == 245 and d[1] == 245 and d[2] == 250: #hp
# #             f.append((0,0,0))
# #         elif d[0] == 246 and d[1] == 227 and d[2] == 227: #card cost
# #             f.append((0,0,0))
# #         else:
# #             f.append((255,255,255))
# #     im.putdata(f)
# #     im = ImageOps.grayscale(im)
# #     # im = im.filter(ImageFilter.GaussianBlur(4))
# #     # im = ImageOps.invert(im)
# #     return im

# # MIN_MATCH_COUNT = 4
# # # pattern_img = Image.open('assets/hp12.png')
# # # img1 = np.array(pattern_img.convert('L'))

# # # src_img = Image.open('tmp/Sample3.png')
# # # img2 = ocr_filter_img(src_img)
# # # img2 = np.array(img2.convert('L'))

# # img1 = cv2.imread('tmp/pattern2.png',0)          # queryImage
# # img2 = cv2.imread('tmp/Sample4.png',0) # trainImage

# # # Initiate SIFT detector
# # sift = cv2.xfeatures2d.SIFT_create()
# # # find the keypoints and descriptors with SIFT
# # kp1, des1 = sift.detectAndCompute(img1,None)
# # kp2, des2 = sift.detectAndCompute(img2,None)
# # FLANN_INDEX_KDTREE = 1
# # index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
# # search_params = dict(checks = 50)
# # flann = cv2.FlannBasedMatcher(index_params, search_params)
# # matches = flann.knnMatch(des1,des2,k=2)
# # # store all the good matches as per Lowe's ratio test.
# # good = []
# # for m,n in matches:
# #     if m.distance < 0.7*n.distance:
# #         good.append(m)

# # if len(good)>MIN_MATCH_COUNT:
# #     src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
# #     dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
# #     M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
# #     matchesMask = mask.ravel().tolist()
# #     h,w,d = img1.shape
# #     pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
# #     dst = cv2.perspectiveTransform(pts,M)
# #     img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)
# # else:
# #     print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
# #     matchesMask = None

# # draw_params = dict(matchColor = (0,255,0), # draw matches in green color
# #                    singlePointColor = None,
# #                    matchesMask = matchesMask, # draw only inliers
# #                    flags = 2)
# # img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
# # plt.imshow(img3, 'gray'),plt.show()


# # # import json

# # # ar = {}
# # # file = open("export.csv","w+") 
# # # with open('set1-en_us.json', encoding="utf8") as json_file:
# # #     for p in json.load(json_file):
# # #         # str = p["type"]
# # #         # for str in p["spellSpeed"]:
# # #         # file.writep(p["cardCode"], "\t", p["type"], "\t", p["name"], "\t", p["cost"],"\t", p["health"],"\t", p["attack"],"\t", p["SpellSpeed"], "\t", )
# # #         file.write(p["type"] + "\t" + p["descriptionRaw"].replace("\r\n",",") + "\n")
# # #         ar[str] = None

# # # file.close()
# # # print(ar.keys())


# # # from scapy.all import *
# # # sniff(filter="ip", prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}"))

# # # items = [1,1,3,4,5]
# # # knapsack = []
# # # limit = 7

# # # def print_solutions(current_item, knapsack, current_sum):
# # #     #if all items have been processed print the solution and return:
# # #     if current_item == len(items):
# # #         print(knapsack)
# # #         return

# # #     #don't take the current item and go check others
# # #     print_solutions(current_item + 1, list(knapsack), current_sum)

# # #     #take the current item if the value doesn't exceed the limit
# # #     if (current_sum + items[current_item] <= limit):
# # #         knapsack.append(items[current_item])
# # #         current_sum += items[current_item]
# # #         #current item taken go check others
# # #         print_solutions(current_item + 1, knapsack, current_sum )

# # # print_solutions(0,knapsack,0)


# # # from __future__ import print_function
# # # from ortools.algorithms import pywrapknapsack_solver


# # # def main():
# # #     # Create the solver.
# # #     solver = pywrapknapsack_solver.KnapsackSolver(
# # #         pywrapknapsack_solver.KnapsackSolver.
# # #         KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')

# # #     values = [
# # #         1,1,1,2,1,2
# # #     ]
# # #     weights = [[
# # #        2,2,2,4,2,4
# # #     ]]
# # #     capacities = [6]

# # #     solver.Init(values, weights, capacities)
# # #     computed_value = solver.Solve()

# # #     packed_items = []
# # #     packed_weights = []
# # #     total_weight = 0
# # #     print('Total value =', computed_value)
# # #     for i in range(len(values)):
# # #         if solver.BestSolutionContains(i):
# # #             packed_items.append(i)
# # #             packed_weights.append(weights[0][i])
# # #             total_weight += weights[0][i]
# # #     print('Total weight:', total_weight)
# # #     print('Packed items:', packed_items)
# # #     print('Packed_weights:', packed_weights)

# # #     # solver.


# # # if __name__ == '__main__':
# # #     main()
