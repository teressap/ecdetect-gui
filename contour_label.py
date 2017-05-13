### This module will draw contour and return the labeled image

from tkinter import *
from tkinter import filedialog 
from PIL import Image 
from PIL import ImageTk
import cv2
import numpy as np

thresh = 160
BG = np.array([255,255,0])
CHR = np.array([0,128,128])
CHR_label = (255,0,0)
CELL = np.array([0,0,255])
CELL_label = (0,255,0)
SEARCH = np.array([0,165,255])

solidity_cutoff = 0.8

MAX_SIZE = 400000

EC_size_thresh_RELAX = 75
EC_min_size = 3

MED_COMP_SIZE = 200
CHR_NEAR_DILATION = 15
CHR_size_thresh = 4000

EC_CIRCLING_SIZE = 20
EC_CIRCLING_WIDTH = 10

####
# takes binarized image and return the labeled image
####
def find_contour(image, gray):
	## find contours in image
	im2, contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	im2, border, hierarchy_out = cv2.findContours(gray, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

	cell = np.empty_like(contours)
	chr = np.empty_like(contours)
	small = np.empty_like(contours)
	ignore = np.empty_like(contours)
	search = []

	gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

	idx = 0
	idx_ch = 0
	idx_small = 0
	idx_ig = 0
	for cnt in contours:
		area = cv2.contourArea(cnt)
		hull = cv2.convexHull(cnt)
		hull_area = cv2.contourArea(hull)
		solidity = 0
		if hull_area != 0:
			solidity = float(area)/hull_area

		# solid and large are cells
		if solidity > solidity_cutoff and CHR_size_thresh < area < MAX_SIZE:
			cell[idx] = hull
			idx += 1
		# solid and median are chrs
		elif MED_COMP_SIZE < area < CHR_size_thresh:
			chr[idx_ch] = cnt
			idx_ch += 1
			(x,y),radius = cv2.minEnclosingCircle(cnt)
			center = (int(x),int(y))
			search.append(center)

	# find border components and add them to cells
	border1 = np.empty_like(border)
	idx_b = 0
	for b in border:
		area = cv2.contourArea(b)
		hull = cv2.convexHull(b)
		hull_area = cv2.contourArea(hull)
		if area < MAX_SIZE:
			border1[idx_b] = hull
			idx_b+=1

	cv2.drawContours(gray, chr, -1, CHR_label,thickness = -1)
	cv2.drawContours(gray, cell, -1, CELL_label,thickness = -1)
	# cv2.drawContours(gray, contours, -1, (0,255,0),thickness = 1)
	cv2.drawContours(gray, border1, -1, CELL_label, thickness = -1)

	label_im = np.zeros_like(gray)
	for i in range(len(gray)):
		for j in range(len(gray[i])):
			if (gray[i,j] == np.array(CELL_label)).all():
				label_im[i,j] = CELL
			elif (gray[i,j] == np.array(CHR_label)).all():
				label_im[i,j] = CHR
			elif (gray[i,j] == np.array([0,255,255])).all():
			 	label_im[i,j] = SEARCH
			else:
				label_im[i,j] = np.array([0,0,0])

	mixed = cv2.addWeighted(image, 1, label_im, 0.6, 0.0)  ## -> return value

	return mixed, 0 

	# print(len(contours))

	# ## exclude the outmost contours ##
	# display = np.empty_like(contours)
	# small = np.empty_like(contours)
	# ignore = np.empty_like(contours)
	# cnt_area = np.arange(0)
	# cnt_centroid = np.arange(0)
	# idx = 0
	# idx_small = 0
	# idx_ig = 0

	# ## eliminate unwanted contours (outmost)
	# for cnt in contours:
	# 	area = cv2.contourArea(cnt)
	# 	if 10 < area < 100:
	# 		small[idx_small] = cnt
	# 		idx_small += 1
	# 	if 100 <= area < 30000:
	# 		M = cv2.moments(cnt)
	# 		cx = int(M['m10']/M['m00'])
	# 		cy = int(M['m01']/M['m00'])
	# 		display[idx] = cnt
	# 		cnt_area = np.append(cnt_area, area)
	# 		cnt_centroid = np.append(cnt_centroid, (cx,cy))
	# 		idx += 1
	# 	if area <= 10:
	# 		ignore[idx_ig] = cnt
	# 		idx_ig += 1

	# gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
	# cv2.drawContours(gray, display, -1, (0,255,0),thickness = -1)
	# cv2.drawContours(gray, small, -1, (255,0,0),thickness = -1)
	# cv2.drawContours(gray, ignore, -1, (255,255,255), thickness = -1)

	# # initialize label_im ##


	# ## fuse two images together
	# return mixed, label_im

####
# Takes a label_im 2-d array and modify points specified through parameter
####
def add_label(label_im, points, arg):
	if arg == "chr":
		arg = CHR
	if arg == "cell":
		arg = CELL
	tmp = label_im.copy()	
	points = [[points[i], points[i+1]] for i in range(0,len(points),2)]
	points = np.array(points, np.int32)
	cv2.fillPoly(tmp, [points], tuple(arg.tolist()))
	return tmp

def main():
	root = Tk()

	image = cv2.imread("M14_004.tif")

	thre = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	tmp, gray = cv2.threshold(thre, thresh, 255, cv2.THRESH_BINARY)

	mixed = find_contour(image,gray)

	image = cv2.cvtColor(mixed, cv2.COLOR_BGR2RGB)
	image = Image.fromarray(image)
	image.thumbnail((800,800))
	image = ImageTk.PhotoImage(image)

	thumb = Label(root, image = image)
	thumb.pack()

	root.mainloop()

if __name__ == "__main__":
	main()
