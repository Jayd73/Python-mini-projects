import pygame, sys
from pygame.math import Vector2
from pygame.font import Font
from pygame import Rect, Surface
from queue import PriorityQueue
import random as rd
import json
from maze_generation import Maze

# rd.seed(7)

def get_hamiltonian_cycle(grnd_dim):
    # generate a maze with half the size for each dim
    # expand the maze by 2 to fill the actual ground
    maze_dim = (grnd_dim[0] // 2, grnd_dim[1] // 2)
    maze = Maze(screen = Surface((0, 0)), top_left = (0, 0), room_size = 1, dim = maze_dim)
    maze.create_maze()
    maze = maze.get_expanded((2, 2))
    heading = Snake.RIGHT
    start_room = Vector2(0, 0)
    next_room = start_room
    hamil_cycle_inds = []
    while True:
        curr_room = next_room
        pov_lft_direc = heading.rotate(90)
        pov_rt_direc = heading.rotate(-90)
        for direc in [pov_lft_direc, heading, pov_rt_direc]:
            room = curr_room + direc
            wall_inds = maze.get_common_wall_inds(curr_room, room)
            if maze.maze_grid[tuple(curr_room)][wall_inds[0]] == 0:
                next_room = room
                heading = direc
                hamil_cycle_inds.append(curr_room)
                break
        if next_room == start_room:
            break
    return hamil_cycle_inds


class Food:
    def __init__(self, pos, box_size, graphic):
        self.pos = Vector2(*pos)
        self.box_size = box_size
        self.graphic = graphic
    
    def draw(self, grnd_surf):
        x, y = self.pos.y * self.box_size, self.pos.x * self.box_size
        food_rect = Rect(x, y, self.box_size, self.box_size)
        grnd_surf.blit(self.graphic, food_rect)

class Snake:
    LEFT = Vector2(0, -1)
    RIGHT = Vector2(0, 1)
    DOWN = Vector2(1, 0)
    UP = Vector2(-1, 0)

    def __init__(self, pos, box_size, graphics, direc = None, start_body_len = 2):
        self.direc = direc if direc else Snake.RIGHT
        self.box_size = box_size
        self.food_items_eaten = 0
        self.is_dead = False
        self.start_body_len = start_body_len
        self.graphics = graphics
        self.graphics_orient_ord = [Snake.UP, Snake.RIGHT, Snake.DOWN, Snake.LEFT]
        self.build_body(pos)
    
    def build_body(self, pos):
        self.body = [Vector2(*pos)]
        self.new_part_pos = self.get_trailing_pos()
        # should have a min body len of 2
        for i in range(max(self.start_body_len - 1, 1)): self.add_body_part()

    def get_trailing_pos(self):
        return self.body[-1] -1 * self.direc
    
    def set_direc(self, direc):
        # should only do this when the game is being updated. Shouldn't call this every frame
        if direc != -1 * self.direc:
            self.direc = direc
    
    def add_body_part(self):
        self.body.append(self.new_part_pos)
        self.new_part_pos = self.get_trailing_pos() 

    def get_next_pos(self):
        return self.body[0] + self.direc

    def move(self):
        self.new_part_pos = self.body.pop()
        self.body.insert(0, self.get_next_pos())
    
    def respawn(self):
        self.build_body(self.body[0])
        self.food_items_eaten = 0

    def draw(self, grnd_surf):
        for idx, part_pos in enumerate(self.body):
            x, y = part_pos.y * self.box_size, part_pos.x * self.box_size
            part_rect = Rect(x, y, self.box_size, self.box_size)
            if idx == 0:
                orient_idx = self.graphics_orient_ord.index((self.body[0] - self.body[1]))
                grnd_surf.blit(self.graphics["head" if not self.is_dead else "dead_head"][orient_idx], part_rect)
            elif idx == len(self.body) - 1:
                orient_idx = self.graphics_orient_ord.index((self.body[-1] - self.body[-2]))
                grnd_surf.blit(self.graphics["tail"][orient_idx], part_rect)
            else:
                prev_direc = (self.body[idx - 1] - part_pos)
                next_direc = (self.body[idx + 1] - part_pos)
                if prev_direc.x == next_direc.x == 0 or prev_direc.y == next_direc.y == 0:
                    orient_idx = self.graphics_orient_ord.index(prev_direc)
                    grnd_surf.blit(self.graphics["body"][orient_idx % 2], part_rect)
                else:
                    idx1 = self.graphics_orient_ord.index(prev_direc)
                    idx2 = self.graphics_orient_ord.index(next_direc)
                    orient_idx = min(idx1, idx2) + abs(idx1 - idx2) // 3 * 3
                    grnd_surf.blit(self.graphics["turn"][orient_idx], part_rect)
  

class SnakeGame:
    PLAY = 0
    AI = 1
    MULTISNAKE = 2

    def __init__(self, screen, dim, cell_size, assets, score_board_ht = 50, game_mode = None, start_len = 3, tot_snakes = 5, max_food_items = 4):
        self.screen = screen
        self.cell_size = cell_size
        self.assets = assets
        self.start_len = max(2, start_len)
        self.dim = tuple([max(dim_val, self.start_len + 2) for dim_val in dim])
        self.max_food_items = max_food_items
        self.grnd_surf = Surface(self.get_ground_wdth_ht())
        self.score_board_surf = Surface((self.get_ground_wdth_ht()[0], score_board_ht))
        self.cols = [(170, 215, 81), (162, 209, 73)]
        self.score_board_bg_color = (60, 107, 5)
        self.font_size = 24
        self.font_col = (255, 255, 255)
        self.food = []
        self.snakes = []
        self.obstacles = set()
        self.is_game_over = False
        self.start_idx = (1, int(start_len))
        self.init_graphics_and_font()
        self.add_boundary()
        self.set_up_for_play_mode(game_mode if game_mode else SnakeGame.PLAY, tot_snakes)
        
    def init_graphics_and_font(self):
        self.game_font = Font(self.assets["font"], self.font_size)
        self.food_graphic = pygame.image.load(self.assets["food"]["apple"]).convert_alpha()
        self.obstacle_graphic = pygame.image.load(self.assets["obstacle"]).convert_alpha()
        self.food_graphic = pygame.transform.scale(self.food_graphic, (self.cell_size,) * 2)
        self.obstacle_graphic = pygame.transform.scale(self.obstacle_graphic, (self.cell_size,) * 2)
        parts_name_map = {"head_up": "head",
                          "head_up_dead": "dead_head", 
                          "body_vert": "body", 
                          "turn_top_rt": "turn", 
                          "tail_up": "tail"}
        for snake_name, body_parts in self.assets["snakes"].items():
            updated_body_parts = {}
            for part_name, file_path in body_parts.items():
                part = pygame.image.load(file_path).convert_alpha()
                part = pygame.transform.scale(part, (self.cell_size,) * 2)
                rotated_imgs = [part]
                for i in range(1, 4):
                    rotated_imgs.append(pygame.transform.rotate(part, -90 * i))
                updated_body_parts[parts_name_map[part_name]] = rotated_imgs
            del updated_body_parts["body"][-2:]
            self.assets["snakes"][snake_name] = updated_body_parts
    
    def set_up_for_play_mode(self, game_mode, tot_snakes = 1):
        self.game_mode = game_mode
        self.set_next_direc_for = lambda snake: None
        if self.game_mode == SnakeGame.MULTISNAKE:
            self.set_next_direc_for = self.set_direc_when_multisnake_for
            horiz_pos, vert_pos = self.get_possible_snake_pos(self.start_len)
            snake_pos_and_direc = {}
            for h_pos in horiz_pos: snake_pos_and_direc[h_pos] = rd.choice([Snake.RIGHT, Snake.LEFT])
            for v_pos in vert_pos: snake_pos_and_direc[v_pos] = rd.choice([Snake.UP, Snake.DOWN])
            tot_snakes = min(len(snake_pos_and_direc), tot_snakes)
            chosen_pos = rd.sample(snake_pos_and_direc.keys(), tot_snakes)
            for pos in chosen_pos:
                direc = snake_pos_and_direc[pos]
                if direc == Snake.RIGHT: pos = (pos[0], pos[1] + self.start_len - 1)
                if direc == Snake.DOWN: pos = (pos[0] + self.start_len - 1, pos[1])
                self.add_snake(pos, self.start_len, direc = direc)
            tot_food_spots = (self.dim[0] - 2) * (self.dim[1] - 2) - self.start_len * len(self.snakes)
            tot_food_items = min(tot_food_spots, self.max_food_items)
            for _ in range(tot_food_items): self.add_food_item_at_rand()
        else:
            if self.game_mode == SnakeGame.AI:
                self.set_next_direc_for = self.set_next_hamil_direc_for
                # both dim must be even bcoz the dim are further divided by 2 to generate a smaller maze. 
                self.dim = (self.dim[0] - self.dim[0] % 2, self.dim[1] - self.dim[1] % 2)
                self.hamil_cycle_inds = get_hamiltonian_cycle((self.dim[0] - 2, self.dim[1] - 2))
                self.hamil_cycle_inds = [Vector2(i + 1, j + 1) for i, j in self.hamil_cycle_inds]
                self.curr_cycle_idx = self.hamil_cycle_inds.index(Vector2(self.start_idx))
                self.add_boundary()
            self.add_snake(self.start_idx, self.start_len)
            self.add_food_item_at_rand()

    def add_boundary(self):
        for i in range(self.dim[0]): self.obstacles.update([(i, 0), (i, self.dim[1] - 1)])
        for j in range(self.dim[1]): self.obstacles.update([(0, j), (self.dim[0] - 1, j)])
    
    def add_obstacle_at(self, pos):
        x, y = pos
        if self.grnd_surf.get_rect(topleft=(0, 0)).collidepoint(x, y):
            idx = (y // self.cell_size, x // self.cell_size)
            if self.is_empty(idx): self.obstacles.add(idx)

    def add_food_item_at_rand(self):
        available_spots = []
        for spot in [(i, j) for i in range(self.dim[0]) for j in range(self.dim[1])]:
            if self.is_empty(spot):
                available_spots.append(spot)
        if available_spots:
            food = Food(rd.choice(available_spots), self.cell_size, graphic = self.food_graphic)
            self.food.append(food)
        else:
            self.is_game_over = True
    
    def is_empty(self, idx, include_food_spots = True):
        for obs_idx in self.obstacles:
            if obs_idx == idx:
                return False
        for snake in self.snakes:
            for part_pos in snake.body:
                if tuple(part_pos) == idx:
                    return False
        if include_food_spots:        
            for food_item in self.food:
                if tuple(food_item.pos) == idx:
                    return False
        return True
    
    def get_possible_snake_pos(self, snake_len):
        horiz_pos, vertical_pos = [], []
        rows, colms = self.dim[0] - 2, self.dim[1] - 2
        row_stop, colm_stop = rows - snake_len + 1, colms - snake_len + 1
        for i in range(snake_len * 2, colms, snake_len * 2):
            for r, c in zip(range(0, rows), range(i, colm_stop)):
                horiz_pos.append((r + 1, c + 1))
        for j in range(snake_len * 2 - 1, colms, snake_len * 2):
            for r, c in zip(range(0, row_stop), range(j, colms)):
                vertical_pos.append((r + 1, c + 1))
        for i in range(0, rows, snake_len * 2):
            for r, c in zip(range(i, rows), range(0, colm_stop)):
                horiz_pos.append((r + 1, c + 1))
        for j in range(1, rows, snake_len * 2):
            for r, c in zip(range(j, row_stop), range(0, colms)):
                vertical_pos.append((r + 1, c + 1))
        return (horiz_pos, vertical_pos)
            
    def add_snake(self, idx, start_len, direc = None):
        snake_names = list(self.assets["snakes"].keys())
        name = snake_names[len(self.snakes) % len(snake_names)]
        snake_graphics = self.assets["snakes"][name]
        snake = Snake(idx,
                      self.cell_size, 
                      direc = direc, 
                      graphics = snake_graphics, 
                      start_body_len = start_len)
        self.snakes.append(snake)

    def get_ground_wdth_ht(self):
        wdth = self.cell_size * self.dim[1]
        ht = self.cell_size * self.dim[0]
        return (wdth, ht)
    
    def set_play_snake_direc(self, direc):
        if self.game_mode == SnakeGame.PLAY:
            self.snakes[0].set_direc(direc)
    
    def get_surr_empty_spots(self, curr_idx):
        surr_inds = []
        for i in [0, 1]:
            for j in [1, -1]:
                idx = curr_idx[0] + j * i, curr_idx[1] + j * (1 - i)
                if self.is_empty(idx, include_food_spots = False):
                    surr_inds.append(idx) 
        return surr_inds
    
    def set_next_hamil_direc_for(self, snake):
        self.curr_cycle_idx += 1
        next_cell_idx = self.hamil_cycle_inds[(self.curr_cycle_idx) % len(self.hamil_cycle_inds)]
        curr_cell_idx = snake.body[0]   # snake head
        food_cell_idx = self.food[0].pos
        food_cell_1D_idx = self.hamil_cycle_inds.index(food_cell_idx)
        short_path_cell_1D_idx, chosen_cell_idx = -1, None
        # check for shortcuts if snake's body len is less than 50% of longest possible len
        if len(snake.body) < ((self.dim[0] - 2) * (self.dim[1] - 2)) // 2:
            # uses greedy search to find next cell in the shortest path. Refer notes for details.
            for surr_cell_idx in self.get_surr_empty_spots(curr_cell_idx):
                surr_cell_1D_idx = self.hamil_cycle_inds.index(surr_cell_idx)
                if surr_cell_1D_idx <= food_cell_1D_idx and surr_cell_1D_idx > short_path_cell_1D_idx:
                    short_path_cell_1D_idx = surr_cell_1D_idx
                    chosen_cell_idx = surr_cell_idx
            if chosen_cell_idx:
                head_cell_1D_idx = self.hamil_cycle_inds.index(curr_cell_idx)
                tail_cell_1D_idx = self.hamil_cycle_inds.index(snake.body[-1])
                diff = head_cell_1D_idx - tail_cell_1D_idx
                polarity = diff / abs(diff)
                bounds = [(head_cell_1D_idx + 1, tail_cell_1D_idx), (tail_cell_1D_idx, head_cell_1D_idx + 1)]
                bound_idx = int((1 + polarity) // 2)
                if bound_idx - (short_path_cell_1D_idx in range(*bounds[bound_idx])):
                    next_cell_idx = chosen_cell_idx
        self.curr_cycle_idx = self.hamil_cycle_inds.index(next_cell_idx)
        snake.set_direc(next_cell_idx - curr_cell_idx)

    def get_manhattan_dist(self, pos_1, pos_2):
        return abs(pos_1[0] - pos_2[0]) + abs(pos_1[1] - pos_2[1])
    
    def set_direc_when_multisnake_for(self, snake):
        head_pos = snake.body[0]
        empty_spots = self.get_surr_empty_spots(head_pos)
        if not empty_spots: return
        # increase the prob for moving straight
        frwrd_pos = snake.get_next_pos()
        prob = [10] * len(empty_spots)
        if frwrd_pos in empty_spots: prob[empty_spots.index(frwrd_pos)] = 200
        next_pos = rd.choices(empty_spots, weights = prob, k = 1)[0]
        field_of_vision = 4 # num of tiles a snake can see in all directions
        priority_q = PriorityQueue()
        for food_item in self.food:
            dist = self.get_manhattan_dist(head_pos, food_item.pos)
            if dist <= field_of_vision:
                priority_q.put((dist, tuple(food_item.pos)))
        if not priority_q.empty():
            food_pos = priority_q.get()[1]
            dist_spot_q = PriorityQueue()
            for pos in empty_spots:
                dist = self.get_manhattan_dist(pos, food_pos)
                dist_spot_q.put((dist, pos))
            next_pos = dist_spot_q.get()[1]
        snake.set_direc(next_pos - head_pos)
    
    def update(self):
        if self.is_game_over: return
        all_snakes_dead = True
        for snake in self.snakes:
            self.set_next_direc_for(snake)
            did_collide = self.check_collision(snake)
            if not did_collide:
                snake.move()
                self.handle_food_grab(snake)
            all_snakes_dead = all_snakes_dead and did_collide
        if all_snakes_dead:
            for snake in self.snakes:
                if self.game_mode == SnakeGame.MULTISNAKE: snake.respawn()
                else:
                    snake.is_dead = True
                    self.is_game_over = True
        self.draw()

    def check_collision(self, snake):
        next_pos = snake.get_next_pos()
        for obs_pos in self.obstacles:
            if next_pos == obs_pos: return True
        snake_parts = [part_pos for snake in self.snakes for part_pos in snake.body]
        for part_pos in snake_parts:
            if next_pos == part_pos: return True
        return False
    
    def handle_food_grab(self, snake):
        head_pos = snake.body[0]
        for food in self.food:
            if head_pos == food.pos:
                snake.add_body_part()
                snake.food_items_eaten += 1
                self.food.remove(food)
                self.add_food_item_at_rand()

    def draw_score_board(self):
        self.score_board_surf.fill(self.score_board_bg_color)
        y_offset = self.score_board_surf.get_rect().height
        x_offset = 30
        food_graphic_x, food_graphic_y = x_offset, y_offset // 2
        food_rect = self.food_graphic.get_rect(center = (food_graphic_x, food_graphic_y))
        score_multiplier = 10
        score = (len(self.snakes[0].body) - self.start_len) * score_multiplier
        score_txt_surf = self.game_font.render(str(score), True, self.font_col) # antialiasing = True
        score_rect = score_txt_surf.get_rect(midleft = (food_rect.right, food_rect.centery))
        self.score_board_surf.blit(self.food_graphic, food_rect)
        self.score_board_surf.blit(score_txt_surf, score_rect)
        if self.is_game_over:
            go_msg = "Game Over"
            go_msg_surf = self.game_font.render(go_msg, True, self.font_col) # antialiasing = True
            go_msg_x = self.score_board_surf.get_rect().width - x_offset
            go_msg_rect = go_msg_surf.get_rect(midright = (go_msg_x, food_rect.centery))
            self.score_board_surf.blit(go_msg_surf, go_msg_rect)
        self.screen.blit(self.score_board_surf, (0, 0))

    def draw(self):
        self.grnd_surf.fill((0, 0, 0))
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                x = j * self.cell_size
                y = i * self.cell_size
                pygame.draw.rect(self.grnd_surf, self.cols[(i + j) % 2], Rect(x, y, self.cell_size, self.cell_size))
        for obs_x, obs_y in self.obstacles:
            x, y = obs_y * self.cell_size, obs_x * self.cell_size
            self.grnd_surf.blit(self.obstacle_graphic, Rect(x, y, self.cell_size, self.cell_size))
        for food in self.food:
            food.draw(self.grnd_surf)
        for snake in self.snakes:
            snake.draw(self.grnd_surf)
        y_offset = 0
        if self.game_mode != SnakeGame.MULTISNAKE:
            y_offset = self.score_board_surf.get_rect().height
            self.draw_score_board()
        self.screen.blit(self.grnd_surf, (0, y_offset))
    

def main():
    pygame.init()
    FPS = 60
    cell_size = 50
    rows, colms = 10, 16  # both must be even for AI mode
    score_board_ht = 60
    min_snake_len = 4
    tot_snakes = 5
    game_mode = SnakeGame.MULTISNAKE
    update_times = {SnakeGame.PLAY: 100, SnakeGame.AI: 10, SnakeGame.MULTISNAKE: 40}

    WIDTH, HEIGHT = cell_size * colms, cell_size * rows
    HEIGHT = HEIGHT + score_board_ht if game_mode != SnakeGame.MULTISNAKE else HEIGHT
    
    game_assets = json.load(open("D:\Jayesh\Python\Python Projects\Snake Game\img_paths.json"))

    main_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")

    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, update_times[game_mode])

    clock = pygame.time.Clock()

    game = SnakeGame(main_screen, dim = (rows, colms), cell_size = cell_size, assets = game_assets, game_mode = game_mode, score_board_ht = score_board_ht, start_len = min_snake_len, tot_snakes = tot_snakes)
    
    game.draw()
    curr_direc = Snake.RIGHT
    is_adding_obs = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    curr_direc = Snake.UP
                elif event.key == pygame.K_DOWN:
                    curr_direc = Snake.DOWN
                elif event.key == pygame.K_LEFT:
                    curr_direc =  Snake.LEFT
                elif event.key == pygame.K_RIGHT:
                    curr_direc = Snake.RIGHT

            if event.type == pygame.MOUSEBUTTONDOWN and game_mode == SnakeGame.MULTISNAKE:
                is_adding_obs = True
            elif is_adding_obs and event.type == pygame.MOUSEMOTION:
                game.add_obstacle_at(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONUP:
                is_adding_obs = False

            if event.type == SCREEN_UPDATE:
                game.set_play_snake_direc(curr_direc)
                game.update()

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
