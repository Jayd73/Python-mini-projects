from tkinter import *
from CustomVectorModule import *
from MazeGeneration import *
import random


class Ray:
    def __init__(self, pos, direc):
        self.pos = pos
        self.direc = direc
        self.rayID = None
        self.color = "white"

    def draw(self, cvs, scaleVal=10):
        cvs.delete(self.rayID)
        vect = self.direc.getScaled(scaleVal).getAdd(self.pos)
        self.rayID = cvs.create_line(self.pos.getX(), self.pos.getY(), vect.getX(), vect.getY(), fill=self.color)

    def moveTo(self, x, y):
        self.pos.setX(x)
        self.pos.setY(y)

    def castOn(self, x1, y1, x2, y2, width=1):
        x3 = self.pos.getX()
        y3 = self.pos.getY()
        x4 = self.pos.getX() + self.direc.getX()
        y4 = self.pos.getY() + self.direc.getY()

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return
        t = ((x1 - x3) * (y3 - y4) - (y1 -y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 -y2) * (x1 - x3)) / den

        if t >= 0 and t <= 1 and u > 0:
            pt = (x1 + t * (x2 - x1), y1 + t*(y2 - y1))
            return (pt, u)

    

class Observer:
    def __init__(self, cvs, pos, viewRadius= 100, viewAngle = 40):
        self.pos = pos
        self.cvs=cvs
        self.viewRadius = viewRadius
        self.viewAngle = viewAngle
        angInRad = viewAngle*math.pi/180
        self.heading = None
        self.rays = []
        self.wallCoords=[]
        self.viewScreen = None
        self.createRays()

    def createRays(self):
        for ang in range(0,self.viewAngle, 1):
            angInRad = ang*math.pi/180
            direc = Vector([math.cos(angInRad), math.sin(angInRad)])
            ray = Ray(self.pos, direc)
            self.rays.append(ray)

        self.heading = self.rays[math.ceil(len(self.rays)/2)]

    def draw(self):
        self.castRays()

    def castRays(self):
        if self.viewScreen:
            self.viewScreen.delete("imgSlice")
            screenW = int(self.cvs.cget("width"))
            screenH = int(self.cvs.cget("height"))
            width = screenW / len(self.rays)
            
        for i, ray in enumerate(self.rays):
            shortestDist = self.viewRadius
            pt = None
            for wallCoords in self.wallCoords:
                info = ray.castOn(wallCoords[0], wallCoords[1], wallCoords[2], wallCoords[3])
                if info and info[1] < shortestDist:
                    pt = info[0]
                    shortestDist = info[1]
            ray.draw(self.cvs, shortestDist)

            if self.viewScreen:
                val = math.ceil(self.mapVal(shortestDist, 0, self.viewRadius, 255, 0))
                color = self.rgb_to_hex((val, val, val))
                ht = screenH * self.viewAngle / shortestDist
                self.viewScreen.create_rectangle(i * width, screenH/2 - ht/2, i * width + width, screenH/2 + ht/2, fill = color, outline = color, tag = "imgSlice")                
        
    def moveTo(self, x, y):
        self.pos.setX(x)
        self.pos.setY(y)
        for ray in self.rays:
            ray.moveTo(x, y)
        self.castRays()

    def moveFrontBack(self, dist, step=1):
        v = self.heading.direc.getScaled(dist).getAdd(self.pos)
        self.moveTo(v.getX(), v.getY())

    def moveSideways(self, dist):
        v = self.heading.direc.getPerpendicularVect2D()
        v.scale(dist).add(self.pos)
        self.moveTo(v.getX(), v.getY())
        

    def rotate(self, ang):
        angInRad = ang*math.pi/180
        for ray in self.rays:
            x, y = self.getNewPtsAfterRotation(ray.direc.getX(), ray.direc.getY(), angInRad)
            ray.direc.setX(x)
            ray.direc.setY(y)

        self.castRays()

    def getNewPtsAfterRotation(self, oldX, oldY, ang):
        x = oldX * math.cos(ang) - oldY * math.sin(ang)
        y = oldX * math.sin(ang) + oldY * math.cos(ang)
        return (x, y)

    def setViewScreen(self, viewCvs):
        self.viewScreen = viewCvs
        
    def setWallCoords(self, wallCoords):
        self.wallCoords = wallCoords

    def addWallCoords(self, coord):
        self.wallCoords.append(coord)

    def putInMaze(self, maze):
        self.maze = maze
        for row in self.maze.grid:
            for cell in row:
                for wall in cell.walls:
                    if wall: 
                        self.addWallCoords(self.cvs.coords(wall))

    def goToEndPt(self, endPt, stepSize = 10):
        startPt = self.maze.getCellFromCoords(self.pos.getX(), self.pos.getY())
        self.moveTo(startPt.x1 + (startPt.x2 - startPt.x1)/2, startPt.y1 + (startPt.y2 - startPt.y1)/2)
        pathCells = self.maze.findPath(startPt, endPt, animate = False, showPath = True)
        
        for pathCell in pathCells:
            moveBy = math.sqrt(math.pow((self.pos.getX() - pathCell.x),2) + math.pow((self.pos.getY() - pathCell.y),2))/stepSize
            diffVect = Vector([pathCell.x, pathCell.y])
            diffVect.sub(self.heading.pos)
            angInDeg = round(self.heading.direc.getAng2D(diffVect)*180/math.pi,0)
            
            if angInDeg !=0:
                if abs(angInDeg) == 270:
                    angInDeg = (angInDeg/270)*-90
                for _ in range(stepSize):
                    self.rotate(angInDeg/stepSize)
                    maze.root.update()
            for _ in range(stepSize):
                self.moveFrontBack(moveBy)
                maze.root.update()            
        
        
    def mapVal (self, val, fromA, fromB, toA, toB):
        y= (val-fromA)*((toB-toA)/(fromB-fromA))+toA
        return y

    def rgb_to_hex(self, colorTuple):
        return "#%02x%02x%02x"%colorTuple
                

root=Tk()
root.title("Ray Tracing Visual")

_ht=500
_width=630

canvas=Canvas(root, bg="black",height=_ht, width=_width)
canvas.pack(side=LEFT)
view=Canvas(root, bg="black",height=_ht, width=_width)
view.pack(side=LEFT)

def moveObs(event):
    obs.moveTo(event.x, event.y)

ang=3
def rotateObsPos(event):
    obs.rotate(ang)

def rotateObsNeg(event):
    obs.rotate(-ang)

moveBy = 5
#with respect to player view and not the top view on the left
def moveLeft(e):
    obs.moveSideways(moveBy)

def moveRight(e):
    obs.moveSideways(-moveBy)

def moveUp(e):
    obs.moveFrontBack(moveBy)

def moveDown(e):
    obs.moveFrontBack(-moveBy)

def travelToTheEnd(event):
    endPt = obs.maze.getCellFromCoords(event.x, event.y)
    endPt.changeColor("orange")
    obs.goToEndPt(endPt)

# Controls
canvas.focus_set()
canvas.bind("<B1-Motion>", moveObs)
canvas.bind("<Button-3>", travelToTheEnd)
canvas.bind("<Left>", moveLeft)
canvas.bind("<Right>", moveRight)
canvas.bind("<Up>", moveUp)
canvas.bind("<Down>", moveDown)
canvas.bind("a", rotateObsNeg)
canvas.bind("d", rotateObsPos)


obs= Observer(canvas, Vector([300,300]), 300)
obs.setViewScreen(view)

maze = Grid(canvas, topLeft=(30,30), dim=(7,9), cellSize=(50,50), bgColor = "black", wallColor = "white")
maze.setRootObject(root)
maze.createMaze()
maze.draw()

obs.putInMaze(maze)
obs.moveTo(obs.maze.topLeft[0]+5,obs.maze.topLeft[1]+5)
obs.draw()
root.mainloop()





