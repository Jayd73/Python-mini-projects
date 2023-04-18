import pygame, sys
import math
import random as rd
from pygame import Rect, Surface

class Maze:
    def __init__(self, screen, anchor_pt, room_size, dim = None, layers = None, wall_thickness = 4):
        self.screen = screen
        self.room_size = room_size
        self.wall_thickness = wall_thickness
        self.wall_col = (255, 255, 255)
        self.floor_col = (0, 0, 0)
        self.visited_highlight_col = (0, 0, 255)
        self.curr_highlight_col = (255, 0, 0)
        self.top_left = anchor_pt
        self.center_pt = anchor_pt if layers else None
        self.layers = layers
        self.dim = dim
        if not self.dim:
            self.set_vars_for_poly_shaped_maze()
            self.maze_grid = self.generate_shaped_maze_grid()
        else:
            self.strt_colm_inds = [0] * self.dim[0]
            # end bound is actual bound + 1 so it can be used in range() as it is.
            self.end_colm_inds = [self.dim[1]] * self.dim[0]        
            self.maze_grid = self.generate_reg_maze_grid()
        self.maze_surface = Surface(self.get_maze_wdth_ht())
        self.maze_surface.fill(self.floor_col)
        self.screen.blit(self.maze_surface, self.top_left)
        row = rd.choice(range(self.dim[0]))
        colm = rd.choice(range(self.strt_colm_inds[row], self.end_colm_inds[row]))
        self.stack, self.visited = [(row, colm)], [(row, colm)]
    
    def get_tot_room_walls(self):
        return 4

    def get_maze_wdth_ht(self):
        return (self.room_size * self.dim[1], 
                self.room_size * self.dim[0])
    
    def set_vars_for_poly_shaped_maze(self):
        self.dim = (self.layers, self.layers)
        wdth, ht = self.get_maze_wdth_ht()
        x, y = self.center_pt
        self.top_left = (x - wdth / 2, y - ht / 2)
        self.strt_colm_inds = [0] * self.layers
        self.end_colm_inds = [self.layers] * self.layers

    def generate_reg_maze_grid(self):
        return {(i, j): [1] * self.get_tot_room_walls() for i in range(self.dim[0]) for j in range(self.dim[1])}

    def generate_shaped_maze_grid(self):
        grid = {}
        for i in range(self.dim[0]):
            for j in range(self.strt_colm_inds[i], self.end_colm_inds[i]):
                # for wall_idx in range(len(grid[i][j])):
                grid[(i, j)] = [1] * self.get_tot_room_walls()
        return grid

    def get_vertices(self, room_idx):
        i, j = room_idx
        tl_x = j * self.room_size
        tl_y = i * self.room_size
        return [
            (tl_x, tl_y),
            (tl_x + self.room_size, tl_y),
            (tl_x + self.room_size, tl_y + self.room_size),
            (tl_x, tl_y + self.room_size)
        ]
    
    def get_comman_wall_inds(self, idx1, idx2):
        r1, c1 = idx1
        r2, c2 = idx2
        if r1 - r2 == 1: comm_wall_inds = [0, 2]
        elif r1 - r2 == -1: comm_wall_inds = [2, 0]
        elif c1 - c2 == 1: comm_wall_inds = [3, 1]
        elif c1 - c2 == -1: comm_wall_inds = [1, 3]
        return comm_wall_inds

    def is_valid_idx(self, idx):
        i, j = idx
        if i >= 0 and i < self.dim[0]:
            if j >= self.strt_colm_inds[i] and j < self.end_colm_inds[i]:
                return True
        return False
    
    def get_neighbours(self, idx):
        i, j = idx
        neighbour_inds = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        return [idx for idx in neighbour_inds if self.is_valid_idx(idx)]

    def rmv_common_wall(self, idx1, idx2):
        r1, c1 = idx1
        r2, c2 = idx2
        comm_wall_inds = self.get_comman_wall_inds(idx1, idx2)
        self.maze_grid[(r1, c1)][comm_wall_inds[0]] = 0
        self.maze_grid[(r2, c2)][comm_wall_inds[1]] = 0

    def highlight_room(self, room_idx, color):
        vertices = self.get_vertices(room_idx)
        pygame.draw.polygon(self.maze_surface, color, vertices)

    def draw_wall(self, room_idx, wall_idx):
        vertices = self.get_vertices(room_idx)
        side_coords = [[vertices[i], vertices[(i + 1) % len(vertices)]] for i in range(len(vertices))]
        pygame.draw.line(self.maze_surface, self.wall_col, *side_coords[wall_idx], width = self.wall_thickness)
    
    def create_maze(self, max_iter = math.inf):
        count = 0
        while count < max_iter and self.stack:
            curr_room = self.stack.pop()
            if max_iter != math.inf: self.highlight_room(curr_room, self.visited_highlight_col)
            neighbours = self.get_neighbours(curr_room)
            unvisited = [neighb for neighb in neighbours if neighb not in self.visited]
            if unvisited:
                self.stack.append(curr_room)
                chosen_room = rd.choice(unvisited)
                self.rmv_common_wall(curr_room, chosen_room)
                self.visited.append(chosen_room)
                self.stack.append(chosen_room)
                if max_iter != math.inf: self.highlight_room(chosen_room, self.curr_highlight_col)
            elif max_iter != math.inf:
                self.highlight_room(curr_room, self.floor_col)
                if self.stack: self.highlight_room(self.stack[-1], self.curr_highlight_col)
            count += 1
            self.screen.blit(self.maze_surface, self.top_left)
        # if not self.stack:
        #     print(self.maze_grid)

    def show_maze_generation(self):
        self.create_maze(max_iter = 1)
        self.draw_maze()

    def get_expanded(self, exp_by, top_left = None):
        if type(self) == Maze:
            e1, e2 = exp_by
            new_top_left = top_left if top_left else self.top_left
            new_dim = (self.dim[0] * e1, self.dim[1] * e2)
            exp_maze = Maze(self.screen, new_top_left, self.room_size, dim = new_dim)
            exp_maze.stack = [] if not self.stack else exp_maze.stack
            exp_maze.maze_grid = {(i, j): [0] * 4 for i in range(exp_maze.dim[0]) for j in range(exp_maze.dim[1])}
            for i in range(self.dim[0]):
                for j in range(self.dim[1]):
                    for k in range(i * e1, (i + 1) * e1):
                        exp_maze.maze_grid[(k, (j + 1) * e2 - 1)][1] = self.maze_grid[(i, j)][1]
                        exp_maze.maze_grid[(k, j * e2)][3] = self.maze_grid[(i, j)][3]
                    for k in range(j * e2, (j + 1) * e2):
                        exp_maze.maze_grid[(i * e1, k)][0] = self.maze_grid[(i, j)][0]
                        exp_maze.maze_grid[((i + 1) * e1 - 1, k)][2] = self.maze_grid[(i, j)][2]
            return exp_maze
        raise Exception("{} can not be expanded".format(type(self).__name__))

    # function for debugging
    def draw_maze_boundary(self):
        wdth, ht = self.get_maze_wdth_ht()
        pygame.draw.rect(self.maze_surface, self.wall_col, Rect(0, 0, wdth, ht), width = 1)

    def draw_maze(self):
        # self.draw_maze_boundary()
        for i in range(self.dim[0]):
            for j in range(self.strt_colm_inds[i], self.end_colm_inds[i]):
                walls = self.maze_grid[(i, j)]
                for k, wall in enumerate(walls):
                    if wall: self.draw_wall((i, j), k)
            self.screen.blit(self.maze_surface, self.top_left)


class TriangleMaze(Maze):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_tot_room_walls(self):
        return 3
    
    def get_maze_wdth_ht(self):
        wdth = self.room_size * self.dim[1]
        ht = self.room_size * self.dim[0]
        return (wdth / 2 + self.room_size / 2, ht)
    
    def set_vars_for_poly_shaped_maze(self):
        self.dim = (self.layers, 2 * self.layers - 1)
        wdth, ht = self.get_maze_wdth_ht()
        x, y = self.center_pt
        self.top_left = (x - wdth / 2, y - ht / 2)
        self.strt_colm_inds = [i for i in range(self.dim[1] // 2, -1, -1)]
        self.end_colm_inds = [self.strt_colm_inds[i] + 2 * i + 1 for i in range(self.layers)]
    
    def get_vertices(self, room_idx):
        i, j = room_idx
        tl_x = j * self.room_size / 2
        tl_y = i * self.room_size
        # if pointing up, right - 0, btm - 1, left - 2
        # if pointing down, right - 0, left - 1, top - 2
        # ordering of coords is imp. Do not Change
        tri_coords = ((tl_x + self.room_size / 2, tl_y), (tl_x + self.room_size, tl_y + self.room_size), (tl_x, tl_y + self.room_size))
        inv_tri_coords = ((tl_x + self.room_size, tl_y),  (tl_x + self.room_size / 2, tl_y + self.room_size), (tl_x, tl_y))
        coords = [tri_coords, inv_tri_coords]
        return coords[self.get_tri_direction(room_idx)]

    def get_tri_direction(self, idx):
        # 0 for up, 1 for down
        i, j = idx
        direc = 0 if self.layers and self.layers % 2 == 0 else 1
        if (i % 2 == 0 and j % 2 == 0) or (i % 2 != 0 and j % 2 != 0): direc = 1 - direc
        return direc
    
    def get_neighbours(self, idx):
        i, j = idx
        neighbour_inds = [(i, j - 1), (i, j + 1)]
        row_offset = 1 if self.get_tri_direction(idx) == 0 else -1
        neighbour_inds.append((i + row_offset, j))
        return [idx for idx in neighbour_inds if self.is_valid_idx(idx)]

    def get_comman_wall_inds(self, idx1, idx2):
        r1, c1 = idx1
        r2, c2 = idx2
        direc = self.get_tri_direction(idx1)
        if r1 - r2 == 1: comm_wall_inds = [2, 1]
        elif r1 - r2 == -1: comm_wall_inds = [1, 2]
        elif  direc == 0:
            if c1 - c2 == 1: comm_wall_inds = [2, 0]
            elif c1 - c2 == -1: comm_wall_inds = [0, 1]
        elif direc == 1: 
            if c1 - c2 == 1: comm_wall_inds = [1, 0]
            elif c1 - c2 == -1: comm_wall_inds = [0, 2]
        return comm_wall_inds


class HexagonMaze(Maze):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_tot_room_walls(self):
        return 6
    
    def get_maze_wdth_ht(self):
        room_box_size = (math.sqrt(3) * self.room_size, 2 * self.room_size)
        wdth = room_box_size[0] * self.dim[1]
        if self.dim[0] > 1: wdth += room_box_size[0] / 2
        ht = room_box_size[1] * math.ceil(self.dim[0] / 2) + self.room_size * (self.dim[0] // 2)
        if self.dim[0] % 2 == 0: ht += self.room_size / 2
        return (wdth, ht)
    
    def set_vars_for_poly_shaped_maze(self):
        self.dim = (2 * self.layers - 1, 2 * self.layers - 1)
        half_hex_wdth = math.sqrt(3) * self.room_size / 2
        hex_maze_wdth_offset = half_hex_wdth if self.layers % 2 == 0 else -half_hex_wdth
        wdth, ht = self.get_maze_wdth_ht()
        wdth += hex_maze_wdth_offset
        x, y = self.center_pt
        self.top_left = (x - wdth / 2, y - ht / 2)
        self.strt_colm_inds = [int(self.layers // 2 - math.ceil(i / 2)) for i in range(self.layers)]
        self.strt_colm_inds += list(reversed(self.strt_colm_inds))[1:]
        self.end_colm_inds = [self.strt_colm_inds[i] + self.layers + i for i in range(self.layers)]
        self.end_colm_inds += list(reversed(self.end_colm_inds))[1:]

    def get_vertices(self, room_idx):
        i, j = room_idx
        room_box_size = (math.sqrt(3) * self.room_size, 2 * self.room_size)
        half_wdth = room_box_size[0] / 2
        one_frth_ht = room_box_size[1] / 4
        tl_x = j * room_box_size[0] + (i % 2) * half_wdth
        tl_y = i * room_box_size[1] - i * one_frth_ht
        return [
            (tl_x + half_wdth, tl_y),
            (tl_x + room_box_size[0], tl_y + one_frth_ht),
            (tl_x + room_box_size[0], tl_y + one_frth_ht + self.room_size),
            (tl_x + half_wdth, tl_y + room_box_size[1]),
            (tl_x, tl_y + one_frth_ht + self.room_size),
            (tl_x, tl_y + one_frth_ht)
        ]
    
    def get_neighbours(self, idx):
        i, j = idx
        neighbour_inds = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        colm_offset = 1 if i % 2 != 0 else -1
        neighbour_inds += [(i - 1, j + colm_offset), (i + 1, j + colm_offset)]
        return [idx for idx in neighbour_inds if self.is_valid_idx(idx)]
    
    def get_comman_wall_inds(self, idx1, idx2):
        r1, c1 = idx1
        r2, c2 = idx2
        if r1 == r2:
            if c1 - c2 == 1: comm_wall_inds = [4, 1]
            elif c1 - c2 == -1: comm_wall_inds = [1, 4]
        elif r1 % 2 == 0:
            if c1 == c2:
                if r1 - r2 == 1: comm_wall_inds = [0, 3]
                elif r1 - r2 == -1: comm_wall_inds = [2, 5]
            elif c1 - c2 == 1:
                if r1 - r2 == 1: comm_wall_inds = [5, 2]
                elif r1 - r2 == -1: comm_wall_inds = [3, 0]
        else:
            if c1 == c2:
                if r1 - r2 == 1: comm_wall_inds = [5, 2]
                elif r1 - r2 == -1: comm_wall_inds = [3, 0]
            elif c1 - c2 == -1:
                if r1 - r2 == 1: comm_wall_inds = [0, 3]
                elif r1 - r2 == -1: comm_wall_inds = [2, 5]
        return comm_wall_inds


class CircularMaze(Maze):
    def __init__(self, screen, anchor_pt, slices, slice_ht, layers):
        self.init_slices = slices
        super().__init__(screen, anchor_pt, room_size = slice_ht, layers = layers)
        # innermost circle will only have 1 wall i.e the outer arc
        self.maze_grid[(0, 0)] = [1, 0, 0, 0]
        wdth, ht = self.get_maze_wdth_ht()
        self.maze_center_pt = (wdth / 2, ht / 2)
        
    def get_tot_room_walls(self):
        return 4
    
    def get_maze_wdth_ht(self):
        return (2 * self.room_size * (self.layers),) * 2

    def get_slices(self, layer_num):
        if layer_num <= 0: return 1
        return self.init_slices * 2 ** int(math.floor(math.log2(layer_num)))
    
    def set_vars_for_poly_shaped_maze(self):
        self.dim = (self.layers, self.get_slices(self.layers - 1))
        wdth, ht = self.get_maze_wdth_ht()
        x, y = self.center_pt
        self.top_left = (x - wdth / 2, y - ht / 2)
        self.strt_colm_inds = [0] * self.layers
        self.end_colm_inds = [self.get_slices(lay_num) for lay_num in range(self.layers)]

    def get_neighbours(self, idx):
        i, j = idx
        if i == 0: return [(1, c) for c in range(self.get_slices(1))]
        neighbour_inds = [(i, j + 1), (i, j - 1), (i - 1, j)]
        if self.get_slices(i) > self.get_slices(i - 1):
            neighbour_inds[-1] = (i - 1, j // 2)
        neighbour_inds.append((i + 1, j))
        if self.get_slices(i) < self.get_slices(i + 1):
            del neighbour_inds[-1]
            neighbour_inds.extend([(i + 1, 2 * j), (i + 1, 2 * j + 1)])
        neighbour_inds = {(i, j % self.get_slices(i)) for i, j in neighbour_inds}
        return [idx for idx in neighbour_inds if self.is_valid_idx(idx)]
    
    def get_comman_wall_inds(self, idx1, idx2):
        r1, c1 = idx1
        r2, c2 = idx2
        if r1 - r2 == 1: comm_wall_inds = [2, 0]
        elif r1 - r2 == -1: comm_wall_inds = [0, 2]
        elif c1 - c2 == 1 or c1 - c2 == -(self.get_slices(r1) - 1): comm_wall_inds = [1, 3]
        elif c1 - c2 == -1 or c1 - c2 == self.get_slices(r1) - 1: comm_wall_inds = [3, 1]
        return comm_wall_inds

    def get_room_radii(self, layer_num):
        out_rad = (layer_num + 1) * self.room_size
        in_rad = layer_num * self.room_size
        return (out_rad, in_rad)
    
    def get_room_bound_angles(self, room_idx):
        i, j = room_idx
        arc_ang = math.radians(360 / self.get_slices(i))
        strt_ang, end_ang = j * arc_ang, (j + 1) * arc_ang
        return (strt_ang, end_ang)

    def get_vertices(self, room_idx, resolution):
        out_rad, in_rad = self.get_room_radii(room_idx[0])
        x, y = self.maze_center_pt
        strt_ang, end_ang = self.get_room_bound_angles(room_idx)
        turn_ang = (end_ang - strt_ang) / resolution
        out_verts, in_verts = [], []
        for step in range(resolution + 1):
            cos_ang = math.cos(strt_ang + step * turn_ang)
            sin_ang = math.sin(strt_ang + step * turn_ang)
            # mult by -1 as y increases downwards
            out_verts.append((x + in_rad * cos_ang, y + -1 * in_rad * sin_ang))
            in_verts.append((x + out_rad * cos_ang, y + -1 * out_rad * sin_ang))
        return (out_verts, in_verts)

    def draw_wall(self, room_idx, wall_idx):
        out_rad, in_rad = self.get_room_radii(room_idx[0])
        x, y = self.maze_center_pt
        out_box = (x - out_rad, y - out_rad, 2 * out_rad, 2 * out_rad)
        in_box = (x - in_rad, y - in_rad, 2 * in_rad, 2 * in_rad)
        boxes = [out_box, in_box]
        strt_ang, end_ang = self.get_room_bound_angles(room_idx)
        out_verts, in_verts = self.get_vertices(room_idx, resolution = 1)
        if wall_idx % 2 == 0:
            box = boxes[wall_idx // 2]
            pygame.draw.arc(self.maze_surface, self.wall_col, box, strt_ang, end_ang, width = self.wall_thickness)
        else:
            l_strt, l_end = out_verts[wall_idx // 3], in_verts[wall_idx // 3]
            pygame.draw.line(self.maze_surface, self.wall_col, l_strt, l_end, width = self.wall_thickness)
    
    def highlight_room(self, room_idx, color):
        out_verts, in_verts = self.get_vertices(room_idx, resolution = 7)
        in_verts.reverse()
        vertices = out_verts + in_verts
        pygame.draw.polygon(self.maze_surface, color, vertices)

        

WIDTH, HEIGHT = 800, 600
FPS = 60

def main():
    pygame.init()

    main_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Generation")
    clock = pygame.time.Clock()

    tp_lft = (30, 30)
    cent_pt = (WIDTH / 2, HEIGHT / 2)

    # maze = Maze(main_screen, dim = (7, 10), anchor_pt = tp_lft, room_size = 20)
    # maze = TriangleMaze(main_screen, anchor_pt = cent_pt, room_size = 20, layers = 20)
    # maze = HexagonMaze(main_screen, anchor_pt = cent_pt, room_size = 20, layers = 7)
    maze = CircularMaze(main_screen, cent_pt, slices = 8, slice_ht = 20, layers = 10)

    # maze.create_maze()
    # maze.draw_maze()

    # exp_maze = maze.get_expanded(exp_by = (2, 3), top_left = (30, 200))
    # exp_maze.draw_maze()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        maze.show_maze_generation()

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
