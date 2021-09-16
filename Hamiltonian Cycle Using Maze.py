from tkinter import *
from SnakeGame import *
from MazeGeneration import Cell

def stretchMaze(maze):
    vOffset = 20
    topLeft = (maze.topLeft[0],maze.topLeft[1]+maze.dim[0]*maze.cellSize[1]+vOffset)
    newMaze = Ground(canvas, topLeft, maze.cellSize[0], (maze.dim[0]*2,maze.dim[1]*2), isWrappingAround = maze.isWrappingAround, bgColor = "white")
    for i in range(maze.dim[0]):
        for j in range(maze.dim[1]):
            r = i*2
            c = j*2
            cell = maze.grid[i][j]
            quartet = []
            for m in [0,1]:
                for n in [0,1]:
                    newCell = newMaze.grid[r+m][c+n]
                    quartet.append(newCell)
                    for w, wall_id in enumerate(cell.walls):
                        if wall_id:
                            newCell.buildWall(w)

            for m in [0,3]:
                for n in [1,2]:
                    if newMaze.wallExistsBetween(quartet[m], quartet[n]):
                        newMaze.removeCommonWall(quartet[m], quartet[n])

    for i in range(newMaze.dim[0]):
        newMaze.grid[i][1].removeWall(Cell.LEFT_WALL)

    for j in range(newMaze.dim[1]):
        newMaze.grid[1][j].removeWall(Cell.TOP_WALL)
        
    return newMaze

root=Tk()
root.title("Snake Game")

_ht = 650
_width = 1000
canvas = Canvas(root, bg = "white", height=_ht, width=_width)
canvas.pack(fill=X)

maze = Ground(canvas,(10,10), 10, (20,45), isWrappingAround = True, bgColor = "white")
maze.createMaze()
maze.draw()
maze.drawWalls()

newMaze = stretchMaze(maze)
newMaze.draw()
newMaze.drawWalls()
root.update()

startInd = (0,0)
if not newMaze.isWrappingAround:
    startInd = (2,2)
    
traverser = Snake(newMaze, startInd, length = 2)
rows = traverser.ground.dim[0]
colms = traverser.ground.dim[1]

h_cycleIndices = []

nextCell = None
while nextCell != traverser.getCellAt(startInd):
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
            traverser.moveToAdjCell(cell)
            head.highlight("blue", "blue")
            h_cycleIndices.append(cell.index)
            break
    root.update()

for i in range(len(h_cycleIndices)):
    cell_1 = traverser.getCellAt(h_cycleIndices[i])
    cell_2 = traverser.getCellAt(h_cycleIndices[(i+1)%len(h_cycleIndices)])
    canvas.create_line(cell_1.x, cell_1.y, cell_2.x, cell_2.y, width = 2, fill="yellow")
    root.update()

#newMaze.draw()
root.mainloop()












