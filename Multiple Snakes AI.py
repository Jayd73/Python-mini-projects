from tkinter import *
from SnakeGame import *
import time
import random

root=Tk()
root.title("Snake Game")

_ht = 480
_width = 620
canvas = Canvas(root, bg = "white", height=_ht, width=_width)
canvas.pack(fill=X)

gDim = (46, 60)
ground = Ground(canvas,(10,10), 10, gDim, isWrappingAround = False)
ground.draw()

drawnObstacles=[]
def createObstacle(event):
    cell = ground.getCellFromCoords(event.x, event.y)
    if cell and not cell.isObstacle and cell.index in ground.availableCellIndices:
        cell.markAsObstacle("white")
        ground.availableCellIndices.remove(cell.index)
        drawnObstacles.append(cell)

def changePercpRad(rad):
    for snake in snakes:
        snake.setPerceptionRadius(int(rad))

canvas.bind("<B1-Motion>", createObstacle)
Label(root,text="Perception radius ").pack(side = LEFT, padx=10)
scaleXAllPoints=Scale(root, from_=0, to = 100,orient=HORIZONTAL, command=changePercpRad, resolution=1, cursor="hand2", sliderlength=15, length=400)
scaleXAllPoints.set(10)
scaleXAllPoints.pack(side = LEFT)

def createCircle(x, y, rad, color, _tag):
    canvas.create_oval(x - rad, y - rad, x + rad, y+ rad, outline = color, tag = _tag)

snakes = []
aliveStatus = []
headColors = ["forest green", "blue", "orange","purple", "OrangeRed4"]
bodyColor = ["light green", "light blue", "yellow","pink", "brown1"]
circleRadii = []
for (hColor, bColor) in zip(headColors[:4], bodyColor[:4]) :
    r = random.randrange(2, ground.dim[0]-2)
    c = random.randrange(2, ground.dim[1]-2)
    s = Snake(ground,(r,c))
    s.setHeadColor(hColor)
    s.setBodyColor(bColor)
    s.setPerceptionRadius(10)
    snakes.append(s)
    aliveStatus.append(True)
    circleRadii.append(s.percpRad*s.ground.cellSize[0])
    
for i in range(len(snakes)):
    ground.placeFoodAtRandom()

root.update()

while True:
    #canvas.delete("percpCircle")
    for i, snake in enumerate(snakes):
        pathFound = False
        head = snake.getCellAt(snake.bodyPartInd[0])
        if snake.foodSpotted():
            foodCell = snake.getCellAt(snake.foodInd)
            nextStep = snake.ground.findPath(head, foodCell, getNextStep = True)
            if nextStep:
                nextCell = nextStep
                pathFound = True
        if not pathFound:
            nextCell = snake.wander()

        if nextCell:
            aliveStatus[i] = True
            snake.moveToAdjCell(nextCell)
            #createCircle(head.x, head.y, circleRadii[i], snake.headColor, "percpCircle")
            if snake.foodInd and snake.ateFood():
                r = snake.ground.dim[0]
                c = snake.ground.dim[1]
                snake.grow()
                ground.placeFoodAtRandom()
            root.update()
        else:
            aliveStatus[i] = False
            adjCells = snake.ground.getNeighbours(snake.getCellAt(snake.bodyPartInd[0]))
            obsBodyParts = 0
            for cell in adjCells:
                if cell.index in snake.bodyPartInd or cell.currColor == snake.ground.borderColor or cell in drawnObstacles:
                    obsBodyParts+=1
            if obsBodyParts == 4:
                for ind in snake.bodyPartInd:
                    cell = snake.getCellAt(ind)
                    cell.changeColor("red")
                root.update()
                time.sleep(0.02)
                snake.removeFromGround()
                newSnake = Snake(ground, snake.bodyPartInd[0], direc = snake.heading)
                newSnake.setHeadColor(snake.headColor)
                newSnake.setBodyColor(snake.bodyColor)
                newSnake.setPerceptionRadius(snake.percpRad)
                snakes[i] = newSnake                
            
    if aliveStatus.count(False) == len(snakes):
        break
print("SIM OVER")
            
            
    











        
