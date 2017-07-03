from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
import contour_label as cnt
import shape_util as sh
from bradley import bradley

path = "M14_004.tif"
# path = "PC3_Ctrl_003.tif"
ypad = 50
thres = 0

# current label
curr_label = 0
# origin label before manual selection
origin = 0
# size of display window
window_size = 960
# image with EC circles
circles_left = 0
circles_right = 0

# image before EC circles with labels in BGR
before_circles = 0
ori_right = 0

# lable array to save
to_save = 0
# number of ECs
EC_count = 0

adj_image = 0

###
# Change labels
###
def change(arg):
    global panelA, points, imgA, imgB, panelB, mixed, curr_label, to_save, before_circles, ori_right
    # compose new points
    new_points = []
    for p in sh.points:
        new_points.append(p.x)
        new_points.append(p.y)
    if arg == "resetpoly":
        points = [[new_points[i], new_points[i+1]] for i in range(0,len(new_points),2)]
        points = np.array(points, np.int32)
        # initialize blank canvas
        blank = np.empty_like(curr_label)
        cv2.fillPoly(blank, [points], (1,1,1))
        # reset polygon region
        curr_label[blank == (1,1,1)] = origin[blank==(1,1,1)]
    elif arg == "resetall":
        curr_label = origin
        ori_right = Image.fromarray(adj_image)
        ori_right.thumbnail((window_size,window_size))
        ori_right = ImageTk.PhotoImage(ori_right)
        panelB.delete("all")
        imgB = panelB.create_image((0,0), image = ori_right, anchor = "nw")
    else:
        # add to original labels
        label_im = cnt.add_label(curr_label, new_points, arg)
        curr_label = label_im

    to_save = curr_label

    # blend again
    label = Image.fromarray(curr_label)
    label.thumbnail((window_size,window_size))
    gray = cv2.cvtColor(adj_image, cv2.COLOR_GRAY2RGB)
    gray = Image.fromarray(gray)
    gray.thumbnail((window_size,window_size))
    mixed = Image.blend(gray, label, 0.3)
    before_circles = np.copy(mixed)
    mixed = ImageTk.PhotoImage(mixed)

    # delete original img
    panelA.delete("all")
    imgA = panelA.create_image((0,0), image = mixed, anchor = "nw")
    sh.reset()
    panelA.bind("<Button-1>", sh.draw)
    return imgA, imgB

def delete():
    global panelA,imgA
    # reset points and shapes arrays
    sh.points = []
    sh.shape = 0
    panelA.delete("all")
    panelA.bind("<Button-1>", sh.draw)
    # put image back
    imgA = panelA.create_image((0,0), image = orig_mix, anchor = "nw")

#### read in image and convert that to binary ####
def read_im(image, ww, wh, factor = 1):
    global adj_image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bw_ratio = np.count_nonzero(image[image < np.mean(image)])/(image.shape[0]*image.shape[1])
    if bw_ratio > 0.5:
        image = (255 - image)
    # clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(8,8))
    # image = clahe.apply(image)
    adj_image = np.copy(image)

    # set threshold and create binary image
    gray = convert_im(image, thres)

    # cv to PIL
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)

    # thumbnail
    image_resize = image.copy()
    image_resize.thumbnail((ww,wh))
    image_resize = ImageTk.PhotoImage(image_resize) # to Tk

    # original image to tk
    image.thumbnail((window_size,window_size))
    image = ImageTk.PhotoImage(image)

    return image, image_resize, gray

#### returns binarized tk photoImage ####
def convert_im(image, threshold = 100):
    global curr_label, origin, thresh, before_circles
    # median = np.median(image)
    # ret,gray = cv2.threshold(image,median-20,255,cv2.THRESH_TRUNC)
    # gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,25,2)

    gray = bradley(image, 150,150,10)

    # update threshold global variable
    thresh = np.copy(gray)
    thresh = Image.fromarray(thresh)
    thresh.thumbnail((window_size,window_size))
    thresh = np.array(thresh)

    # label image for cell and chr and search region
    curr_label= cnt.find_contour(image, gray)

    # shrink images
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    gray = Image.fromarray(image)
    gray.thumbnail((window_size,window_size))
    label = Image.fromarray(curr_label)
    label.thumbnail((window_size,window_size))
    curr_label = np.array(label)
    origin = np.copy(curr_label)

    # blend
    gray = Image.blend(gray, label, 0.3)
    before_circles = np.copy(gray)

    gray = ImageTk.PhotoImage(gray)
    return gray

#### scroll at the same time ####
def scroll_x(*args):
    panelA.xview(*args)
    panelB.xview(*args)

#### scroll at the same time ####
def scroll_y(*args):
    panelA.yview(*args)
    panelB.yview(*args)

#### terminates program ####
def quit_prog():
    global root
    root.destroy()

#### Mark selected as chromosomal region ####
def chr_area():
    change("chr")

#### Mark selected as cell region ####
def mask():
    change("cell")

#### Reset selected region ####
def reset_poly():
    change("resetpoly")

def reset_all():
    change("resetall")

def discard():
    quit_prog()

def save():
    quit_prog()

def detect_EC():
    global thresh, panelA, imgA, imgB, circles_left, before_circles, EC_count, panelB, circles_right

    tmp = np.copy(before_circles)

    # adjust adj_image size
    ori_image = Image.fromarray(adj_image)
    ori_image.thumbnail((window_size,window_size))
    ori_image = np.array(ori_image)

    # detect EC
    circles_left, EC_count, circles_right= cnt.detect_EC(tmp, thresh, curr_label, ori_image)
    print("Number of ECs: " + str(EC_count))

    # convert circles
    circles_left = Image.fromarray(circles_left)
    circles_left = ImageTk.PhotoImage(circles_left)
    circles_right = Image.fromarray(circles_right)
    circles_right = ImageTk.PhotoImage(circles_right)

    # reset panelA
    panelA.delete("all")
    imgA = panelA.create_image((0,0), image = circles_left, anchor = "nw")
    sh.reset()
    panelA.bind("<Button-1>", sh.draw)
    # reset panelB
    panelB.delete("all")
    imgB = panelB.create_image((0,0), image = circles_right, anchor = "nw")
    return imgA, imgB


def clear_EC():
    global panelA, imgA, imgB, panelB, circles_right, circles_left

    # assign back the origin images
    circles_left= Image.fromarray(before_circles)
    circles_left = ImageTk.PhotoImage(circles_left)
    circles_right = Image.fromarray(adj_image)
    circles_right.thumbnail((window_size,window_size))
    circles_right = ImageTk.PhotoImage(circles_right)

    # delete original img
    panelA.delete("all")
    imgA = panelA.create_image((0,0), image = circles_left, anchor = "nw")
    sh.reset()
    panelA.bind("<Button-1>", sh.draw)
    panelB.delete("all")
    imgB = panelB.create_image((0,0), image = circles_right, anchor = "nw")
    return imgA


root = Tk()

image = cv2.imread(path)

img, img_small, mixed = read_im(image, 240, 300)
orig_mix = mixed
w = 1200
h = 650
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
imgA = panelA.create_image((0,0), image = mixed, anchor = "nw")

# bind mouse event
panelA.bind("<Button-1>", sh.draw)

panelB = Canvas(frameA, width=w//2-20, height=h-70,
                scrollregion=(0,0,img.width(),img.height()),
                xscrollcommand=scx_B.set,
                yscrollcommand=scy_B.set)
panelB.grid(row=0, column=5, columnspan=4)
imgB = panelB.create_image((0,0), image = img, anchor = "nw")

# create frame for buttons
frameB = Frame(new)
frameB.grid(row=5,column=0)

quit_button = Button(frameB, text = "Quit", command = quit_prog)
quit_button.grid(row = 5, column=0, padx=20, pady=10)

quit_button3 = Button(frameB, text = "Chr", command = chr_area)
quit_button3.grid(row = 5, column=2, padx=20, pady=10)

quit_button4 = Button(frameB, text = "Mask", command = mask)
quit_button4.grid(row = 5, column=3, padx=20, pady=10)

quit_button5 = Button(frameB, text = "Reset Polygon", command = reset_poly)
quit_button5.grid(row = 5, column=4, padx=20, pady=10)

quit_button7 = Button(frameB, text = "Reset All", command = reset_all)
quit_button7.grid(row = 5, column=5, padx=20, pady=10)

quit_button8 = Button(frameB, text = "Detect ECs", command = detect_EC)
quit_button8.grid(row = 5, column=6, padx=20, pady=10)

quit_button9 = Button(frameB, text = "Clear ECs", command = clear_EC)
quit_button9.grid(row = 5, column=7, padx=20, pady=10)

quit_button10 = Button(frameB, text = "Discard", command = change)
quit_button10.grid(row = 5, column=8, padx=20, pady=10)

quit_button11 = Button(frameB, text = "Continue", command = save)
quit_button11.grid(row = 5, column=9, padx=20, pady=10)

root.mainloop()
