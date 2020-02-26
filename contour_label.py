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
CHR = [0,128,128]
NUCLEUS = [0,0,255]
SEARCH = [255,140,0]

solidity_cutoff = 0.8

MAX_SIZE = 400000

EC_size_thresh_RELAX = 75
EC_min_size = 0

MED_COMP_SIZE = 100
CHR_NEAR_DILATION = 15
CHR_size_thresh = 8000

EC_CIRCLING_SIZE = 20
EC_CIRCLING_WIDTH = 10

search = 0

class ContourLabel:

	# original label
	label_im = 0

	# new label
	new_label = 0

	# contour vectors
	chr = 0
	nucleus = 0
	border_nucleus = 0
	search = 0
	small = 0

	# source image
	gray = 0

 
	# -------------------------------------------------------
	# Initialize object with contours 
	# -------------------------------------------------------
	def __init__(self, gray):
		self.find_contour(gray)
		self.dilate()
		self.gray = gray
		self.new_label = self.label_im.copy()


	# -------------------------------------------------------
	# Reset All 
	# -------------------------------------------------------
	def resetAll(self):
		self.find_contour(self.gray)
		self.dilate()
		self.new_label = self.label_im.copy()

	# -------------------------------------------------------
	# recompute search region and put all contours together 
	# -------------------------------------------------------
	def repaint(self, label):
		# compute search region
		search_label = self.search_region()
		search_label = cv2.cvtColor(search_label, cv2.COLOR_BGR2GRAY)
		im2, self.search, hierarchy = cv2.findContours(search_label, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		cv2.drawContours(label, self.search, -1, SEARCH,thickness = -1)

		# add label and draw border for dilation
		cv2.drawContours(label, self.chr, -1, CHR,thickness = -1)
		cv2.drawContours(label, self.nucleus, -1, NUCLEUS,thickness = -1)
		cv2.drawContours(label, self.border_nucleus, -1, NUCLEUS, thickness = -1)


	# -------------------------------------------------------
	# recompute chromosomal and nucleus contours
	# -------------------------------------------------------
	def recompute(self):
		# recompute chr region from new label image
		chr_only = np.zeros_like(self.label_im)
		chr_only [self.new_label == CHR] = self.new_label [self.new_label == CHR]
		chr_only = cv2.cvtColor(chr_only, cv2.COLOR_RGB2GRAY)
		im2, self.chr, hierarchy = cv2.findContours(chr_only, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

		# recompute nucleus region
		nu_only = np.zeros_like(self.label_im)
		nu_only [self.new_label == NUCLEUS] = self.new_label [self.new_label == NUCLEUS]
		nu_only = cv2.cvtColor(nu_only, cv2.COLOR_RGB2GRAY)
		im2, self.nucleus, hierarchy = cv2.findContours(nu_only, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

		self.new_label = np.empty_like(self.new_label)
		self.repaint(self.new_label)

	# -------------------------------------------------------
	# Dilate original label image
	# -------------------------------------------------------
	def dilate(self):
		cv2.drawContours(self.label_im, self.chr, -1, CHR,thickness = 5)
		cv2.drawContours(self.label_im, self.nucleus, -1, NUCLEUS,thickness = 15)
		cv2.drawContours(self.label_im, self.border_nucleus, -1, NUCLEUS, thickness = 15)

	# -------------------------------------------------------
	# find contours in given binary image
	# -------------------------------------------------------
	def find_contour(self,gray):
		## find contours in image
		im2, contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		# border contour
		im2, border, hierarchy_out = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

		self.nucleus = np.empty_like(contours)
		self.chr = np.empty_like(contours)
		self.small = np.empty_like(contours)

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
			# solid and large are nucleuss
			if solidity > solidity_cutoff and CHR_size_thresh < area < MAX_SIZE:
				self.nucleus[idx] = hull
				idx += 1
			# solid and median are chrs
			elif MED_COMP_SIZE < area < CHR_size_thresh:
				self.chr[idx_ch] = cnt
				idx_ch += 1
			elif EC_min_size < area < 100:
				self.small[idx_ch] = cnt
				idx_ch += 1

		# find border components and add them to nucleuss
		self.border_nucleus = np.empty_like(border)
		idx_b = 0
		for b in border:
			area = cv2.contourArea(b)
			hull = cv2.convexHull(b)
			hull_area = cv2.contourArea(hull)
			if area < MAX_SIZE: # exclude the outmost contour
				self.border_nucleus[idx_b] = hull
				idx_b+=1
		self.label_im = np.zeros_like(gray)

		self.repaint(self.label_im)


	# -------------------------------------------------------
	# create a convex hull around close connected chromosomes
	# -------------------------------------------------------
	def search_region(self):

		D_near = 150

		search_label = np.empty_like(self.label_im)
		chr_center = []
		dist = []

		# get centroid of chrs
		for cnt in self.chr:
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
		search_label = np.zeros_like(self.label_im)
		cv2.drawContours(search_label, extracted_cluster, -1, SEARCH, thickness=-1)

		kernel = np.ones((100,100),np.uint8)
		search_label = cv2.dilate(search_label,kernel,iterations = 1)

		return search_label

	def detect_EC(self, thresh):

		im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

		circles = []
		# ori_image = cv2.cvtColor(ori_image, cv2.COLOR_GRAY2RGB)
		for cnt in contours:
			area = cv2.contourArea(cnt)
			hull = cv2.convexHull(cnt)
			hull_area = cv2.contourArea(hull)
			M = cv2.moments(cnt)
			if M['m00'] == 0:
				continue
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
			if ((self.new_label[cy][cx] == np.array(SEARCH)).all()) and EC_min_size < area < 100:
				circles.append((cx,cy))

		# circles = []

		# for cnt in self.small:

		# 	M = cv2.moments(cnt)
		# 	if M['m00'] == 0:
		# 		continue
		# 	cx = int(M['m10']/M['m00'])
		# 	cy = int(M['m01']/M['m00'])
		# 	if ((self.new_label[cy][cx] == np.array(SEARCH)).all()):
		# 		circles.append((cx,cy))

		# for center in circles:
		# 	cv2.circle(image, center, 8, [255,0,0], thickness=2)
		# 	cv2.circle(ori_image, center, 8, [255,0,0], thickness=2)

		return circles

	####
	# Takes a label_im 2-d array and modify points specified through parameter
	####
	def add_label(self, points, arg):
		if arg == "chr":
			arg = CHR
		if arg == "nucleus":
			arg = NUCLEUS

		points = [[points[i], points[i+1]] for i in range(0,len(points),2)]
		points = np.array(points, np.int32)

		cv2.fillPoly(self.new_label, [points], tuple(arg))

		self.recompute()

		# cv2.fillPoly(self.new_label, [points], tuple(arg))

		return self.new_label

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
