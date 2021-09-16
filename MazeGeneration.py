from tkinter import *
import random
import time
import math

class Cell:
    RIGHT_WALL = 0
    BOTTOM_WALL = 1
    LEFT_WALL = 2
    TOP_WALL = 3
    
    def __init__(self, x1, y1, x2, y2, index, cvs, thickness = 1, origColor = "white"):
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.x = x1 + (x2 - x1)/2
        self.y = y1 + (y2 - y1)/2
        self.f = 0
        self.g = math.inf
        self.previous = None
        self.cvs=cvs
        self.index = index
        self.visited=False
        self.walls=[None]*4
        self.outlines = [None]*4
        self.isObstacle = False
        self.origColor = origColor
        self.currColor = self.origColor
        self.wallColor = "black"
        self.wallThickness = thickness
        self.bg = None

    def draw(self):
        if not self.bg:
            self.bg = self.cvs.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.currColor, outline=self.currColor)
            self.cvs.lower(self.bg)
        
    def buildWall(self, index):
        self.walls[index] = True

    def drawWalls(self):
        for w,wall in enumerate(self.walls):
            if wall:
                self.drawWall(w)

    def drawLines(self, lineLst, index):
        if self.bg:
            if index == Cell.RIGHT_WALL: 
                lineLst[Cell.RIGHT_WALL] = self.cvs.create_line(self.x2, self.y1, self.x2, self.y2, width=self.wallThickness, fill=self.wallColor,  tag="wall")
            elif index == Cell.BOTTOM_WALL: 
                lineLst[Cell.BOTTOM_WALL] = self.cvs.create_line(self.x1, self.y2, self.x2, self.y2, width=self.wallThickness, fill=self.wallColor, tag="wall")
            elif index == Cell.LEFT_WALL: 
                lineLst[Cell.LEFT_WALL] = self.cvs.create_line(self.x1, self.y1, self.x1, self.y2, width=self.wallThickness, fill=self.wallColor, tag="wall")
            elif index == Cell.TOP_WALL: 
                lineLst[Cell.TOP_WALL] = self.cvs.create_line(self.x1, self.y1, self.x2, self.y1, width=self.wallThickness, fill=self.wallColor, tag="wall")

    def drawWall(self, index):
        self.drawLines(self.walls, index)
        
    def drawOutline(self, index):
        self.drawLines(self.outlines, index)

    def removeLine(self, lineLst, index):
        val = lineLst[index]
        if type(val) is int:
            self.cvs.delete(val)
        lineLst[index] = None
    
    def removeWall(self,index):
        self.removeLine(self.walls, index)
        
    def removeOutline(self, index):
        self.removeLine(self.outlines, index)

    def highlight(self, color, outlineColor = "black"):
        self.hRect = self.cvs.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=color, width=self.wallThickness, outline =outlineColor )

    def unhighlight(self):
        self.cvs.delete(self.hRect)

    def changeColor(self, color):
        self.currColor=color
        if self.bg:
            self.cvs.itemconfig(self.bg, fill=self.currColor, outline=self.currColor)
            self.cvs.lower(self.bg)

    def markAsObstacle(self, color):
        self.currColor=color
        self.isObstacle = True
        if self.bg:
            self.cvs.itemconfig(self.bg, fill=color, outline=color)
            self.cvs.lift(self.bg)
        
        
class Grid:
    def __init__(self, cvs, topLeft, dim, cellSize, bgColor = "white", wallColor = "black", wallThickness = 4):
        self.cellSize = cellSize
        if type(cellSize) is not tuple:
            self.cellSize = (cellSize, cellSize)
            
        self.topLeft = topLeft
        self.dim = dim
        self.cvs = cvs
        self.bgColor = bgColor
        self.grid=[]
        self.setUpGrid(wallColor, wallThickness)
        self.root = None
        self.wallsBuilt  = False

    def setUpGrid(self, wallColor, wallThickness):
        for row in range(self.dim[0]):
            lst=[]
            for colm in range(self.dim[1]):
                x = self.topLeft[0]+colm*self.cellSize[0]
                y = self.topLeft[1]+row*self.cellSize[1]
                cell = Cell(x, y, x+self.cellSize[0], y+self.cellSize[1], (row, colm), self.cvs, thickness=wallThickness, origColor = self.bgColor)
                cell.wallColor=wallColor
                lst.append(cell)
            self.grid.append(lst)
                
    
    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()
                cell.drawWalls()
        
    def buildWalls(self):
        self.wallsBuilt  = True
        for row in self.grid:
            for cell in row:
                for i in [Cell.RIGHT_WALL, Cell.BOTTOM_WALL]:
                    cell.buildWall(i)
                    
        for eachCell in self.grid[0]:
            eachCell.buildWall(Cell.TOP_WALL)
    
        for eachRow in self.grid:
            cell = eachRow[0]
            cell.buildWall(Cell.LEFT_WALL)

    def setRootObject(self, root):
        self.root=root

    def getCellFromCoords(self, x, y):
        if x > self.topLeft[0] and y > self.topLeft[1] and x < self.topLeft[0]+self.dim[1]*self.cellSize[0] and y < self.topLeft[1]+self.dim[0]*self.cellSize[1]:
            xLen = x - self.topLeft[0]
            yLen = y - self.topLeft[1]
            colm=int((xLen-(xLen%self.cellSize[0]))/self.cellSize[0])
            row=int((yLen-(yLen%self.cellSize[1]))/self.cellSize[1])
            return self.grid[row][colm]

    #only takes 2 adj cells (includes wrap around)
    def getCommonWallIndex(self,cell_1, cell_2):
        row_diff = cell_1.index[0] - cell_2.index[0]
        colm_diff = cell_1.index[1] - cell_2.index[1]

        #for wrap around
        if abs(row_diff) == self.dim[0]-1:
            row_diff = -1*row_diff/abs(row_diff)
        elif abs(colm_diff) == self.dim[1]-1:
            colm_diff = -1*colm_diff/abs(colm_diff)
            
        if row_diff != 0:
            if row_diff == 1:
                return (cell_2,Cell.BOTTOM_WALL)           #bottom
            return (cell_1,Cell.BOTTOM_WALL)               
        
        if colm_diff == 1:
            return (cell_2, Cell.RIGHT_WALL)              #right
        return (cell_1, Cell.RIGHT_WALL)
        
    def removeCommonWall(self, currCell, adjCell):
        wallInfo = self.getCommonWallIndex(currCell, adjCell)
        cell = wallInfo[0]
        ind = wallInfo[1]
        cell.removeWall(ind)   
            

    def isValidInd(self, ind):
        if ind[0] >= 0 and ind[0] < self.dim[0] and ind[1] >=0 and ind[1] < self.dim[1]:
            return True
        return False
        
    def getUnvisitedNeighbours(self, cell):
        row = cell.index[0]
        colm = cell.index[1]

        neighbours=[]
        for i in range(2):
            for offset in [1,-1]:
                ind=[row, colm]
                ind[i]+= offset
                if self.isValidInd(ind):
                    neighbour = self.grid[ind[0]][ind[1]]
                    if not neighbour.visited and not neighbour.isObstacle:
                        neighbours.append(neighbour)

        return neighbours

    def getNeighbours(self, cell):
        neighbours=[]
        for i in range(cell.index[0]-1, cell.index[0]+2):
            for j in range(cell.index[1]-1, cell.index[1]+2):
                if self.isValidInd([i,j]) and (i!=cell.index[0] or j!=cell.index[1]):
                    neighbours.append(self.grid[i][j])

        return neighbours

    def getHeuristic(self, cell_1, cell_2):
        return math.pow(cell_1.index[0] - cell_2.index[0],2)+math.pow(cell_1.index[1] - cell_2.index[1],2)

    def wallExistsBetween(self, current, neighbour):
        if neighbour.isObstacle:
            return True
        
        if not current.walls and not neighbour.walls:
            return False
        #diagonal neighbours
        row_diff = current.index[0] - neighbour.index[0]
        colm_diff = current.index[1] - neighbour.index[1]
        
        if row_diff!=0 and colm_diff!=0:
            r = neighbour.index[0]+row_diff
            c = neighbour.index[1]+colm_diff
            if self.grid[r][neighbour.index[1]].isObstacle or self.grid[neighbour.index[0]][c].isObstacle:
                return True
            elif not self.grid[r][neighbour.index[1]].isObstacle and not self.grid[neighbour.index[0]][c].isObstacle:
                return True
                
            for cell in [neighbour, current]:
                diff=[row_diff, colm_diff]
                for i, cellInd in enumerate(cell.index):
                    indices = [cell.index[0], cell.index[1]]
                    d=diff[i]
                    indices[i]=cellInd + d
                    wallInfo = self.getCommonWallIndex(cell, self.grid[indices[0]][indices[1]])
                    c = wallInfo[0]
                    ind = wallInfo[1]
                    if c.walls[ind] is not None:
                        return True
                row_diff*=-1
                colm_diff*=-1
            return False 

        #horizonal and vertical neighbours
        wallInfo = self.getCommonWallIndex(current, neighbour)
        if wallInfo[0].walls[wallInfo[1]] is None:
            return False
        return True
        

    def createMaze(self, animate=False):
        if not self.wallsBuilt:
            self.buildWalls()
            
        col="light green"
        initial= self.grid[random.randrange(0,self.dim[0])][random.randrange(0,self.dim[1])]
        initial.visited = True
        if animate:
            initial.changeColor(col)
        stack = [initial]
        while len(stack)!=0:
            current = stack.pop()
            if animate:
                current.highlight("light blue")
            unvisitedNeighbours = self.getUnvisitedNeighbours(current)
            if len(unvisitedNeighbours) > 0:
                stack.append(current)
                chosen = random.choice(unvisitedNeighbours)
                chosen.visited=True
                
                if animate:
                    chosen.changeColor(col)
                    chosen.highlight("blue")
                    
                self.removeCommonWall(current, chosen)
                stack.append(chosen)
                
            if animate and self.root:
                self.root.update()
                time.sleep(0.05)
                current.unhighlight()
                chosen.unhighlight()

    def drawPath(self, endPt, animate, showPath):
        pathCells=[]
        while endPt.previous:
            pathCells.append(endPt)
            endPt = endPt.previous

        pathCells.reverse()
        if showPath:
            for cell in pathCells[:len(pathCells)-1]:
                cell.changeColor("blue")
                if self.root and animate:
                    self.root.update()
                    time.sleep(0.01)

        return pathCells
                

    def findPath(self, startPt, endPt, animate=False, showPath=False, getNextStep = False):
        #cost 0 as we are at start node.
        startPt.g = 0
        openSet=[startPt]
        visitedCells=[]

        while len(openSet)> 0:
            openSet.sort(key=lambda cell: cell.f)
            current = openSet[0]
            
            if current == endPt:
                pathCells = self.drawPath(current, animate, showPath)
                self.resetForPathFinding(startPt, visitedCells)
                if getNextStep and pathCells:
                    return pathCells[0]
                return pathCells
            
            openSet.remove(current)
            
            neighbours = self.getNeighbours(current)
            for neighbour in neighbours:
                if not self.wallExistsBetween(current, neighbour) :
                    tent_g = current.g + ((current.index[0]-neighbour.index[0])**2 + (current.index[1]-neighbour.index[1])**2)/10
                    if tent_g < neighbour.g:
                        neighbour.g = tent_g
                        neighbour.previous = current
                        neighbour.f = neighbour.g + self.getHeuristic(neighbour, endPt)
                        if neighbour not in openSet:
                            visitedCells.append(neighbour)
                            openSet.append(neighbour)
                            if animate and self.root and neighbour!=endPt:
                                self.root.update()
                                neighbour.changeColor("green")
                                
        self.resetForPathFinding(startPt, visitedCells)
        return False

    def findLongestPath(self, startPt, endPt, animate = False, showPath = False, getNextStep = False):
        #has problems
        finishedPairs = []
        restartPtr = 1
        pathCells = self.findPath(startPt, endPt, animate = False, showPath = False)
        if not pathCells:
            return []
        while True:
            i = restartPtr
            pair = [pathCells[i-1], pathCells[i]]
            while pair in finishedPairs and i < len(pathCells):
                i+=1
                if i < len(pathCells):
                    pair = [pathCells[i-1], pathCells[i]]
                    
            restartPtr = i
            if i == len(pathCells):
                break
                
            comDimInd = 0
            if pair[0].index[1] == pair[1].index[1]:
                comDimInd = 1

            while True:
                extendable = False
                for j in [1,-1]:
                    extPair = []
                    for cell in pair:
                        ind = [cell.index[0], cell.index[1]]
                        ind[comDimInd]+=j
                        extPair.append(self.grid[ind[0]][ind[1]])

                    if not extPair[0].isObstacle and extPair[0] not in pathCells and extPair[1] not in pathCells:                
                        pathCells.insert(pathCells.index(pair[1]),extPair[0])
                        pathCells.insert(pathCells.index(pair[1]),extPair[1])
                        extendable = True
                        pair = extPair
                        break
                    
                if not extendable:
                    finishedPairs.append(pair)
                    break

        if showPath:
            for cell in pathCells[1:len(pathCells)-1]:
                cell.changeColor("blue")
                if self.root and animate:
                    self.root.update()
                    time.sleep(0.01)
                
        if getNextStep:
            return pathCells[1]
        return pathCells
    
    def removeRandomWalls(self, perc):
        for row in self.grid:
            for cell in row:
                val = random.randrange(0,100)
                if val < perc:
                    if cell.index[1] != self.dim[1]-1:
                        cell.removeWall(Cell.RIGHT_WALL)
                    if cell.index[0] != self.dim[0]-1:
                        cell.removeWall(Cell.BOTTOM_WALL)

    def resetForPathFinding(self, start, visitedCells):
        resetingCells = [start] + visitedCells
        for cell in resetingCells:
            cell.f = 0
            cell.g = math.inf
            cell.previous = None
        
    def reset(self):
        if self.root:
            self.root.update()
        self.cvs.delete("wall")
        self.wallsBuilt = False
        for row in self.grid:
            for cell in row:
                cell.changeColor(cell.origColor)
                cell.f=0
                cell.g = math.inf
                cell.visited = False
                cell.previous=None
                cell.currColor = cell.origColor
                if cell.isObstacle:
                    cell.isObstacle = False
                cell.walls=[None]*4
                cell.draw()
                         

if __name__ == "__main__":
    root=Tk()
    root.title("Maze Generation")

    _ht=600
    _width=700

    canvas=Canvas(root, bg="white",height=_ht, width=_width)
    canvas.pack(side=LEFT)

    mazes=[]
    maze = Grid(canvas, topLeft=(20,20), dim=(15,20), cellSize=(16,16))
    maze.setRootObject(root)
    maze.buildWalls()
    maze.draw()
    root.update()
    mazes.append(maze)

    maze = Grid(canvas, topLeft=(370,20), dim=(22,15), cellSize=(15,20))
    maze.setRootObject(root)
    maze.buildWalls()
    for i in range(80):
        r = random.randrange(0,maze.dim[0])
        c = random.randrange(0,maze.dim[1])
        maze.grid[r][c].markAsObstacle("grey")
    maze.draw()
    root.update()
    mazes.append(maze)
    
    for maze in mazes:
        maze.createMaze(animate=True)
        
    root.mainloop()
