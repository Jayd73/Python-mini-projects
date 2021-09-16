from tkinter import *
from SnakeGame import *
from MazeGeneration import Cell
import time
import math


root=Tk()
root.title("Snake Game")

_ht = 440
_width = 615
canvas = Canvas(root, bg = "white", height=_ht, width=_width)
canvas.pack(fill=X)

#both dim must be even for constructing h-cycle, as both dim are gonna be divided by 2
#gDim = (22, 30)
gDim = (14, 20)
ground = Ground(canvas,(10,10), 30, gDim, isWrappingAround = False, bgColor = "black")

#place the snake after creating the cycle.
root.update()

#trying hamiltionian
def getHamiltonianCycleCells(ground):
    dimen = [ground.dim[0], ground.dim[1]]
    startInd = (0,0)
    if not ground.isWrappingAround:
        #excluding borders
        dimen[0]-=2
        dimen[1]-=2
        startInd = (1,1)

    smallerDim = (int(dimen[0]/2), int(dimen[1]/2))
    maze = Ground(canvas, (0,0), ground.cellSize[0],smallerDim, isWrappingAround = True)
    maze.createMaze()

    #stretching the maze
    for i in range(maze.dim[0]):
        for j in range(maze.dim[1]):
            r = i*2 + startInd[0]
            c = j*2 + startInd[1]
            cell = maze.grid[i][j]
            quartet = []
            for m in [0,1]:
                for n in [0,1]:
                    newCell = ground.grid[r+m][c+n]
                    quartet.append(newCell)
                    for w, wall_id in enumerate(cell.walls):
                        if wall_id:
                            newCell.buildWall(w)

            for m in [0,3]:
                for n in [1,2]:
                    if ground.wallExistsBetween(quartet[m], quartet[n]):
                        ground.removeCommonWall(quartet[m], quartet[n])

    c = 1+startInd[1]
    for i in range(dimen[0]):
        r = i + startInd[0]
        ground.grid[r][c].removeWall(Cell.LEFT_WALL)

    r = 1+startInd[0]
    for j in range(dimen[1]):
        c = j + startInd[1]
        ground.grid[r][c].removeWall(Cell.TOP_WALL)
    
    #traversing the maze to create h-cycle
    traverser = Snake(ground, startInd, length = 2)

    #when startInd is (1,1) the ground will wrap to (0,0) instead of (1,1).
    #but as there will always be a wall for edge cells, it does not affect the neighbour selection.
    rows = dimen[0] + startInd[0]
    colms = dimen[1] + startInd[1]
    
    h_cycleCells=[]
    nextCell = None
    startCell = traverser.getCellAt(startInd)
    
    while nextCell != startCell:
        headInd = traverser.bodyPartInd[0]
        head = traverser.getCellAt(headInd)
        rightDir = (traverser.heading[1], -traverser.heading[0])
        leftDir = (-rightDir[0], -rightDir[1])
        directions = [leftDir, traverser.heading, rightDir]

        for direction in directions:
            ind = ( (headInd[0]+direction[0])%rows, (headInd[1]+direction[1])%colms )
            cell = traverser.getCellAt(ind)
            if not traverser.ground.wallExistsBetween(head, cell):
                nextCell = cell
                traverser.moveToAdjCell(nextCell)
                h_cycleCells.append(nextCell)
                break

    traverser.removeFromGround()
    return h_cycleCells

def drawRoute(pathCells):
    loopLen = len(pathCells)    #i.e dimen[0]*dimen[1] for H-cycle
    for i in range(loopLen):
        cell_1 = pathCells[i]
        cell_2 = pathCells[(i+1)%loopLen]
        canvas.create_line(cell_1.x, cell_1.y, cell_2.x, cell_2.y, width = 2, fill="blue", tag = "route")

pathCells = getHamiltonianCycleCells(ground)
ground.draw()
snake = Snake(ground, (1,2))

showCycle = True
def handlePathVisibility():
    global showCycle
    if showCycle:
        drawRoute(pathCells)
        showBtn.config(text = "Hide Hamiltonian cycle")
    else:
        canvas.delete("route")
        showBtn.config(text = "Show Hamiltonian cycle")
    showCycle = not showCycle
    
scoreLabel = Label(root, text = "Score:0", font = ("Fira Code", 30, "bold"))
scoreLabel.pack(side = LEFT, padx = 10)
showBtn = Button(root, text="Show Hamiltonian cycle", font = ("Fira Code", 18, "bold"), command=handlePathVisibility, height=1, width=22)
showBtn.pack(side = RIGHT, padx = 3)

#taking shortcuts while following hamiltonian cycle
snake.foodInd = snake.ground.placeFoodAtRandom()
foodCell = snake.getCellAt(snake.foodInd)
fInd = pathCells.index(foodCell)
snakeLen = 2
hCycleLen = len(pathCells)

a = time.time()

while True:
    head = snake.getCellAt(snake.bodyPartInd[0])
    tail = snake.getCellAt(snake.bodyPartInd[-1])

    hInd = pathCells.index(head)
    tInd = pathCells.index(tail)
      
    sInd = -1
    selectedCell = None
        
    for nCell in snake.ground.getNeighbours(head):
        if not nCell.isObstacle:
            nInd = pathCells.index(nCell)
            if nInd <= fInd and sInd < nInd:
                selectedCell = nCell
                sInd = nInd
    
    if selectedCell and snakeLen <= hCycleLen/2  and ((hInd > tInd and (sInd > hInd or sInd < tInd)) or (hInd < tInd and (sInd > hInd and sInd < tInd))):
        nextCell = selectedCell
    else:
        nextCell = pathCells[(hInd+1)%hCycleLen]
        
    snake.moveToAdjCell(nextCell)
    if snake.ateFood():
        snakeLen+=1
        scoreLabel.config(text = "Score:"+str((snakeLen-2)*10))
        snake.grow()
        snake.foodInd = snake.ground.placeFoodAtRandom()
        if not snake.foodInd:
            break
        foodCell = snake.getCellAt(snake.foodInd)
        fInd = pathCells.index(foodCell)
           
    root.update()
        
b = time.time()
print("Snake Won !")
print("Time: ",b-a," secs")
#ground.draw()
root.mainloop()

    
    
    
