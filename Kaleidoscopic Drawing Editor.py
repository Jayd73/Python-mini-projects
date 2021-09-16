from tkinter import *
from tkinter import filedialog
from CustomVectorModule import Vector
import math
import colorsys
import random
from PIL import Image
import os

class KaleidoscopicDrawer:
    GREY_SCALE = 0
    MULTICOLOR = 1
    def __init__(self, center, symmetries, cvs):
        self.cvs = cvs
        self.center = Vector([center[0], center[1]])
        self.symmetries = symmetries
        self.prevPos = None
        self.currPos = Vector([0,0])
        self.colorVal = random.randint(0,256)
        self.getColor = self.getMulticolorHex

    def resetPrevPos(self, event):
        self.prevPos = None

    def draw(self, event):
        self.currPos.setX(event.x)
        self.currPos.setY(event.y)
        
        color = self.getColor()
        self.colorVal+=2

        if not self.prevPos:
            self.prevPos = Vector([event.x, event.y])

        d = math.sqrt((self.prevPos.getX()-event.x)**2 + (self.prevPos.getY()-event.y)**2)
        w = self.mapVal(d, 0, 60, 13, 1)
        if w<0:
            w=1

        ang = 360/self.symmetries
        rotatedPrev = self.prevPos.getClone()
        rotatedCurr = self.currPos
        for _ in range(self.symmetries):
            self.cvs.create_line(rotatedPrev.getX(), rotatedPrev.getY(), rotatedCurr.getX(), rotatedCurr.getY(), fill = color, width = w, smooth = True, capstyle = ROUND)
            self.flipPt(rotatedPrev)
            self.flipPt(rotatedCurr)
            self.cvs.create_line(rotatedPrev.getX(), rotatedPrev.getY(), rotatedCurr.getX(), rotatedCurr.getY(), fill = color, width = w, smooth = True, capstyle = ROUND)
            self.flipPt(rotatedPrev)
            self.flipPt(rotatedCurr)
            self.rotatePt(rotatedPrev, ang)
            self.rotatePt(rotatedCurr, ang)

        self.prevPos.setX(event.x)
        self.prevPos.setY(event.y)

    def mapVal (self, val, fromA, fromB, toA, toB):
        y= (val-fromA)*((toB-toA)/(fromB-fromA))+toA
        return y

    def rotatePt(self, point, ang):
        point.sub(self.center)
        point.rotate2D(ang)
        point.add(self.center)

    def flipPt(self, point):
        point.sub(self.center)
        point.scaleX(-1)
        point.add(self.center)

    def drawHelperLines(self):
        v1 = Vector([self.center.getX(), 0])
        v2 = Vector([self.center.getX(), self.center.getY()*2])

        ang = 360/(self.symmetries*2)
        for _ in range(self.symmetries*2):
            self.cvs.create_line(v1.getX(), v1.getY(), v2.getX(), v2.getY(),fill = "red",tag="helper")
            self.rotatePt(v1, ang)
            self.rotatePt(v2, ang)

    def removeHelperLines(self):
        self.cvs.delete("helper")

    def rgb_to_hex(self, colorTuple):
        return "#%02x%02x%02x"%colorTuple

    def getMulticolorHex(self):
        colorTuple = colorsys.hsv_to_rgb((self.colorVal%256)/255, 1, 1)
        colorTuple = tuple(map(lambda x: int(x*255), colorTuple))
        return self.rgb_to_hex(colorTuple)

    def getGreyScaleHex(self):
        return self.rgb_to_hex((self.colorVal%256, self.colorVal%256, self.colorVal%256))

    def changeColorScheme(self, colorScheme):
        if colorScheme == KaleidoscopicDrawer.GREY_SCALE:
            self.getColor = self.getGreyScaleHex
        elif colorScheme == KaleidoscopicDrawer.MULTICOLOR:
            self.getColor = self.getMulticolorHex



class DrawingApp:
    def __init__(self, root):
        HEIGHT = 700
        WIDTH = 800
        self.defaultSymmetries = 6
        self.helperLinesDrawn = BooleanVar()
        self.helperLinesDrawn.set(False)
        self.colorSchemeVal = IntVar()
        self.colorSchemeVal.set(1)
        self.root = root
        self.root.title("Kaleidoscopic Drawing")
        self.cvs=Canvas(self.root, bg="black", height=HEIGHT, width=WIDTH)  
        self.cvs.pack(side = LEFT)

        self.drawer = KaleidoscopicDrawer((WIDTH/2, HEIGHT/2), self.defaultSymmetries, self.cvs)
        self.addWidgets()
        self.doBindings()

    def addWidgets(self):
        symmetrySlider = Scale(self.root, from_=1, to = 50,orient=HORIZONTAL, command = self.changeSymmetry, resolution=1, cursor="hand2", sliderlength=15, length=250)
        symmetrySlider.set(self.defaultSymmetries)
        symmetrySlider.pack(fill = X)
        Label(self.root, text="Symmetry").pack(fill = X)
        Button(self.root, text="Clear",command = self.clearCanvas, height=3, width=20).pack(fill=X, pady = 10)
        Checkbutton(self.root, text="Show Helper Lines", variable = self.helperLinesDrawn, onvalue=True, offvalue=False, command = self.handleLineVisibility).pack(fill=X, padx=3, pady=10)
        
        Radiobutton(self.root, text="Multicolor", variable = self.colorSchemeVal, value = 1, command = lambda : self.drawer.changeColorScheme(KaleidoscopicDrawer.MULTICOLOR)).pack(fill = X)
        Radiobutton(self.root, text="Grey scale", variable = self.colorSchemeVal, value = 2, command = lambda : self.drawer.changeColorScheme(KaleidoscopicDrawer.GREY_SCALE)).pack(fill = X)
        Button(self.root, text="Save",command = self.saveDrawing, height=3, width=20).pack(fill=X, pady = 10)

    def doBindings(self):
        self.cvs.bind("<B1-Motion>", self.drawer.draw)
        self.cvs.bind("<ButtonRelease-1>", self.drawer.resetPrevPos)

    def changeSymmetry(self, symmetries):
        self.drawer.symmetries = int(symmetries)
        self.handleLineVisibility()

    def handleLineVisibility(self):
        if self.helperLinesDrawn.get():
            self.drawer.removeHelperLines()
            self.drawer.drawHelperLines()
        else:
            self.drawer.removeHelperLines()

    def clearCanvas(self):
        self.cvs.delete("all")
        self.handleLineVisibility()

    def saveDrawing(self):
        imgFilePath = filedialog.asksaveasfilename(defaultextension = '.png')
        if imgFilePath:
            bgColor = self.cvs["background"]
            self.cvs.lower(self.cvs.create_rectangle(0,0,self.cvs.winfo_width(), self.cvs.winfo_height(), fill = bgColor, outline = bgColor))   
            psFilePath = imgFilePath[:len(imgFilePath)-3]+'eps'
            self.cvs.postscript(file = psFilePath, pagewidth = self.cvs.winfo_width()+2, pageheight = self.cvs.winfo_height()+2 , colormode = 'color')
            img = Image.open(psFilePath)
            img.save(imgFilePath, 'png', quality = 99)
            img.close()
            os.remove(psFilePath)
            
root=Tk()
app = DrawingApp(root)
root.mainloop()

