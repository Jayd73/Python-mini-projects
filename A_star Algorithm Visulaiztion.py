from tkinter import *
from MazeGeneration import *

# The A* path finding algorithm is implemented in the findPath() method of Grid class in MazeGeneration.py module 

root=Tk()
root.title("A* Path finding")

_ht=600
_width=800

canvas=Canvas(root, bg="white",height=_ht, width=_width)
canvas.pack(side=LEFT)
    
maze = Grid(canvas, topLeft=(20,20), dim=(43,59), cellSize=(13,13))
maze.setRootObject(root)

maze.buildWalls()
maze.removeRandomWalls(perc=100)
maze.draw()

terminalCells = []
def markPts(event):
    if len(terminalCells) < 2:
        cell = maze.getCellFromCoords(event.x, event.y)
        cell.changeColor("orange")
        terminalCells.append(cell)
        if len(terminalCells) == 2:
            found = maze.findPath(terminalCells[0], terminalCells[1], animate = var.get(), showPath = True)
            if found:
                print("Path Found !")
            else:
                print("Cannot find a path")
            del terminalCells[:]

def createObstacle(event):
    cell = maze.getCellFromCoords(event.x, event.y)
    if cell and not cell.isObstacle:
        cell.markAsObstacle("black")

def createMazeOntheGrid():
    maze.reset()
    maze.createMaze()
    maze.draw()
    terminalCells=[]
    
def clear():
    maze.reset()
    maze.buildWalls()
    maze.removeRandomWalls(perc=100)
    maze.draw()
    terminalCells=[]
    
# Right click to select start and end points
# Left click + drag to draw obstacles
canvas.bind("<Button-3>", markPts)
canvas.bind("<B1-Motion>", createObstacle)

Button(root, text="Create Maze", command=createMazeOntheGrid, height=5, width=20).pack(fill=X, padx=1)
Button(root, text="Clear All", command=clear, height=5, width=20).pack(fill=X, padx=1)
var=BooleanVar()
showVisited=Checkbutton(root, text="Show visited cells", variable=var, onvalue=True, offvalue=False)
showVisited.pack(fill=X, padx=3, pady=6)
var.set(True)
root.mainloop()
