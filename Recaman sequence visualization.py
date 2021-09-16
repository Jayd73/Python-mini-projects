from tkinter import *
import time

rootWin = Tk()
rootWin.state("zoomed")
rootWin.title("Recaman sequence")


fg_col = "white"
bg_col = "black"

canvas = Canvas(rootWin, bg = bg_col)
canvas.pack(fill = BOTH, expand = True)

rootWin.update()

num = 300
start_x = 10
end_x = canvas.winfo_width() - 10
y_pos = canvas.winfo_height() / 2


gap_size = (end_x - start_x) / num

sequence = [0]

counter = 1
while counter < num + 200:
    curr_num = sequence[counter - 1] - counter
    if curr_num < 0 or curr_num in sequence:
        curr_num = sequence[counter - 1] + counter

    if counter % 2 == 0:
        arc_start = 0
    else:
        arc_start = 180
    
    from_num = sequence[-1]
    x1 = start_x + gap_size * from_num
    x2 = start_x + gap_size * curr_num
    sq_size = abs(x2 - x1)
    y1 = y_pos - sq_size / 2
    y2 = y_pos + sq_size / 2

    canvas.create_arc(x1, y1, x2, y2, start = arc_start, extent = 180, style = ARC, width = 1, outline = fg_col)
    rootWin.update()
    time.sleep(0.01)

    sequence.append(curr_num)
    counter += 1


rootWin.mainloop()



