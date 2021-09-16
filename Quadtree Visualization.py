from tkinter import *
import random
import math

class Point:
    def __init__ (self, x,y, userData=None):
        self.x=x
        self.y=y
        self.userData = userData

    def draw(self, cvs):
        self.cvs = cvs
        rad=3
        self.orig_color="white"
        self.ptID = cvs.create_oval(self.x-rad, self.y-rad,self.x+rad, self.y+rad, fill=self.orig_color, outline=self.orig_color)
        #root.update()

    def toString(self):
        return "x: " + str(self.x)+" y: "+str(self.y)

    def highlight(self):
        color="red"
        self.cvs.itemconfig(self.ptID, fill=color, outline=color)

    def unhighlight(self):
        self.cvs.itemconfig(self.ptID, fill=self.orig_color, outline=self.orig_color)

class Boundary:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, cvs, _tag="boundary", color="white", _width=1):
        cvs.create_rectangle(self.x1, self.y1, self.x2, self.y2, tag=_tag, outline=color, width=_width)

    def contains(self, point):
        if point.x >= self.x1 and point.y >= self.y1 and point.x <= self.x2 and point.y <= self.y2:
            return True
        return False

    def toString(self):
        return "x1: " + str(self.x1)+" y1: "+str(self.y1)+" x2: " + str(self.x2)+" y2: "+str(self.y2)

    def intersects(self, bRect):
        if (self.x1 >= bRect.x2 or bRect.x1 >= self.x2) or (self.y1 >= bRect.y2 or bRect.y1 >= self.y2):
            return False
        return True
    

class Quadtree:
    count=0
    def __init__(self,boundary,capacity):
        self.boundary=boundary
        self.capacity = capacity
        self.isDivided=False
        #only the leaf nodes will store the points. i.e. undivided quadtrees
        self.points=[]
        self.sections=None

    def insert(self, point):
        if not self.boundary.contains(point):
            return False
        # points array is made mt in subdivide
        if len(self.points) < self.capacity and not self.isDivided:
            self.points.append(point)
            return True
        if not self.isDivided:
            self.subDivide()

        for section in self.sections:
            if section.insert(point):
                return True
        
    def subDivide(self):
        self.isDivided=True
        x1 = self.boundary.x1
        y1 = self.boundary.y1
        x2 = self.boundary.x2
        y2 = self.boundary.y2
        
        w = x2 - x1
        h = y2 - y1
            
        nw= Quadtree(Boundary(x1, y1, x1 + w/2, y1 + h/2), self.capacity)
        ne= Quadtree(Boundary(x1 + w/2, y1, x2, y1 + h/2), self.capacity)
        sw= Quadtree(Boundary(x1, y1 + h/2, x1 + w/2, y2), self.capacity)
        se= Quadtree(Boundary(x1 + w/2, y1 + h/2, x2, y2), self.capacity)
        self.sections = [nw, ne, sw, se]

        #push all the points stored to children
        for point in self.points:
            for section in self.sections:
                if section.insert(point):
                    break
        self.points=[]
            

    def printPts(self):
        print("Boundary: ", self.boundary.toString())
        for pt in self.points:
            print(pt.toString())
        if self.isDivided:
            for section in self.sections:
                section.printPts()

    def draw(self, cvs):
        cvs.delete("boundary")
        self.redrawBoundaries(cvs)
        root.update()

    def redrawBoundaries(self, cvs):
        self.boundary.draw(cvs)
        if self.isDivided:
            for section in self.sections:
                section.redrawBoundaries(cvs)

    def query(self, border):
        requiredPts=[]
        if not self.isDivided:
            if self.boundary.intersects(border):
                for point in self.points:
                     if border.contains(point):
                         requiredPts.append(point)
        else:                
            for section in self.sections:
                requiredPts.extend(section.query(border))
                
        return requiredPts

if __name__=="__main__":
    root=Tk()
    root.title("Quadtree Visualization")

    _ht=600
    _width=700

    canvas=Canvas(root, bg="black",height=_ht, width=_width)
    canvas.pack(side=LEFT)

    b = Boundary(_width/10, _ht/10, 9*_width/10, 9*_ht/10)
    quadtree = Quadtree(b, 4)
    coords = [(100,100),(500, 100), (100,400),(500, 400)]
    # ,(530, 400),(520, 400),(510, 390),(500, 350),(535, 400)


    def drawGivenPts(coords):
        for coord in coords:
            p = Point(coord[0], coord[1])
            p.draw(canvas)
            quadtree.insert(p)

    randomPts=[]
    def drawRandomPoints(quadtree):
        for _ in range(1000):
            x = random.randrange(_width/10, 9*_width/10)
            y = random.randrange(_ht/10, 9*_ht/10)
            p = Point(x, y)
            randomPts.append(p)
            p.draw(canvas)
            quadtree.insert(p)

    #drawGivenPts(coords)
    #drawRandomPoints(quadtree)
    quadtree.draw(canvas)

    #b.draw(canvas)
    def drawClusterOfPts(event):
        side = 10
        for _ in range(random.randrange(1, 4)):
            p = Point(event.x+random.randrange(-side, side), event.y+random.randrange(-side, side))
            p.draw(canvas)
            quadtree.insert(p)
            quadtree.draw(canvas)

    detectedPts=[]   
    def drawDetectingRect(event):
        global detectedPts
        side = 50
        canvas.delete("range")
        rect = Boundary(event.x - side, event.y - side, event.x + side, event.y + side)
        rect.draw(canvas, _tag="range", color="blue", _width=2)
        pts = quadtree.query(rect)

        for p in detectedPts:
            if p not in pts:
                p.unhighlight()
                
        detectedPts=[]
        for p in pts:
            p.highlight()
            detectedPts.append(p)
        root.update()
            
    canvas.bind("<B1-Motion>", drawClusterOfPts)
    canvas.bind("<Motion>", drawDetectingRect)
    root.mainloop()

