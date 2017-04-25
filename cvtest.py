from tkinter import *
from tkinter import filedialog 
from PIL import Image 
from PIL import ImageTk
import cv2
import numpy as np
import tk_example as cnt
import shape_util as sh

path = "M14_004.tif"
ypad = 50
thres = 150
orig_label = 0

# add label
def change(arg):
	global panelA, img, points, imgA, mixed, orig_label
	new_points = []
	for p in sh.points:
		new_points.append(p.x)
		new_points.append(p.y)
	label_im = cnt.add_label(orig_label, new_points, arg)
	orig_label = label_im
	mixed = cv2.addWeighted(image, 1, label_im, 0.5, 0.0)
	mixed = cv2.cvtColor(mixed, cv2.COLOR_BGR2RGB)
	mixed = Image.fromarray(mixed)
	#mixed.thumbnail((800,800))
	mixed = ImageTk.PhotoImage(mixed)
	panelA.delete("all")
	imgA = panelA.create_image((0,0), image = mixed, anchor = "nw")
	sh.reset()
	panelA.bind("<Button-1>", sh.draw)
	return imgA

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
	tmp, gray = cv2.threshold(thre, threshold, 255, cv2.THRESH_BINARY)
	gray, orig_label= cnt.find_contour(image, gray)
	gray = cv2.cvtColor(gray, cv2.COLOR_BGR2RGB)
	gray = Image.fromarray(gray)
	#gray.thumbnail((800,800))
	gray = ImageTk.PhotoImage(gray)
	return gray

#### terminates program ####
def quit_prog():
	global root
	root.destroy()

#### draw polygon ####
def motion(event):
	print (event.x, event.y)

#### scroll at the same time ####
def scroll_x(*args):
	panelA.xview(*args)
	panelB.xview(*args)

#### scroll at the same time ####
def scroll_y(*args):
	panelA.yview(*args)
	panelB.yview(*args)

def chr_area():
	change("chr")

def mask():
	change("cell")

def reset_all():
	pass

def discard():
	pass

def save():
	pass


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
scx_A.grid(row=1, column=0, columnspan=2, sticky=E+W)

scy_A = Scrollbar(frameA, orient = VERTICAL, command=scroll_y)
scy_A.grid(row=0, column=2, sticky=N+S)

scx_B = Scrollbar(frameA, orient = HORIZONTAL, command=scroll_x)
scx_B.grid(row=1, column=3, columnspan=2, sticky=E+W)

scy_B = Scrollbar(frameA, orient = VERTICAL, command=scroll_y)
scy_B.grid(row=0, column=5, sticky=N+S)

# put the other two side by side on two scrollable canvases
panelA = Canvas(frameA, width=w//2-20, height=h-70,
				scrollregion=(0,0,img.width(),img.height()),
				xscrollcommand=scx_A.set,
				yscrollcommand=scy_A.set)
panelA.grid(row=0, column=0, columnspan=2)
imgA = panelA.create_image((0,0), image = mixed, anchor = "nw")

# bind mouse event
panelA.bind("<Button-1>", sh.draw)

panelB = Canvas(frameA, width=w//2-20, height=h-70,
				scrollregion=(0,0,img.width(),img.height()),
				xscrollcommand=scx_B.set,
				yscrollcommand=scy_B.set)
panelB.grid(row=0, column=3, columnspan=2)
imgB = panelB.create_image((0,0), image = img, anchor = "nw")

# create frame for buttons
frameB = Frame(new)
frameB.grid(row=5,column=0)

#place a button to quit the program.
quit_button = Button(frameB, text = "Quit", command = quit_prog)
quit_button.grid(row = 5, column=0, padx=50, pady=10)
#place a button to quit the program.
quit_button3 = Button(frameB, text = "chr", command = chr_area)
quit_button3.grid(row = 5, column=2, padx=50, pady=10)
#place a button to quit the program.
quit_button4 = Button(frameB, text = "mask", command = mask)
quit_button4.grid(row = 5, column=3, padx=50, pady=10)
#place a button to quit the program.
quit_button5 = Button(frameB, text = "reset polygon", command = delete)
quit_button5.grid(row = 5, column=4, padx=50, pady=10)

quit_button7 = Button(frameB, text = "reset all", command = reset_all)
quit_button7.grid(row = 5, column=5, padx=50, pady=10)

quit_button8 = Button(frameB, text = "discard", command = change)
quit_button8.grid(row = 5, column=7, padx=50, pady=10)

quit_button9 = Button(frameB, text = "continue", command = save)
quit_button9.grid(row = 5, column=8, padx=50, pady=10)

root.mainloop()



