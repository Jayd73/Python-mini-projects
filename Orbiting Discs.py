from tkinter import *
import math
import random

class Disc:
    def __init__(self, disc_rad, orbit_rad, start_ang = 0, step_ang_size = 0.1):
        self.disc_rad = disc_rad
        self.orbit_rad = orbit_rad
        self.curr_ang = start_ang
        self.step_ang_size = step_ang_size
        self.pos = None
        
    def draw(self, cvs):
        x = self.pos[0]
        y = self.pos[1]
        cvs.create_oval(x - self.disc_rad, y - self.disc_rad, x + self.disc_rad, y + self.disc_rad, outline = "white", fill = "grey", tag = "orb_disc")

    def set_pos(self, pos):
        self.pos = pos

    def orbit_around(self, parent):
        x = parent.pos[0] + self.orbit_rad * math.cos(math.radians(self.curr_ang))
        y = parent.pos[1] + self.orbit_rad * math.sin(math.radians(self.curr_ang))
        self.set_pos((x, y))
        self.curr_ang = (self.curr_ang + self.step_ang_size) % 360


class OrbitingSystem:
    def __init__(self, root, center = None):
        self.center = center
        self.root = root
        self.root.set_pos(center)
        self.children = []      
    
    def add_disc(self, disc):
        self.children.append(OrbitingSystem(disc))

    def add_orbiting_sys(self, orb_sys):
        self.children.append(orb_sys)

    def calc_positions(self):
        queue = [self]
        while queue:
            parent = queue.pop(0)
            for child in parent.children:
                child.root.orbit_around(parent.root)
                queue.append(child)

    def draw(self, cvs):
        cvs.delete("orb_disc")
        self.root.draw(cvs)
        stack = self.children[:]
        while stack:
            child_sys = stack.pop()
            child_sys.root.draw(cvs)
            stack.extend(child_sys.children)


rootWin = Tk()
rootWin.title("Orbiting Discs")

WIDTH = 800
HEIGHT = 600

fg_color = "white"
bg_color = "black"

canvas = Canvas(rootWin, bg = bg_color, height = HEIGHT, width = WIDTH)
canvas.pack(side = LEFT)

orb = OrbitingSystem(Disc(50, 100, 0, 0.1), (WIDTH / 2, HEIGHT / 2))

child_orb = OrbitingSystem(Disc(30, 150, 0, 0.05))
child_orb.add_disc(Disc(10, 70, 0, -0.1))
child_orb.add_disc(Disc(20, 90, 0, 0.15))

child_orb1 = OrbitingSystem(Disc(40, 250, 90, 0.15))
child_orb1.add_disc(Disc(10, 70, 23, -0.1))
child_orb1.add_disc(Disc(20, 90, 89, 0.2))
child_orb1.add_disc(Disc(10, 100, 67, -0.1))
child_orb1.add_disc(Disc(5, 80, 10, 0.4))

orb.add_orbiting_sys(child_orb)
orb.add_orbiting_sys(child_orb1)

while True:
    orb.calc_positions()
    orb.draw(canvas)
    rootWin.update()

rootWin.mainloop()



