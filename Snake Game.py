from tkinter import *
import MazeGeneration as mg
import time
import random
    
class Ground (mg.Grid):
    def __init__(self, cvs, topLeft, cellSize, dim, isWrappingAround = True, bgColor = "black"):
        super().__init__(cvs,topLeft, dim, cellSize, bgColor, wallThickness = 2)
        self.gridLineColor = "white"
        self.borderColor = "grey"
        self.foodColor = "red"
        self.isWrappingAround = isWrappingAround
        self.foodIndices = []
        self.availableCellIndices = []
        for r in range(self.dim[0]):
            for c in range (self.dim[1]):
                self.availableCellIndices.append((r,c))
                
        if not self.isWrappingAround:
            self.createBorderWall()            

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()

        tl = self.topLeft
        self.cvs.create_rectangle(tl[0], tl[1], tl[0] + self.cellSize[0]*self.dim[1], tl[1] + self.cellSize[0]*self.dim[0], width = cell.wallThickness)
        if not self.isWrappingAround:
            tl = (self.topLeft[0]+self.cellSize[0], self.topLeft[1]+self.cellSize[0])
            self.cvs.create_rectangle(tl[0], tl[1], tl[0] + self.cellSize[0]*(self.dim[1]-2), tl[1] + self.cellSize[0]*(self.dim[0]-2), width = cell.wallThickness)

    def drawWalls(self):
        for row in self.grid:
            for cell in row:
                cell.drawWalls()
            
    def drawGrid(self):
        cellSize = self.cellSize[0]
        tx = self.topLeft[0]
        ty = self.topLeft[1]
            
        for i in range(self.dim[0]+1):
            self.cvs.create_line( tx, cellSize*i + ty, self.dim[1]*cellSize + tx, cellSize*i + ty, tag = "gridLines", fill = self.gridLineColor)

        for i in range(self.dim[1]+1):
            self.cvs.create_line(cellSize*i + tx, ty, cellSize*i + tx, self.dim[0]*cellSize + ty, tag = "gridLines", fill = self.gridLineColor)

    def undraw(self):
        self.cvs.delete("gridLines")

    def createBorderWall(self):      
        for i in range(self.dim[0]):
            for j in [0, self.dim[1]-1]:
                self.grid[i][j].markAsObstacle(self.borderColor)
                self.availableCellIndices.remove((i,j))

        for j in range(1, self.dim[1]-1):
            for i in [0, self.dim[0]-1]:
                self.grid[i][j].markAsObstacle(self.borderColor)
                self.availableCellIndices.remove((i,j))        

    def placeFoodAtRandom(self):
        if self.availableCellIndices:
            ind = random.choice(self.availableCellIndices)
            cell = self.grid[ind[0]][ind[1]]
            cell.changeColor(self.foodColor)                
            self.availableCellIndices.remove(ind)
            self.foodIndices.append(ind)
            return ind 

    #this method overrides the super class's method used while finding path
    def getNeighbours(self, cell):
        row = cell.index[0]
        colm = cell.index[1]
        neighbours=[]
        for i in range(len(cell.index)):
            for offset in [1,-1]:
                ind=[row, colm]
                ind[i]+= offset
                neighbours.append(self.grid[ind[0]%self.dim[0]][ind[1]%self.dim[1]])
        return neighbours

    #removes both the common walls
    def removeCommonOutline(self, currCell, adjCell):
        wallInfo = self.getCommonWallIndex(currCell, adjCell)
        cell = wallInfo[0]
        ind = wallInfo[1]
        cell.removeOutline(ind)

        cells = [currCell, adjCell]
        cell = cells[(cells.index(cell)+1)%2]
        ind+=2
        cell.removeOutline(ind)

class Snake:    
    #row and column num, not x and y
    UP = (-1, 0)
    DOWN = (1, 0)
    RIGHT = (0, 1)
    LEFT = (0, -1)
        
    def __init__(self, ground, headInd, direc = (0, 1), length = 2):
        self.ground = ground
        self.heading = direc
        self.headColor = "green"
        self.bodyColor = "white"
        self.percpRad  = self.ground.cellSize[0]
        self.bodyPartInd = []
        self.newHeadInd = headInd
        self.newPartInd = self.getStillnewPartInd()
        if length < 1:
            length = 1
        for i in range(length):
            if self.newPartInd is None:
                self.newPartInd = headInd
            self.grow()                
            self.newPartInd = self.getStillnewPartInd()
        self.getCellAt(headInd).changeColor(self.headColor)
        self.foodInd = None

    def grow(self):
        cell = self.getCellAt(self.newPartInd)
        cell.changeColor(self.bodyColor)
        cell.isObstacle = True

        for i in range(4):
            cell.drawOutline(i)
        if self.bodyPartInd:
            self.ground.removeCommonOutline(cell, self.getCellAt(self.bodyPartInd[-1]))

        self.bodyPartInd.append(self.newPartInd)
        self.ground.availableCellIndices.remove(self.newPartInd)
        
    def getStillnewPartInd(self):
        if self.bodyPartInd:
            tailInd = self.bodyPartInd[-1]
            tailNeighbs = self.ground.getNeighbours(self.getCellAt(tailInd))
            
            for cell in reversed(tailNeighbs):
                if cell.isObstacle:
                    tailNeighbs.remove(cell)

            straightOutInd = (tailInd[0] - self.heading[0], tailInd[1] - self.heading[1])
            straightOutCell = self.getCellAt(straightOutInd)
            if straightOutCell in tailNeighbs:
                return straightOutCell.index
            return tailNeighbs[0].index
            
    def wander(self):
        headInd = self.bodyPartInd[0]
        rightDir = (self.heading[1], -self.heading[0])
        leftDir = (-rightDir[0], -rightDir[1])
        directions = [leftDir, self.heading, rightDir]
        rows = self.ground.dim[0]
        colms = self.ground.dim[1]
        
        posbCells = {}
        for d, direction in enumerate(directions):
            ind = ( (headInd[0]+direction[0])%rows, (headInd[1]+direction[1])%colms )
            cell = self.getCellAt(ind)
            if not cell.isObstacle:
                posbCells[d] = cell
            
        if posbCells:
            nonObstacleCells = []
            for cell in posbCells.values():
                nonObstacleCells.append(cell)

            for i in reversed(list(posbCells)):
                cornerCells = []
                cell = posbCells[i]
                direction = directions[abs(1-i)]
                for j in [1,-1]:
                    r = (cell.index[0] + j*direction[0]) %rows
                    c = (cell.index[1] + j*direction[1]) %colms
                    cornerCells.append(self.getCellAt((r,c)))

                if cornerCells[0].isObstacle and cornerCells[1].isObstacle:
                    del posbCells[i]

            if posbCells:
                if 1 in posbCells:
                    return posbCells[1]
                return random.choice(list(posbCells.values()))
            
            return random.choice(nonObstacleCells)
                        
    
    def moveToAdjCell(self, cell):
        self.setHeadingTowards(cell)
        self.move()

    def move(self):
        self.newPartInd = self.bodyPartInd.pop()
        self.bodyPartInd.insert(0, self.newHeadInd)

        # to handle condition for only 1 body part, % is used
        secondCell = self.getCellAt(self.bodyPartInd[1%len(self.bodyPartInd)])
        secondCell.changeColor(self.bodyColor)
        
        newPartCell = self.getCellAt(self.newPartInd)
        newPartCell.changeColor(self.ground.bgColor)

        # problem when there's only 1 part. all outlines are drwan and no None in list
        lineInd = (newPartCell.outlines.index(None)+2)%4
        self.getCellAt(self.bodyPartInd[-1]).drawOutline(lineInd)
        
        newPartCell.isObstacle = False
        self.ground.availableCellIndices.append(self.newPartInd)
        
        newHeadCell = self.getCellAt(self.bodyPartInd[0])
        newHeadCell.changeColor(self.headColor)

        for i in range(4):
            newHeadCell.drawOutline(i)
            newPartCell.removeOutline(i)
        self.ground.removeCommonOutline(newHeadCell, secondCell)
        
        newHeadCell.isObstacle = True
        if self.bodyPartInd[0] in self.ground.foodIndices:
            self.foodInd = self.bodyPartInd[0]
        else:
            self.ground.availableCellIndices.remove(self.bodyPartInd[0])
        
    def willCrash(self, direc):
        if (direc[0] != -self.heading[0]) and (direc[1] != -self.heading[1]):
            self.heading = direc

        headInd = self.bodyPartInd[0]
        r = headInd[0]+self.heading[0]
        c = headInd[1]+self.heading[1]
        
        if self.ground.isWrappingAround:
            r %= self.ground.dim[0]
            c %= self.ground.dim[1]
            
        newHeadInd = (r, c)
        if self.getCellAt(newHeadInd).isObstacle:
            return True
        self.newHeadInd = newHeadInd
        return False

    def foodSpotted(self):
        if self.foodInd is not None and self.foodInd in self.ground.foodIndices:
            return True
        headInd = self.bodyPartInd[0]
        for foodInd in self.ground.foodIndices:
            distSq = (headInd[0] - foodInd[0])**2 + (headInd[1] - foodInd[1])**2
            if distSq <= self.percpRad * self.percpRad:
                self.foodInd = foodInd
                return True
        self.foodInd = None
        return False
        
    def ateFood(self):
        if self.bodyPartInd[0] == self.foodInd:
            self.ground.foodIndices.remove(self.foodInd)
            self.foodInd = None
            return True
        return False

    def removeFromGround(self):
        for ind in self.bodyPartInd:
            cell = self.getCellAt(ind)
            cell.changeColor(self.ground.bgColor)
            cell.isObstacle = False
            self.ground.availableCellIndices.append(ind)
            for i in range(4):
                cell.removeOutline(i)
        self.ground = None

    def getCellAt(self,ind):
        return self.ground.grid[ind[0]][ind[1]]

    def setHeadingTowards(self, cell):
        #allow snake to head in opp. direction.
        self.newHeadInd = cell.index
        headInd = self.bodyPartInd[0]
        newDir = (self.newHeadInd[0] - headInd[0], self.newHeadInd[1] - headInd[1])
        self.heading = newDir

    def setHeadColor(self, color):
        self.headColor = color

    def setBodyColor(self, color):
        self.bodyColor = color

    def setPerceptionRadius(self, rad):
        self.percpRad = rad

if __name__ == "__main__":
    root=Tk()
    root.title("Snake Game")

    _ht = 480
    _width = 620
    canvas = Canvas(root, bg = "white", height=_ht, width=_width)
    canvas.pack(fill=X)

    gDim = (23,30)
    _ground = Ground(canvas,(10,10), 20, gDim, isWrappingAround = True)
    _ground.draw()

    snake = Snake(_ground, (int(gDim[0]/2),int(gDim[1]/2)-2))
    currDirec = snake.heading

    canvas.focus_set()
 
    '''had to do this way, bcoz quick pressing of different keys lead to a heading changing quickly before moving
    allowing snake to head in opposite direction and crash.'''
    def goLeft(e):
        globals()["currDirec"] = Snake.LEFT

    def goRight(e):
        globals()["currDirec"] = Snake.RIGHT

    def goUp(e):
        globals()["currDirec"] = Snake.UP

    def goDown(e):
        globals()["currDirec"] = Snake.DOWN

    canvas.bind("<Left>", goLeft)
    canvas.bind("<Right>", goRight)
    canvas.bind("<Up>", goUp)
    canvas.bind("<Down>", goDown)

    scoreLabel = Label(root, text = "Score:0", font = ("Fira Code", 30, "bold"))
    scoreLabel.pack(side = LEFT, padx = 10)

    score = 0
    snake.foodInd = snake.ground.placeFoodAtRandom()
    while not snake.willCrash(currDirec):
        snake.move()
        if snake.ateFood():
            snake.grow()
            snake.foodInd = snake.ground.placeFoodAtRandom()
            score+=10
            scoreLabel.config(text = "Score:"+str(score))
        root.update()
        time.sleep(0.1)

    Label(root, text = "GAME OVER", font = ("Harry P", 36)).pack(side = RIGHT, padx = 20)
    root.mainloop()
        
