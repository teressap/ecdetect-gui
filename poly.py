from tkinter import *
from tkinter import filedialog 
from PIL import Image 
from PIL import ImageTk
import cv2
import numpy as np
import contour_label as cnt

path = "M14_004.tif"
thres = 150

#### read in image and convert that to binary ####
def read_im(image, ww, wh, factor = 1):
    # set threshold and create binary image
    gray = convert_im(image, thres)

    # cv to PIL
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)

    # thumbnail
    image_resize = image.copy()
    image_resize.thumbnail((ww,wh))
    image_resize = ImageTk.PhotoImage(image_resize) # to Tk

    # original image to tk
    #image.thumbnail((800*factor,800*factor))
    image = ImageTk.PhotoImage(image)

    return image, image_resize, gray

#### returns binarized tk photoImage ####
def convert_im(image, threshold = 100):
    global orig_label
    thre = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    # ret3,gray = cv2.threshold(thre,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    ret,gray = cv2.threshold(thre,150,255,cv2.THRESH_TRUNC)
    # ret2,gray = cv2.threshold(thre,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,13,2)
    gray, orig_label= cnt.find_contour(image, gray)
    gray = Image.fromarray(gray)
    gray.thumbnail((800,800))
    gray = ImageTk.PhotoImage(gray)
    return gray

root = Tk()
image = cv2.imread(path)
img, img_small, mixed = read_im(image, 240, 300)

# put thumbnail in root
thumb = Label(root, image = mixed)
thumb.pack()

root.mainloop()