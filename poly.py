from tkinter import *

points = []
shapes = []
lines = []

def drag(event):
	global c
	print("DRAAAAAAAAAG")

def point(event):
	global points, c, ovals
	print(event.type)
	if len(shapes) == 0:
		oval = c.create_oval(event.x, event.y, event.x+1, event.y+1, fill="black")
		points.append(event.x)
		points.append(event.y)

		if len(points) > 2:
			lines.append(c.create_line(points[-4:]))
			if points[0] -5 <= event.x <= points[0] +5 and points[1] -5 <= event.y <= points[1] +5:
				x = points.pop()
				y = points.pop()
				c.delete(oval)
				c.delete(lines.pop())
				shapes.append(c.create_polygon(points))
				points = []
	else:
		c.move(shapes[0], 10,10)
	return points

def cursor(event):
    global points, c
    if len(points) > 2:
        if points[0] -5 <= event.x <= points[0] +5 and points[1] -5 <= event.y <= points[1] +5:
            c.configure(cursor="circle")
        else:
            c.configure(cursor="crosshair")
    elif len(shapes) != 0:
    	c.configure(cursor="gumby")
    else:
        c.configure(cursor="crosshair")

def delete(event):
    global c, points, shapes
    points = []
    shapes = []
    c.delete("all")

if __name__ == "__main__":
    root = Tk()

    root.title("Simple Graph")

    root.resizable(0,0)


    c = Canvas(root, bg="white", width=300, height= 300)
    c.configure(cursor="crosshair")
    c.pack()

    c.bind("<Motion>", cursor)
    c.bind("<Button-1>", point)
    c.bind("<Button-2>", delete)

    root.mainloop()