from tkinter import *
import math
import random

class Player:
    def __init__(self):
        pass

class Tile:
    def __init__(self, num, pos, size, bg_color = "white"):
        self.num = num
        self.pos = pos
        self.size = size
        self.center_pos = (self.pos[0] + self.size/2, self.pos[1] + self.size/2)
        self.bg_color = bg_color
        self.ladder_dest = None
        self.snake_end_pos = None

    def draw(self, cvs):
        cvs.create_rectangle(self.pos[0], self.pos[1], self.pos[0] + self.size, self.pos[1] + self.size, fill = self.bg_color)
        cvs.create_text(self.center_pos[0], self.center_pos[1], text = str(self.num), font=('Cambria', str(self.size//3)))

class SnakesAndLaddersBoard:
    def __init__(self, pos, tile_size, dim, tot_snakes = None, tot_ladders = None):
        self.dim = dim
        self.top_left = pos
        self.tile_size = tile_size
        self.unavailable = []
        self.board = self._construct_board()
        self._set_random_ladders(5)
        self._set_random_snakes(5)
    
    def _construct_board(self):
        board_arr = []
        tile_num = 1   # self.dim[0] * self.dim[1]
        alt_colors = ["#c2c2c2", "#757575"]
        for row in range(self.dim[0]):
            tile_row = [None] * self.dim[1]
            colm_indices = list(range(self.dim[1]))
            if row % 2 == 1:
                colm_indices.reverse()
            for colm in colm_indices:
                x = self.top_left[0] + colm * self.tile_size
                y = self.top_left[1] + (self.dim[0] - 1 - row) * self.tile_size
                tile_row[colm] = Tile(tile_num, (x, y), self.tile_size, bg_color = alt_colors[tile_num % 2])
                tile_num += 1
            board_arr.append(tile_row)
        return board_arr

    def _get_mag(self, vect):
        return math.sqrt(vect[0] ** 2 + vect[1] ** 2)

    def _get_normalized(self, vect):
        vect_mag = self._get_mag(vect)
        return [vect[0] / vect_mag, vect[1] / vect_mag]

    def _draw_ladder(self, from_tile, to_tile, cvs):
        ladder_width = 0.2 * self.tile_size
        ladder_col = "black"
        step_size = 20
        ladder_axis = [to_tile.center_pos[0] - from_tile.center_pos[0], to_tile.center_pos[1] - from_tile.center_pos[1]]
        steps = int(self._get_mag(ladder_axis) / step_size)
        norm_lad_axis = self._get_normalized(ladder_axis)
        perp = [norm_lad_axis[1], -norm_lad_axis[0]]

        rail1 = [from_tile.center_pos[0] + perp[0] * ladder_width, from_tile.center_pos[1] + perp[1] * ladder_width, 
                 to_tile.center_pos[0] + perp[0] * ladder_width, to_tile.center_pos[1] + perp[1] * ladder_width]
        
        rail2 = [from_tile.center_pos[0] - perp[0] * ladder_width, from_tile.center_pos[1] - perp[1] * ladder_width, 
                 to_tile.center_pos[0] - perp[0] * ladder_width, to_tile.center_pos[1] - perp[1] * ladder_width]

        cvs.create_line(*rail1, fill = ladder_col, width = 3)
        cvs.create_line(*rail2, fill = ladder_col, width = 3)

        for i in range(1, steps + 1):
            step_pos = [from_tile.center_pos[0] + norm_lad_axis[0] * step_size * i,
                        from_tile.center_pos[1] + norm_lad_axis[1] * step_size * i]

            step = [step_pos[0] + perp[0] * ladder_width, step_pos[1] + perp[1] * ladder_width,
                    step_pos[0] - perp[0] * ladder_width, step_pos[1] - perp[1] * ladder_width,]

            cvs.create_line(*step, fill = ladder_col, width = 3)

    def _draw_snake(self, from_tile, to_tile, cvs):
        step_size, turn_dist, turn_dir = 30, 20, 1
        snake_axis = [to_tile.center_pos[0] - from_tile.center_pos[0] , to_tile.center_pos[1] - from_tile.center_pos[1]]
        norm_axis = self._get_normalized(snake_axis)
        scaled_perp = [norm_axis[1] * turn_dist, -norm_axis[0] * turn_dist]
        body_pts = [from_tile.center_pos[0], from_tile.center_pos[1]]
        if from_tile.center_pos[0] < to_tile.center_pos[1]:
            turn_dir = -1

        turns = int(self._get_mag(snake_axis) / step_size)
        for i in range(turns):
            turn_pos = [from_tile.center_pos[0] + norm_axis[0] * step_size * i,
                        from_tile.center_pos[1] + norm_axis[1] * step_size * i]
            body_pts.append(turn_pos[0] + scaled_perp[0] * turn_dir)
            body_pts.append(turn_pos[1] + scaled_perp[1] * turn_dir)
            turn_dir *= -1
        
        body_pts.extend([to_tile.center_pos[0], to_tile.center_pos[1]])
        cvs.create_line(*body_pts, smooth=True, width = 10, fill = "#0a5c20")

    def _get_tile_indices(self):
        tile_indices = [[(r, c) for c in range(self.dim[1])] for r in range(self.dim[0])]
        del tile_indices[0][0]
        if self.dim[0] % 2 == 0:
            del tile_indices[-1][0]
        else:
            del tile_indices[-1][-1]
        return tile_indices

    
    def _set_random_ladders(self, total):
        counter, min_rows_skipped = 0, 2
        tile_indices = self._get_tile_indices()
        while counter < total:
            base_row_ind = random.choice(list(range(self.dim[0] - min_rows_skipped)))
            base = random.choice(tile_indices[base_row_ind])
            dest = random.choice(random.choice(tile_indices[base_row_ind + min_rows_skipped:]))
            if base not in self.unavailable and dest not in self.unavailable:
                self.board[base[0]][base[1]].ladder_dest = self.board[dest[0]][dest[1]]
                self.unavailable.append(base)
                self.unavailable.append(dest)
                counter += 1

    def _set_random_snakes(self, total):
        counter, min_rows_skipped = 0, 2
        all_indices = self._get_tile_indices() 
        tile_indices = []
        for row in all_indices:
            filtered_row = []
            for ind in row:
                if ind not in self.unavailable:
                    filtered_row.append(ind)
            tile_indices.append(filtered_row)

        while counter < total:
            from_row = random.choice(range(min_rows_skipped + 1, self.dim[0]))
            from_ind = random.choice(tile_indices[from_row])
            to_ind = random.choice(random.choice(tile_indices[:from_row - min_rows_skipped]))
            if from_ind not in self.unavailable and to_ind not in self.unavailable:
                self.board[from_ind[0]][from_ind[1]].snake_end_pos = self.board[to_ind[0]][to_ind[1]]
                self.unavailable.append(from_ind)
                self.unavailable.append(to_ind)
                counter += 1

    def draw(self, cvs):
        for row in self.board:
            for tile in row:
                tile.draw(cvs)

        # drawing snakes over numbers
        for row in self.board:
            for tile in row:
                if tile.snake_end_pos:
                    self._draw_snake(tile, tile.snake_end_pos, cvs)

        # drawing ladders over snakes
        for row in self.board:
            for tile in row:
                if tile.ladder_dest:
                    self._draw_ladder(tile, tile.ladder_dest, cvs)
                

rootWin = Tk()
rootWin.title("Snakes and Ladders")

WIDTH = 700
HEIGHT = 600

fg_color = "black"
bg_color = "white"

canvas = Canvas(rootWin, bg = bg_color, height = HEIGHT, width = WIDTH)
canvas.pack(side = LEFT)

SnakesAndLaddersBoard = SnakesAndLaddersBoard(pos = (50, 20), tile_size = 55, dim =(10, 10))
SnakesAndLaddersBoard.draw(canvas)

rootWin.mainloop()



