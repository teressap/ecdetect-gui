### This module will draw contour and return the labeled image

from tkinter import *
from tkinter import filedialog 
from PIL import Image 
from PIL import ImageTk
import cv2
import numpy as np

thresh = 160
BG = np.array([255,255,255])
CHR = np.array([0,128,128])
CELL = np.array([0,0,255])
SEARCH = np.array([0,165,255])

####
# takes binarized image and return the labeled image
####
def find_contour(image, gray):
	## find contours in image
	im2, contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	## exclude the outmost contours ##
	display = np.empty_like(contours)
	small = np.empty_like(contours)
	cnt_area = np.arange(0)
	cnt_centroid = np.arange(0)
	idx = 0
	idx_small = 0

	## eliminate unwanted contours (outmost)
	for cnt in contours:
		area = cv2.contourArea(cnt)
		if 0 < area < 200:
			small[idx_small] = cnt
			idx_small += 1
		if 200 <= area < 30000:
			M = cv2.moments(cnt)
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
			display[idx] = cnt
			cnt_area = np.append(cnt_area, area)
			cnt_centroid = np.append(cnt_centroid, (cx,cy))
			idx += 1

	gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
	cv2.drawContours(gray, display, -1, (0,255,0),thickness = -1)
	cv2.drawContours(gray, small, -1, (0,0,0),thickness = -1)

	## initialize label_im ##
	label_im = np.zeros_like(gray)
	white = np.array([255,255,255])
	green = np.array([0,255,0])
	for i in range(len(gray)):
		for j in range(len(gray[i])):
			if (gray[i,j] == white).all():
				label_im[i,j] = BG
			elif (gray[i,j] == green).all():
				label_im[i,j] = CHR
			elif (gray[i,j] == np.array([0,255,255])).all():
				label_im[i,j] = SEARCH
			else:
				label_im[i,j] = CELL

	## fuse two images together
	mixed = cv2.addWeighted(image, 1, label_im, 0.5, 0.0)  ## -> return value
	return mixed, label_im

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
