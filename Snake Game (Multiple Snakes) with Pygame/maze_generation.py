import pygame, sys
import math
import random as rd
from pygame import Rect, Surface

class Maze:
    def __init__(self, screen, top_left, room_size, dim, wall_thickness = 4):
        self.screen = screen
        self.room_size = room_size
        self.wall_thickness = wall_thickness
        self.wall_col = (255, 255, 255)
        self.floor_col = (0, 0, 0)
        self.visited_highlight_col = (0, 0, 255)
        self.curr_highlight_col = (255, 0, 0)
        self.top_left = top_left
        self.dim = dim
        self.maze_grid = self.get_reg_maze_grid()
        self.maze_surface = Surface(self.get_maze_wdth_ht())
        self.maze_surface.fill(self.floor_col)
        self.screen.blit(self.maze_surface, self.top_left)
        row = rd.choice(range(self.dim[0]))
        colm = rd.choice(range(self.dim[1]))
        self.stack, self.visited = [(row, colm)], [(row, colm)]
    
    def get_tot_room_walls(self):
        return 4

    def get_maze_wdth_ht(self):
        return (self.room_size * self.dim[1], 
                self.room_size * self.dim[0])

    def get_reg_maze_grid(self):
        return {(i, j): [1] * self.get_tot_room_walls() for i in range(self.dim[0]) for j in range(self.dim[1])}

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
    
    def get_common_wall_inds(self, idx1, idx2):
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
            if j >= 0 and j < self.dim[1]:
                return True
        return False
    
    def get_neighbours(self, idx):
        i, j = idx
        neighbour_inds = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        return [idx for idx in neighbour_inds if self.is_valid_idx(idx)]

    def rmv_common_wall(self, idx1, idx2):
        r1, c1 = idx1
        r2, c2 = idx2
        comm_wall_inds = self.get_common_wall_inds(idx1, idx2)
        self.maze_grid[(r1, c1)][comm_wall_inds[0]] = 0
        self.maze_grid[(r2, c2)][comm_wall_inds[1]] = 0
    
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

    def show_maze_generation(self):
        self.create_maze(max_iter = 1)
        self.draw_maze()

    def get_expanded(self, exp_by, top_left = None):
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
    
    def highlight_room(self, room_idx, color):
        vertices = self.get_vertices(room_idx)
        pygame.draw.polygon(self.maze_surface, color, vertices)

    def draw_wall(self, room_idx, wall_idx):
        vertices = self.get_vertices(room_idx)
        side_coords = [[vertices[i], vertices[(i + 1) % len(vertices)]] for i in range(len(vertices))]
        pygame.draw.line(self.maze_surface, self.wall_col, *side_coords[wall_idx], width = self.wall_thickness)

    def draw_maze(self):
        # self.draw_maze_boundary()
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                walls = self.maze_grid[(i, j)]
                for k, wall in enumerate(walls):
                    if wall: self.draw_wall((i, j), k)
            self.screen.blit(self.maze_surface, self.top_left)


WIDTH, HEIGHT = 800, 600
FPS = 60

def main():
    pygame.init()

    main_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Generation")
    clock = pygame.time.Clock()

    tp_lft = (30, 30)
    cent_pt = (WIDTH / 2, HEIGHT / 2)

    maze = Maze(main_screen, dim = (7, 10), top_left = tp_lft, room_size = 20)

    maze.create_maze()
    maze.draw_maze()

    exp_maze = maze.get_expanded(exp_by = (2, 3), top_left = (30, 200))
    exp_maze.draw_maze()
  
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # maze.show_maze_generation()

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
