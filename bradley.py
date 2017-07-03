#####
# This file contains all the functions in python version of bradley local 
# thresholding method.
#####

from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np

####
# Bradley performs local thresholding of a two-dimensional array image. 
# Image pixel is set to black if its brightness is T percent lower than 
# the average brightness of surrounding pixels in the window of specified 
# size (default 15 x 15).
# The padding method is BORDER_REPLICATE.
#------
def bradley(image, m=15, n=15, T=10):
	out_im = np.full_like(image,255)
	mean = average_filter(image, m, n)
	out_im[image<=mean*(1-T/100)] = 0
	return out_im

####
# Outputs matrix where pixel contains the mean value of m x n neighborhood
# around the corresponding pixel in input image.
#------
def average_filter(image, m, n):
	# pad the image
	border = cv2.copyMakeBorder(image, top=(m+1)//2, bottom=(m-1)//2+1, left=(n+1)//2, right=(n-1)//2+1, borderType=cv2.BORDER_REPLICATE)
	
	# integral of image
	t = np.cumsum(np.cumsum(border,axis=1),axis=0)

	# Get sum for each window and take average
	rows, columns = image.shape
	mean = (t[m:rows+m, n:columns+n] + t[0:rows, 0:columns] - t[m:rows+m, 0:columns] - t[0:rows, n:columns+n]) / (m*n)

	return mean

####
# tester
#------
if __name__ == "__main__":
	path = "./M14_004.tif"
	image = cv2.imread(path)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	thres = bradley(image,m=150,n=150)

	cv2.imshow('image',thres)
	cv2.waitKey(5000)
	cv2.destroyAllWindows()