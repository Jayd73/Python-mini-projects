from tkinter import *
import random
import time
import numpy as np

rootWin = Tk()
rootWin.title("Langton's Ant")

WIDTH = 1200
HEIGHT = 640

canvas = Canvas(rootWin, bg="white",height = HEIGHT, width = WIDTH)
canvas.pack(side=LEFT)

cell_size = 2
rows = HEIGHT // cell_size
colms = WIDTH // cell_size

states = np.full((rows, colms), 0, dtype=int)
rect_ids = np.full((rows, colms), 0 ,dtype=int)
ant_pos = (rows // 2, colms // 2)
ant_direc = 0   # up - 0, right - 1, down - 2, left - 3
direction_vects = {0: (-1, 0), 1: (0, 1), 2: (1, 0), 3: (0, -1)}
iter_per_frame = 500

def move_forward(ant_pos, direc):
    dir_vect = direction_vects[direc]
    r = (ant_pos[0] + dir_vect[0]) % rows
    c = (ant_pos[1] + dir_vect[1]) % colms
    return (r, c)

while True:
    for i in range(iter_per_frame):
        if states[ant_pos] == 0:
            states[ant_pos] = 1
            x = ant_pos[1] * cell_size
            y = ant_pos[0] * cell_size
            rect_ids[ant_pos] = canvas.create_rectangle(x, y, x + cell_size, y + cell_size, fill = "black")
            ant_direc += 1
        else:
            canvas.delete(rect_ids[ant_pos])
            rect_ids[ant_pos] = 0
            states[ant_pos] = 0
            ant_direc -= 1
        ant_direc %= 4
        ant_pos = move_forward(ant_pos, ant_direc)

    rootWin.update()
    # time.sleep(0.01)

rootWin.protocol("WM_DELETE_WINDOW", lambda: rootWin.destroy())
rootWin.mainloop()