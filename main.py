from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
from contour_label import ContourLabel
import shape_util as sh
from bradley import bradley


#---------------------------#
#      GLOBAL VARIABLES     #
#---------------------------#
path = 'M14_004.tif'
# path='PC3_Ctrl_003.tif'

# gui display window
ypad = 50
window_size = 1200

# layers of display
curr_label = 0
orig_image = 0
circles = 0
blended = 0

# intermediate images
thresh_img = 0

# Detected ECs
ec_count = 0

# GUI variables
panelA = 0
panelB = 0
imgA = 0
imgB = 0

#--------------------------#
#       CHANGE LABELS      #
#--------------------------#
def change(arg):
    global panelA, points, img, imgA_handler, imgB_handler, panelB, blended, curr_label, to_save, before_circles, ori_right
    
    # compose new points
    new_points = []
    for p in sh.points:
        new_points.append(p.x)
        new_points.append(p.y)

    if arg == "resetpoly":

        # convert point into [x,y] pair lists
        points = [[new_points[i], new_points[i+1]] for i in range(0,len(new_points),2)]
        points = np.array(points, np.int32)

        # initialize blank canvas
        blank = np.empty_like(curr_label.label_im)
        cv2.fillPoly(blank, [points], (1,1,1))

        # reset polygon region
        curr_label.new_label[blank == (1,1,1)] = curr_label.label_im[blank==(1,1,1)]

        # recompute search region
        curr_label.recompute()

        label = curr_label.new_label

    elif arg == "resetall":

        # get original label
        curr_label.resetAll()
        label = curr_label.label_im

        # delete circles on panelB
        panelB.delete("all")

        # re-pack image on panelB
        img = ImageTk.PhotoImage(orig_image)
        imgB_handler = panelB.create_image((0,0), image = img, anchor = "nw")

    else:
        # add to original labels
        label = curr_label.add_label(new_points,arg)

    # blend again
    label = Image.fromarray(label)
    # label.thumbnail((window_size,window_size))
    # gray = cv2.cvtColor(adj_image, cv2.COLOR_GRAY2RGB)
    # gray = Image.fromarray(gray)
    # gray.thumbnail((window_size,window_size))
    blended = Image.blend(orig_image, label, 0.3)
    # before_circles = np.copy(mixed)
    blended = ImageTk.PhotoImage(blended)

    # delete original img
    panelA.delete("all")
    imgA_handler = panelA.create_image((0,0), image = blended, anchor = "nw")
    sh.reset()
    panelA.bind("<Button-1>", sh.draw)
    return imgA_handler, imgB_handler

#--------------------------#
#   IMAGE PREPROCESSING    #
#--------------------------#

#### read in image and convert to binary ####
def read_im(image, ww, wh, factor = 1): 
    global orig_image, blended

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    # reverse image if necessary
    bw_ratio = np.count_nonzero(image[image < np.mean(image)])/(image.shape[0]*image.shape[1])
    if bw_ratio > 0.5:
        image = (255 - image)
    # clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(20,20))
    # image = clahe.apply(image)

    # set threshold and create binary image
    blended = convert_im(image)

    # thumbnail
    image_resize = Image.fromarray(np.array(orig_image).copy())
    image_resize.thumbnail((ww,wh))
    image_resize = ImageTk.PhotoImage(image_resize) # to Tk

    # original image to tk
    # imageB.thumbnail((window_size,window_size))
    # imageB = ImageTk.PhotoImage(image)
    imageB = ImageTk.PhotoImage(orig_image)

    return imageB, image_resize, blended

#### returns binarized tk photoImage ####
def convert_im(image, threshold = 100):
    global curr_label, orig_image, thresh_img, blended

    # binarize image using bradley method of local thresholding
    gray = bradley(image, 150,150,10)

    # update threshold global variable to suitable size
    thresh_img = np.copy(gray)
    thresh_img = Image.fromarray(thresh_img)
    thresh_img.thumbnail((window_size,window_size))
    thresh_img = np.array(thresh_img)

    # label image for cell and chr and search region
    curr_label = ContourLabel(thresh_img)
    label = Image.fromarray(curr_label.label_im)

    # shrink images
    orig_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    orig_image = Image.fromarray(orig_image)
    orig_image.thumbnail((window_size,window_size))


    # label.thumbnail((window_size,window_size))
    # curr_label = np.array(label)
    # origin = np.copy(curr_label)

    # blend
    blended = Image.blend(orig_image, label, 0.3)
    # before_circles = np.copy(gray)

    blended = ImageTk.PhotoImage(blended)
    return blended


def detect_ECs():
    global imgB_handler, img, blended, imgA_handler, orig_image 

    # detect ECs
    new_thresh = cv2.cvtColor(np.array(orig_image), cv2.COLOR_BGR2GRAY)
    new_thresh = bradley(new_thresh)
    circles = curr_label.detect_EC(new_thresh)
    print(circles)

    # re-create image for panel A
    label = Image.fromarray(curr_label.new_label)
    blended = Image.blend(orig_image, label, 0.3)
    blended = np.array(blended)

    # re-create image for panel B
    img = np.array(orig_image)

    # draw circles
    num = 0
    for center in circles:
        cv2.circle(blended, center, 8, [255,0,0], thickness=2)
        cv2.circle(img, center, 8, [255,0,0], thickness=2)
        num += 1

    # reset panelA
    blended = Image.fromarray(blended)
    blended = ImageTk.PhotoImage(blended)
    panelA.delete("all")
    imgA_handler = panelA.create_image((0,0), image = blended, anchor = "nw")
    sh.reset()
    panelA.bind("<Button-1>", sh.draw)

    # reset panelB
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    panelB.delete("all")
    imgB_handler = panelB.create_image((0,0), image = img, anchor = "nw")

    print("number of ECs: " + str(num))


def clear_ECs():
    global blended, orig_image,imgB_handler, img
    # re-create panelA image
    label = Image.fromarray(curr_label.label_im)
    blended = Image.blend(orig_image, label, 0.3)
    blended = ImageTk.PhotoImage(blended)

    # reset panelA
    panelA.delete("all")
    imgA_handler = panelA.create_image((0,0), image = blended, anchor = "nw")
    sh.reset()
    panelA.bind("<Button-1>", sh.draw)

    # reset panelB
    img = ImageTk.PhotoImage(orig_image)
    panelB.delete("all")
    imgB_handler = panelB.create_image((0,0), image = img, anchor = "nw")

#--------------------------#
#      GUI FUNCTIONS       #
#--------------------------#
# scroll at the same time #
def scroll_x(*args):
    panelA.xview(*args)
    panelB.xview(*args)

## scroll at the same time #
def scroll_y(*args):
    panelA.yview(*args)
    panelB.yview(*args)

# terminates program #
def quit_prog():
    global root
    root.destroy()

# Mark selected as chromosomal region #
def chr_area():
    change("chr")

# Mark selected as cell region #
def mask():
    change("nucleus")

# Reset selected region #
def reset_poly():
    change("resetpoly")

def reset_all():
    change("resetall")

def discard():
    quit_prog()

def save():
    quit_prog()

#--------------------------#
#         MAIN LOOP        #
#--------------------------#
root = Tk()

image = cv2.imread(path)

img, img_small, mixed = read_im(image, 240, 300)

w = 1440
h = 800
rw = img_small.width()
rh = img_small.height()

# defind root height and width
root.geometry("%dx%d" % (rw, rh))
root.resizable(0,0)

# new window with parallel large images
new = Toplevel()
x = root.winfo_x()
y = root.winfo_y()
new.title("Select Polygon")
new.geometry("%dx%d%+d%+d" % (w,h,x + 50,y+50))
new.resizable(0,0)

# put thumbnail in root
thumb = Label(root, image = img_small)
thumb.pack()

frameA = Frame(new)
frameA.grid(row = 0, column = 0, columnspan = 3, rowspan = 5)

# create scrollbars
scx_A = Scrollbar(frameA, orient = HORIZONTAL, command=scroll_x)
scx_A.grid(row=1, column=0, columnspan=4, sticky=E+W)

scy_A = Scrollbar(frameA, orient = VERTICAL, command=scroll_y)
scy_A.grid(row=0, column=4, sticky=N+S)

scx_B = Scrollbar(frameA, orient = HORIZONTAL, command=scroll_x)
scx_B.grid(row=1, column=5, columnspan=4, sticky=E+W)

scy_B = Scrollbar(frameA, orient = VERTICAL, command=scroll_y)
scy_B.grid(row=0, column=9, sticky=N+S)

# put the other two side by side on two scrollable canvases
panelA = Canvas(frameA, width=w//2-20, height=h-70,
                scrollregion=(0,0,img.width(),img.height()),
                xscrollcommand=scx_A.set,
                yscrollcommand=scy_A.set)
panelA.grid(row=0, column=0, columnspan=4)
imgA_handler = panelA.create_image((0,0), image = mixed, anchor = "nw")

# bind mouse event
panelA.bind("<Button-1>", sh.draw)

panelB = Canvas(frameA, width=w//2-20, height=h-70,
                scrollregion=(0,0,img.width(),img.height()),
                xscrollcommand=scx_B.set,
                yscrollcommand=scy_B.set)
panelB.grid(row=0, column=5, columnspan=4)
imgB_handler = panelB.create_image((0,0), image = img, anchor = "nw")

# BUTTONS #
frameB = Frame(new)
frameB.grid(row=5,column=0)

quit_button = Button(frameB, text = "Quit", command = quit_prog)
quit_button.grid(row = 5, column=0, padx=20, pady=10)

chr_button = Button(frameB, text = "Chr", command = chr_area)
chr_button.grid(row = 5, column=2, padx=20, pady=10)

mask_button = Button(frameB, text = "Mask", command = mask)
mask_button.grid(row = 5, column=3, padx=20, pady=10)

reset_poly_button = Button(frameB, text = "Reset Polygon", command = reset_poly)
reset_poly_button.grid(row = 5, column=4, padx=20, pady=10)

reset_all_button = Button(frameB, text = "Reset All", command = reset_all)
reset_all_button.grid(row = 5, column=5, padx=20, pady=10)

detect_button = Button(frameB, text = "Detect ECs", command = detect_ECs)
detect_button.grid(row = 5, column=6, padx=20, pady=10)

clear_button = Button(frameB, text = "Clear ECs", command = clear_ECs)
clear_button.grid(row = 5, column=7, padx=20, pady=10)

discard_button = Button(frameB, text = "Discard", command = change)
discard_button.grid(row = 5, column=8, padx=20, pady=10)

continue_button = Button(frameB, text = "Continue", command = save)
continue_button.grid(row = 5, column=9, padx=20, pady=10)

root.mainloop()

