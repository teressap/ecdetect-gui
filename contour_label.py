### This module will draw contour and return the labeled image

from tkinter import *
from tkinter import filedialog 
from PIL import Image 
from PIL import ImageTk
import cv2
import numpy as np
from scipy import sparse
from scipy import stats

thresh = 160
BG = np.array([255,255,0])
CHR = [0,128,128]
CHR_label = (255,0,0)
CELL = [0,0,255]
CELL_label = (0,255,0)
SEARCH = np.array([255,140,0])

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
	im2, border, hierarchy_out = cv2.findContours(gray, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # border contour

	cell = np.empty_like(contours)
	chr = np.empty_like(contours)
	small = np.empty_like(contours)
	ignore = np.empty_like(contours)
	search = []

	gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

	idx = 0
	idx_ch = 0

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
	label_im = np.zeros_like(gray)

	label_im = search_region(label_im, chr)

	cv2.drawContours(label_im, chr, -1, CHR,thickness = -1)
	kernel = np.ones((5,5),np.uint8)
	label_im = cv2.erode(label_im,kernel,iterations = 1)
	cv2.drawContours(label_im, cell, -1, CELL,thickness = -1)
	cv2.drawContours(label_im, border1, -1, CELL, thickness = -1)
	# mixed = image + label_im * 0.5
	# mixed = cv2.addWeighted(image, 1, label_im, 1, 1)  ## -> return value


	return label_im

# create a convex hull around close connected chromosomes
def search_region(label_im, chr):

	D_near = 150

	search_label = np.empty_like(label_im)
	chr_center = []
	dist = []

	# get centroid of chrs
	for cnt in chr:
		M = cv2.moments(cnt)
		if M['m00'] == 0:
			continue
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
		chr_center.append((cx,cy))

	x = []
	y = []

	# compute distence
	for i in range(len(chr_center)):
		cx = chr_center[i][0]
		cy = chr_center[i][1]
		for j in range(i+1, len(chr_center)):
			dx = chr_center[j][0]
			dy = chr_center[j][1]
			d = ((cx-dx)**2+(cy-dy)**2)**0.5
			if d < D_near:
				x.append(i)
				y.append(j)
				dist.append(d)

	# find weakly connected components
	comp = sparse.csr_matrix((dist, (x,y)),shape=(len(chr_center),len(chr_center)))
	[S,C] = sparse.csgraph.connected_components(comp)

	# find the largest cluster
	condition = np.argwhere(C == stats.mode(C)[0][0]).flatten().tolist()

	# extract positions and draw contour
	extracted_cluster = [cv2.convexHull(np.array([list(chr_center[i]) for i in condition]))]
	cv2.drawContours(label_im, extracted_cluster, -1, SEARCH.tolist(), thickness=-1)

	kernel = np.ones((100,100),np.uint8)
	label_im = cv2.dilate(label_im,kernel,iterations = 1)

	# cv2.imshow("aaa",label_im)
	# cv2.waitKey(5000)
	# cv2.destroyAllWindows()

	return label_im

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
	cv2.fillPoly(tmp, [points], tuple(arg))
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
