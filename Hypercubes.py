from tkinter import *
import itertools
import numpy as np
import math
import time

class Hypercube:
    THREE_D_X = 0
    THREE_D_Y = 1
    THREE_D_Z = 2

    FOUR_D_XY = 0
    FOUR_D_XZ = 1
    FOUR_D_XW = 2
    FOUR_D_YZ = 3
    FOUR_D_YW = 4
    FOUR_D_ZW = 5


    def __init__(self, dim, size, pos, dist = 2):
        self.dim = dim
        self.size = size
        self.pos = pos
        self.dist = dist
        self.vertices = self.get_vertices()
        self.edges = self.get_edges()
        self.rot_matrices = self.get_rot_matrices()
    
    def get_vertices(self):
        permutaions = list(itertools.product([ 0.5, -0.5], repeat = self.dim))
        vertices = list(map(list, permutaions))
        return np.array(vertices, dtype = 'float32')

    def get_edges(self):
        edges = []
        bin_vertices = list(itertools.product([0, 1], repeat = self.dim))

        def get_adj_vert(bin_vert):
            adj_vert = []
            for vert in bin_vertices[bin_vertices.index(bin_vert) + 1:]:
                count = sum(1 for b1, b2 in zip(bin_vert, vert) if b1 != b2)
                if count == 1:
                    adj_vert.append(vert)
            return [bin_vertices.index(vert) for vert in adj_vert]

        for i, vert in enumerate(bin_vertices):
            edges.extend([(i, edge_ind) for edge_ind in get_adj_vert(vert)])
        return edges

    def get_rot_matrices(self):
        rot_matrices = {}
        rot_mat_diags = list(set(itertools.permutations([0,0] + [1] * (self.dim - 2))))
        rot_mat_diags.sort(reverse = True)
        for rot_diag in rot_mat_diags:
            rot_mat = np.full(shape = (self.dim, self.dim), fill_value = 0, dtype = 'float32' )
            for i, num in enumerate(rot_diag):
                rot_mat[i, i] = num
            trig_indices = tuple(i for i, n in enumerate(rot_diag) if n == 0)
            rot_matrices[trig_indices] = rot_mat
        return rot_matrices

    def rotate(self, rot_num, ang):
        ang = math.radians(ang)
        rot_item = list(self.rot_matrices.items())[rot_num]
        rot_mat = rot_item[1]
        trig_ind = rot_item[0]
        rot_mat[trig_ind[0], trig_ind[0]] = math.cos(ang)
        rot_mat[trig_ind[1], trig_ind[1]] = math.cos(ang)
        rot_mat[trig_ind[0], trig_ind[1]] = -math.sin(ang)
        rot_mat[trig_ind[1], trig_ind[0]] = math.sin(ang)
        for i, vert in enumerate(self.vertices):
            vert_mat = np.reshape(vert, (-1, 1))
            rotated = np.matmul(rot_mat, vert_mat)
            self.vertices[i] = rotated.flatten()


    def get_projected_vert(self, vertex):

        for i in range(len(vertex) - 1, len(self.pos) - 1, -1):
            percpective = 1 / (self.dist - vertex[i])
            vertex = vertex * percpective

        x = self.pos[0] + vertex[0]  * self.size
        y = self.pos[1] + vertex[1]  * self.size
        return (x, y)

    def draw(self, cvs):
        rad = 5
        projected_vert = []
        cvs.delete('vertices{0} || edges{0}'.format(str(id(self))))
        for i, vertex in enumerate(self.vertices):
            x, y = self.get_projected_vert(vertex)
            projected_vert.append((x, y))
            cvs.create_oval(x - rad, y - rad, x + rad, y + rad, fill = fg_col, outline = fg_col, tag = "vertices" + str(id(self)))
            # cvs.create_text(x - rad * 4, y - rad * 4, text = str(i) , fill = "yellow", font = ("Cambria", 15))
            
        for edge in self.edges:
            x1, y1 = projected_vert[edge[0]]
            x2, y2 = projected_vert[edge[1]]
            cvs.create_line(x1, y1, x2, y2, fill = fg_col, tag="edges" + str(id(self)))


rootWin = Tk()
rootWin.title("Higher Dimensional Cubes")

WIDTH = 500
HEIGHT = 500
fg_col = "white"
bg_col = "#212121"

canvas = Canvas(rootWin, bg = bg_col, width = WIDTH, height = HEIGHT)
canvas.pack(fill = BOTH, expand = True)

hypercube = Hypercube(dim = 4, size = 400, pos = (WIDTH / 2, HEIGHT / 2))
hypercube1 = Hypercube(dim = 4, size = 400, pos = (WIDTH / 2, HEIGHT / 2))

angle = 0.2

while True:
    hypercube.rotate(Hypercube.FOUR_D_YZ, angle)
    hypercube.rotate(Hypercube.FOUR_D_XW, angle)
    hypercube.draw(canvas)
    rootWin.update()

rootWin.mainloop()

