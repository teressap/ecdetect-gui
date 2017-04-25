from tkinter import *

points = []
lines = []
shape = 0
orig_x = 0
orig_y = 0

# colors
line_c = "gold2"
dot_c = "purple"

def reset():
	global points, lines, shape, orig_x, orig_y
	points=[]
	lines=[]
	shape=0
	orig_x=0
	orig_y=0

class point():
	global points, shape
	line1 = 0	# start
	line2 = 0	# end

	def drag(self, event):
		global points, lines, shape
		idx = points.index(self)
		self.panel.move(self.id, self.panel.canvasx(event.x) - self.x, self.panel.canvasy(event.y) - self.y)
		self.x = self.panel.canvasx(event.x)
		self.y = self.panel.canvasy(event.y)
		points[idx] = self
		if self.line1 != 0:
			p2 = self.line1.end
			idx = lines.index(self.line1)
			self.panel.delete(self.line1.id)
			self.line1 = line(self, p2, self.panel)
			lines[idx] = self.line1
			p2.line2 = self.line1
		if self.line2 != 0:
			p2 = self.line2.start
			idx = lines.index(self.line2)
			self.panel.delete(self.line2.id)
			self.line2 = line(p2, self, self.panel)
			lines[idx] = self.line2
			p2.line1 = self.line2
		self.panel.delete(shape.id)
		shape = poly(points, self.panel)

	def cursor_on(self, event):
		if shape != 0:
			self.panel.configure(cursor="sizing")
		else:
			self.panel.configure(cursor="circle")

	def cursor_off(self,event):
		self.panel.configure(cursor="crosshair")

	def __init__(self,x,y,panel):
		self.x = x
		self.y = y
		self.panel = panel
		self.id = panel.create_oval(x, y, x+7, y+7, outline=dot_c, width=3)
		self.panel.tag_bind(self.id, '<B1-Motion>', self.drag)
		self.panel.tag_bind(self.id, '<Any-Enter>', self.cursor_on)
		self.panel.tag_bind(self.id, '<Any-Leave>', self.cursor_off)

class line():
	def __init__(self, p1, p2, panel):
		self.start = p1
		self.end = p2
		self.panel = panel
		self.id = panel.create_line([p1.x,p1.y,p2.x,p2.y], 
			width=3, joinstyle=MITER, capstyle=ROUND, dash=(3,5,1,1),
			fill=line_c)

class poly():
	def __init__(self, points, panel):
		self.panel = panel
		self.points = points
		new_points = []
		for p in points:
			new_points.append(p.x)
			new_points.append(p.y)
		self.id = self.panel.create_polygon(new_points, fill='')
		self.panel.tag_bind(self.id, '<B1-Motion>', self.drag)
		self.panel.tag_bind(self.id, '<Button-1>', self.click)
		# always raise points
		for p in points:
			self.panel.tag_raise(p.id)

	def click(self, event):
		self.x = self.panel.canvasx(event.x)
		self.y = self.panel.canvasy(event.y)

	def drag(self,event):
		global points, lines
		self.panel.move(self.id, self.panel.canvasx(event.x) - self.x, self.panel.canvasy(event.y) - self.y)
		for p in points:
			self.panel.move(p.id, self.panel.canvasx(event.x) - self.x, self.panel.canvasy(event.y) - self.y)
			p.x = self.panel.canvasx(event.x)-self.x + p.x
			p.y = self.panel.canvasy(event.y)-self.y + p.y
		for l in lines:
			self.panel.move(l.id, self.panel.canvasx(event.x) - self.x, self.panel.canvasy(event.y) - self.y)
		self.x = self.panel.canvasx(event.x)
		self.y = self.panel.canvasy(event.y)

def draw(event, d = True):
	# completion of polygon
	global shape, points, lines, orig_x, orig_y
	if len(points)>2:
		if event.widget.canvasx(event.x)-5 < orig_x < event.widget.canvasx(event.x)+5 and event.widget.canvasy(event.y)-5 < orig_y < event.widget.canvasy(event.y)+5 :
			l = line(points[0],points[-1], event.widget)
			lines.append(l)
			points[-1].line2 = l
			points[0].line1 = l
			event.widget.unbind("<Button-1>")
			shape = 1
			shape = poly(points, event.widget)
			print(shape)
			return
	# otherwise
	points.append(point(event.widget.canvasx(event.x), event.widget.canvasy(event.y), event.widget))
	# add line
	if len(points) >= 2:
		p1 = points[-1]
		p2 = points[-2]
		l = line(p1,p2, event.widget)
		p1.line1 = l
		p2.line2 = l
		lines.append(l)
	# always raise points
	for p in points:
		event.widget.tag_raise(p.id)
	# assign origin x an y
	if len(points) == 1:
		orig_x = event.widget.canvasx(event.x)
		orig_y = event.widget.canvasy(event.y)

def main():
	root = Tk()
	root.geometry("400x300")

	panelA = Canvas(root, width = 400, height = 300)
	panelA.pack()

	if shape == 0:
		drawid = panelA.bind("<Button-1>", draw)

	root.mainloop()

if __name__ == "__main__":
	main()