import tkinter as tk
from tkinter import messagebox
from tkinter import *
import random
from tkinter import filedialog
from tkinter import simpledialog
from PIL import ImageTk, Image

__author__ = "{{Mason}} ({{45666564}})"
__email__ = "xxxxxxx"
__date__ = "25/10/2020"


GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

DIRECTIONS = {
    "w": (-1, 0),
    "s": (1, 0),
    "d": (0, 1),
    "a": (0, -1)
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "
INVALID = "That's invalid."

WIN_TEXT = "You have won the game with your strength and honour!"

LOSE_TEST = "You have lost all your strength and honour."
LOSE_TEXT = "You have lost all your strength and honour."

TASK_ONE = 1
TASK_TWO = 2
MASTERS = 3

def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.
    
    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the 
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    return dungeon_layout

class Entity:
    """ """

    _id = "Entity"

    def __init__(self):
        """
        Something the player can interact with
        """
        self._collidable = True

    def get_id(self):
        """ """
        return self._id

    def set_collide(self, collidable):
        """ """
        self._collidable = collidable

    def can_collide(self):
        """ """
        return self._collidable

    def __str__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        return str(self)


class Wall(Entity):
    """ """

    _id = WALL
    
    def __init__(self):
        """ """
        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """ """
    def on_hit(self, game):
        """ """
        raise NotImplementedError


class Key(Item):
    """ """

    _id = KEY

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())


class MoveIncrease(Item):
    """ """

    _id = MOVE_INCREASE

    def __init__(self, moves=5):
        """ """
        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """ """
    _id = DOOR

    def on_hit(self, game):
        """ """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.get_game_information().pop(player.get_position())
                game.set_win(True)
                return

class Player(Entity):
    """ """

    _id = PLAYER

    def __init__(self, move_count):
        """ """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self, position):
        """ """
        self._position = position

    def get_position(self):
        """ """
        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """
        self._move_count += number

    def moves_remaining(self):
        """ """
        return self._move_count

    def set_move_remaining(self, new_move_num):

        self._move_count = new_move_num

    def add_item(self, item):
        """Adds item (Item) to inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """ """
        return self._inventory

class GameLogic:
    """ """
    def __init__(self, dungeon_name="game2.txt"):
        """ """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False

    def get_positions(self, entity):
        """ """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """ """
        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)[0]
        door_position = self.get_positions(DOOR)[0]
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)
        
        self._player.set_position(player_pos)

        information = {
            key_position: Key(),
            door_position: Door(),
        }

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """ """
        return self._player

    def get_entity(self, position):
        """ """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """ """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)
    
    def set_game_information(self, gameinformation):
        
        self._game_information = gameinformation
        return self._game_information

    def get_game_information(self):
        """ """
        return self._game_information

    def get_dungeon_size(self):
        """ """
        return self._dungeon_size

    def move_player(self, direction):
        """ """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True
        
        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """ """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """ """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """ """
        self._win = win

    def won(self):
        """ """
        return self._win

class AbstractGrid(tk.Canvas):
    """
    View of the game map and game pad.
    
    """

    def __init__(self, master, rows, cols, width, height, *args, **kwargs):
        """
        Construct the AbstractGrid

        Parameters:
            master (tk.Widget): Widget within which the board is placed.
            rows (int): the number of rows.
            cols (int): the number of cols.
            width (int): the width of the board.
            height (int): the height of the board.
            
        """
        super().__init__(master, width = width, height = height, **kwargs)
        self._master = master
        
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height
        self._center_pixel = ()
        self._cell_height = self._height // self._rows
        self._cell_width = self._width // self._cols
        
    def get_bbox(self, position):
        """
        Returns the bounding box for the (row, col) position.

        Parameters:
            position (tuple<int, int>): The row, column position of a cell.

        """
        position_y, position_x = position

        corner1 = (position_x * self._cell_width, position_y * self._cell_height)
        corner2 = ((position_x + 1) * self._cell_width, (position_y + 1) * self._cell_height)

        return corner1, corner2

    def pixel_to_position(self, pixel):
        """
        Converts the x, y pixel position (in graphics units) to a (row, col) position.

        Parameters:
            pixel (tuple<int, int>): The position in the graphics units.
            
        """
        pixel_x, pixel_y = pixel
        x = pixel_x // self._cell_width
        y = pixel_y // self._cell_height
        return y, x

    def get_position_center(self, position):
        """
        Gets the graphics coordinates for the center of the cell
        at the given (row, col) position.

        Parameters:
            position (tuple<int, int>): The row, column position of a cell.
            
        """
        y, x = position
        self._center_pixel = (self._cell_width * x + self._cell_width / 2,
                              self._cell_height * y + self._cell_height / 2)
        return self._center_pixel

    def annotate_position(self, position, text):
        """
        Annotates the cell at the given (row, col) position with the
        provided text.

        Parameters:
            position (tuple<int, int>): The row, column position of a cell.
            text (str): A string represents the entity.
            
        """
        self._text = text
        self.create_text(self.get_position_center(position), text = f"{self._text}")
        
class DungeonMap(AbstractGrid):
    """
    View of the game map.

    """
    def __init__(self, master, size, width=600, **kwargs):
        """
        Construct the map view.

        Parameters:
            master (tk.Widget): Widget within which the board is placed.
            size (int): The size of dungeon map.
            width (int): The width of the map.
            
        """
        super().__init__(master, size, size, width=width, height=width, **kwargs) 
        self._master = master
        self._size = size
        
    def draw_grid(self, dungeon, player_position):
        """
        Draws the dungeon on the DungeonMap based on dungeon,
        and draws the player at the specified (row, col) position.

        Parameters:
            dungeon(dict<tuple<int, int>: Entity>): The dictionary containing the position and the
                corresponding Entity, as the keys and values, for the game.
            player_position(tuple) : The position of player.
            
        """
        self.delete(tk.ALL)
        
        for row in range(self._size):
            for col in range(self._size):
                i = (row, col)
                if i not in dungeon.keys():
                    continue
                
                elif dungeon[i].get_id() == WALL:
                    self.create_rectangle(self.get_bbox(i), fill = "dark grey")
                            
                elif dungeon[i].get_id() == KEY:
                    self.create_rectangle(self.get_bbox(i), fill = "yellow")
                    self.annotate_position(i, "Trash")
                    
                elif dungeon[i].get_id() == MOVE_INCREASE:
                    self.create_rectangle(self.get_bbox(i), fill = "orange")
                    self.annotate_position(i, "Banana")
                    
                elif dungeon[i].get_id() == DOOR:
                    self.create_rectangle(self.get_bbox(i), fill = "red")
                    self.annotate_position(i, "Nest")
                  
        self.create_rectangle(self.get_bbox(player_position), fill = "medium spring green")
        self.annotate_position(player_position, "Ibis")

class AdvancedDungeonMap(AbstractGrid):
    """
    View of the game map with images.

    """
    def __init__(self, master, size, width = 600):
        """
        Construct the map view.

        Parameters:
            master (tk.Widget): Widget within which the board is placed.
            size (int): The size of dungeon map.
            width (int): The width of the map.
            
        """
        super().__init__(master, size, size, width = width, height = width)
        self._size = size
        self._images = {}
        paths = ['empty', 'player', 'wall', 'key', 'moveIncrease', 'door']
        for path in paths:
            self.save_image(path)

    def save_image(self, path):
        """
        Save the image.

        Parameters:
            path (str): The string of the name of each image.
        """
        image = Image.open(f"images/{path}.png").resize((self._width // self._size,
                                                         self._width // self._size))
        photo = ImageTk.PhotoImage(image)
        self._images[path] = photo
        
    def draw_grid(self, dungeon, player_position):
        """
        Use images to replace original content.

        Parameters:
            dungeon(dict<tuple<int, int>: Entity>): The dictionary containing the position and the
                corresponding Entity, as the keys and values, for the game.
            player_position(tuple) : The position of player.

        """
        self.delete(tk.ALL)
        
        for row in range(self._size):
            for col in range(self._size):
                i = (row, col)
                
                if i not in dungeon.keys():
                    self.create_image(self.get_position_center(i), image = self._images['empty'])
                
                elif dungeon[i].get_id() == WALL:
                    self.create_image(self.get_position_center(i), image = self._images['wall'])
                            
                elif dungeon[i].get_id() == KEY:
                    self.create_image(self.get_position_center(i), image = self._images['empty'])
                    self.create_image(self.get_position_center(i), image = self._images['key'])
                    
                elif dungeon[i].get_id() == MOVE_INCREASE:
                    self.create_image(self.get_position_center(i), image = self._images['empty'])
                    self.create_image(self.get_position_center(i), image = self._images['moveIncrease'])
                    
                elif dungeon[i].get_id() == DOOR:
                    self.create_image(self.get_position_center(i), image = self._images['empty'])
                    self.create_image(self.get_position_center(i), image = self._images['door'])       

        self.create_image(self.get_position_center(player_position), image = self._images['player'])
        
class KeyPad(AbstractGrid):
    """
    View of the keypad of game.
    
    """
    def __init__(self, master, width = 200, height = 100, **kwargs):
        """
        Construct the key pad view.

        Parameters:
            master (tk.Widget): Widget within which the board is placed.
            width (int): The width of the pad.
            height (int): The height of the pad.
            
        """
        super().__init__(master, rows = 2, cols = 3, width = width, height = height, **kwargs)
        self._master = master
        
        self.create_rectangle(self.get_bbox((0,1)), fill = "dark grey")
        self.create_rectangle(self.get_bbox((1,0)), fill = "dark grey")
        self.create_rectangle(self.get_bbox((1,1)), fill = "dark grey")
        self.create_rectangle(self.get_bbox((1,2)), fill = "dark grey")
        
        self.annotate_position((0,1), "N")
        self.annotate_position((1,0), "W")
        self.annotate_position((1,1), "S")
        self.annotate_position((1,2), "E")
        
    def pixel_to_direction(self, pixel):
        """
        Converts the x, y pixel position to the direction of the arrow depicted
        at that position.

        Parameters:
            pixel (tuple<int, int>): The click position in the graphics units.
        """

        click_position = self.pixel_to_position(pixel)
        
        if click_position == (0, 1):
            return 'w'
        elif click_position == (1, 0):
            return 'a'
        elif click_position == (1, 1):
            return 's'
        elif click_position == (1, 2):
            return 'd'
       
class GameApp:
    """
    Game application that manages communication among the gamelogic, statusbar, filemenu, view class and each model class.

    """
    def __init__(self, master, task = MASTERS, dungeon_name="game2.txt"):
        """
        Construct of the GameApp class.

        Parameters:
            master (tk.Widget): Widget within which the board is placed.
            task (int): choose one model of the game.
            dungeon_name (str): The name of the level.
            
        """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        
        self._game = GameLogic()
        
        self._master = master
        self._master.title("Key Cave Adventure Game")
        
        self._label = tk.Label(self._master, text = "Key Cave Adventure Game", fg = "black",
                               bg = "medium spring green")
        self._label.pack(side = tk.TOP, fill = tk.X)

        # Set the map and pad in the same Frame.
        self._master_main = tk.Frame(master)
        self._master_main.pack(side = tk.TOP)

        self._moves_left = self._game.get_player().moves_remaining()
        self._lives_remaining = 3

        self._task = task
        
        if self._task == TASK_ONE:
            
            self._view = DungeonMap(self._master_main, self._dungeon_size, width = 600, bg = "light gray")
            
        elif self._task == TASK_TWO:
            
            self._file_menu = FileMenu(self._master, self)
            self._view = AdvancedDungeonMap(self._master_main, self._dungeon_size, width = 600)
            self._status_bar = StatusBar(self._master, self._moves_left, self)
            self._status_bar.pack(side = tk.BOTTOM)
            
        elif self._task == MASTERS:
            
            self._file_menu = FileMenu(self._master, self)
            self._view = AdvancedDungeonMap(self._master_main, self._dungeon_size, width = 600)
            self._status_bar = LivesRemaining(self._master,
                                              self._moves_left,
                                              self
                                              )
            self._status_bar.pack(side = tk.BOTTOM)

        self._view.pack(side = tk.LEFT)
        self._view.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())
        self._pad_view = KeyPad(self._master_main, width = 200, height = 100)
        self._pad_view.pack(side = tk.LEFT)

        self._master.bind("<KeyPress>", self.key_press)
        self._master.bind("<Button-1>", self.press_pad)

        self._filename = None
        self._time = None
        self._scores_file = None

        self._player_1 = None
        self._player_2 = None
        self._player_3 = None
      
    def key_press(self, e):
        """
        The key on the keyboard is pressed.
        """

        if self._game.check_game_over():
            self.lost_the_game()

        elif e.char not in DIRECTIONS:
            return None
        
        else:
            
            if self._task == MASTERS:
                # Store each game step.
                game_step = self._status_bar.save_step(self._game.get_player().moves_remaining(),
                                                       self._game.get_player().get_position(),
                                                       self._game.get_game_information()
                                                       )
                self._status_bar.store(game_step)
            self._game.get_player().change_move_count(-1)
            
            if self._task != TASK_ONE:
                self._status_bar.update_move_remaining(self._game.get_player().moves_remaining())
            
            entity = self._game.get_entity_in_direction(e.char)
            
            if not self._game.collision_check(e.char):
                
                if entity is not None:
                    self._game.move_player(e.char)
                    entity.on_hit(self._game)
                    
                    if self._task != TASK_ONE:
                        self._status_bar.update_move_remaining(self._game.get_player().moves_remaining())
                    self._view.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())
                    
                    if self._game.won():
                        
                        if self._task == MASTERS:
                            self.win_the_game_master()
                        else: 
                            self.win_the_game()
                else:
                    self._game.move_player(e.char)
                    self._view.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())    
            else:
                self.invalid()
            
    def press_pad(self, e):
        """
        Key Pad is pressed by left mouse button.

        """
        pad_direction = self._pad_view.pixel_to_direction((e.x, e.y))

        if self._game.check_game_over():
                self.lost_the_game()

        elif pad_direction not in DIRECTIONS:
            return None

        else:
            if self._task == MASTERS:
                # Store each game step.
                game_step = self._status_bar.save_step(self._game.get_player().moves_remaining(),
                                                       self._game.get_player().get_position(),
                                                       self._game.get_game_information()
                                                       )
                self._status_bar.store(game_step)
            self._game.get_player().change_move_count(-1)
            
            if self._task != TASK_ONE:
                self._status_bar.update_move_remaining(self._game.get_player().moves_remaining())
            
            entity = self._game.get_entity_in_direction(pad_direction)
            
            if not self._game.collision_check(pad_direction):
                
                if entity is not None:
                    self._game.move_player(pad_direction)
                    entity.on_hit(self._game)
                    
                    if self._task != TASK_ONE:
                        self._status_bar.update_move_remaining(self._game.get_player().moves_remaining())
                    self._view.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())
                    
                    if self._game.won():
                        
                        if self._task == MASTERS:
                            self.win_the_game_master()
                        else:
                            self.win_the_game()
                else:
                    self._game.move_player(pad_direction)
                    self._view.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())     
            else:
                self.invalid()

    def quite(self):
        """
        Quit the current game.
        
        """
        quit_box = messagebox.askquestion(title = "Quit ?", message = "Are you sure you would like to quit?",
                                           icon = 'warning')
        if quit_box == 'no':
            self.new_game()
        else:
            self._master.destroy()

    def invalid(self):
        """
        Prompts the player action invalid.
        
        """
        messagebox.showinfo(title = "Sorry", message = INVALID, icon = 'warning')

    def lost_the_game(self):
        """
        When player lost a game.

        """
        if self._task == TASK_ONE:
            messagebox.showinfo(title = "You lost the game", message = LOSE_TEXT)
            
        elif self._task == TASK_TWO or self._task == MASTERS:
            quit_box = messagebox.askquestion(title = "You lost the game", message = "Would you like to play again?",
                                               icon = 'warning')
            if quit_box == 'yes':
                self._master.update_idletasks()
                self.new_game()
                
            else:
                self._master.destroy()

    def win_the_game(self):
        """
        When player wins a game.

        """
        if self._task == TASK_TWO:
            score = self._status_bar._seconds
            win_box1 = messagebox.askquestion(title = "You Won!", message = "You have finished the level with a score of " + str(score) + '\n'
                                              + "Would you like to play again?")
            if win_box1 == 'yes':
                self._master.update_idletasks()
                self.new_game()
            else:
                self._master.destroy()

        elif self._task == TASK_ONE:
            win_box2 = messagebox.askquestion(title = "You Won!", message = "Would you like to play again?")
            if win_box2 == 'yes':
                self.new_game()
            else:
                self._master.destroy()
                
    def win_the_game_master(self):
        """
        When player wins a game, and the model of game is MASTERS.

        """
        self._status_bar.stop_time()
        
        playing_time = self._status_bar.save_time()
        player_name = simpledialog.askstring(title = "You Win!",
                                             prompt = "You won in " + playing_time[0:2] + " and "  + playing_time[3:6] + "! Enter your name: "
                                             )
        if player_name is None or player_name == '':
            player_name = "anonymity"
        try:
            top3_player = self.read_file()
            file_open = open("scores_file.txt", 'w')
            top3_player.append(player_name + ": " + playing_time + "\n")
            if len(top3_player) == 1:
                
                file_open.write(top3_players[0])
                
            elif len(top3_player) == 2:
                    
                if top3_player[0][-8:] > top3_player[1][-8:]:
                        
                    self._player_1 = top3_player[0]
                    self._player_2 = top3_player[1]
                    top3_player[0] = self._player_2
                    top3_player[1] = self._player_1
                        
                file_open.write(top3_player[0] + top3_player[1])

            elif len(top3_player) == 3:
                
                self._player_1 = top3_player[0]
                self._player_2 = top3_player[1]
                self._player_3 = top3_player[2]

                if self._player_1[-8:] < self._player_2[-8:] and self._player_1[-8:] < self._player_3[-8:]:
                    if self._player_2[-8:] < self._player_3[-8:]:
                        top3_player[0] = self._player_1
                        top3_player[1] = self._player_2
                        top3_player[2] = self._player_3
                    elif self._player_2[-8:] == self._player_3[-8:] and len(self._player_2) < len(self._player_3):
                        top3_player[0] = self._player_1
                        top3_player[1] = self._player_2
                        top3_player[2] = self._player_3
                    else:
                        top3_player[0] = self._player_1
                        top3_player[1] = self._player_3
                        top3_player[2] = self._player_2

                elif self._player_2[-8:] < self._player_3[-8:] and self._player_2[-8:] < self._player_1[-8:]:
                    if self._player_1[-8:] < self._player_3[-8:]:
                        top3_player[0] = self._player_2
                        top3_player[1] = self._player_1
                        top3_player[2] = self._player_3
                    elif self._player_1[-8:] == self._player_3[-8:] and len(self._player_1) < len(self._player_3):
                        top3_player[0] = self._player_2
                        top3_player[1] = self._player_1
                        top3_player[2] = self._player_3
                    else:
                        top3_player[0] = self._player_2
                        top3_player[1] = self._player_3
                        top3_player[2] = self._player_1

                elif self._player_3[-8:] < self._player_1[-8:] and self._player_3[-8:] < self._player_2[-8:]:
                    if self._player_1[-8:] < self._player_2[-8:]:
                        top3_player[0] = self._player_3
                        top3_player[1] = self._player_1
                        top3_player[2] = self._player_2
                    elif self._player_1[-8:] == self._player_2[-8:] and len(self._player_1) < len(self._player_2):
                        top3_player[0] = self._player_3
                        top3_player[1] = self._player_1
                        top3_player[2] = self._player_2
                    else:
                        top3_player[0] = self._player_3
                        top3_player[1] = self._player_2
                        top3_player[2] = self._player_1
                        
                file_open.write(top3_player[0] + top3_player[1] + top3_player[2])
                
            elif len(top3_player) > 3:
                for i in top3_player[3::]:
                    if i[-8:] < top3_player[0][-8:]:
                        top3_player[2] = top3_player[1]
                        top3_player[1] = top3_player[0]
                        top3_player[0] = i
                    elif top3_player[0][-8:] <= i[-8:] <= top3_player[1][-8:]:
                        top3_player[2] = top3_player[1]
                        top3_player[1] = i
                    elif top3_player[1][-8:] <= i[-8:] <= top3_player[2][-8:]:
                        top3_player[2] = i
                file_open.write(top3_player[0] + top3_player[1] + top3_player[2])
                
            file_open.close()

        except FileNotFoundError:
            self._scores_file = open("scores_file.txt", "w+")
            self._scores_file.write(player_name + ": " + playing_time + "\n")
            self._scores_file.close()

    def save_game(self):
        """
        Save current game.

        """
        self._status_bar.stop_time()

        if self._filename is None:
            filename = filedialog.asksaveasfilename()
            if filename:
                self._filename = filename

        if self._filename:
            self._master.title(self._filename)
            self._time = self._status_bar.save_time()
            file = open(self._filename, 'w')
            file.write(str(self._dungeon_size) + "\n")
            file.write(str(self._game.get_player().get_position()) + "\n")
            file.write(str(self._time) + "\n")
            file.write(str(self._game.get_player().moves_remaining()) + "\n")
            file.write(str(self._lives_remaining) + "\n")
            dungeon1 = self._game.get_game_information()
            for k, v in dungeon1.items():
                file.write(str(k) + '-' + str(v)[-3] + '\n')
            
            file.close()

    def load_game(self):
        """
        Load a saved game by opening a correct file.
        
        """
        self._status_bar.stop_time()
        filename = filedialog.askopenfilename()
        self._filename = filename
        self._master.title(self._filename)
        file = open(filename, 'r')
        
        file_contents = file.readlines()

        self._dungeon_size = int(file_contents[0])
        self._player_position = eval(file_contents[1])
        self._time = str(file_contents[2])
        self._moves_left = int(file_contents[3])
        self._lives_remaining = int(file_contents[4])
        
        dungeon = {}
        for line in file_contents[5:]:
            line = line.strip()
            k = line.split('-')[0]
            v = line.split('-')[1]
            if v == DOOR:
                v = Door()
            elif v == WALL:
                v = Wall()
            elif v == MOVE_INCREASE:
                v = MoveIncrease()
            elif v == KEY:
                v = Key()
            dungeon[eval(k)] = v
        if Key() not in dungeon:
            self._game.get_player().add_item(Key())

        seconds = int(self._time[0]) * 60 + int(self._time[3])
        self._status_bar.update_timer()
        self._status_bar.continue_saved_time(seconds)
        
        if self._task == MASTERS:
            self._status_bar.update_live_times()
        self._status_bar.update_move_remaining(self._moves_left)
        self._game.set_game_information(dungeon)
        self._game.get_player().set_position(self._player_position)
        self._game.get_player().set_move_remaining(self._moves_left)
        self._view.draw_grid(dungeon, self._player_position)
       
        file.close()

    def new_game(self):
        """
        Restart the current game, including game timer.

        """
        self._filename = None
        self._game = GameLogic()
        self._moves_left = self._game.get_player().moves_remaining()
        if self._task == MASTERS:
            self._status_bar.reset_live_times()
            self._status_bar.update_live_times()
        if self._task != TASK_ONE:
            self._status_bar.update_move_remaining(self._moves_left)
            self._status_bar.stop_time()
            self._status_bar.update_timer()
            self._status_bar.reset_timer()
        self._view.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())
        
    def high_scores(self):
        """
        Get three highers scores and corresponding players' names.
        
        """
        top_page = Toplevel(self._master, bg = 'white')
        top_page.title("High Scores")
        label1 = tk.Label(top_page, text = "High Scores", foreground = "black", bg = "medium spring green")
        label1.pack(side = TOP, fill = tk.X)
        button = Button(top_page, text = "Done", command = top_page.destroy)
        button.pack(side = BOTTOM)
        
        try:
            file_contents = self.read_file()
            label2 = tk.Label(top_page, text = file_contents[0], bg = 'white')
            label2.pack(side = tk.TOP)
            label3 = tk.Label(top_page, text = file_contents[1], bg = 'white')
            label3.pack(side = tk.TOP)
            label4 = tk.Label(top_page, text = file_contents[2], bg = 'white')
            label4.pack(side = tk.TOP)

        except:
            pass

    def read_file(self):
        """
        Read a file which saves three highest scores.

        """
        file_open = open("scores_file.txt", 'r')
        top3_player = file_open.readlines()
        file_open.close()
        return top3_player

class StatusBar(tk.Frame):
    """
    StatusBar display.

    Shows the quit button, newgame buttom, using time, and move remaining of player.
    
    """
    def __init__(self, master, Moves_left, parent):
        """
        Create a status bar.

        Parameters:
            master: the window of bar.
            Moves_left (int): The number of steps the player has left.
            parent: the GameApp object.
            
        """
        super().__init__(master)
        self._master = master
        self._Moves_left = str(Moves_left)
        self._parent = parent
    
        self._seconds = 0

        self._frame1 = tk.Frame(self._master)
        self._frame1.pack(side = tk.LEFT)
        self._button1 = tk.Button(self._frame1, text = "New game", command = self._parent.new_game, bg = "white")
        self._button1.pack(side = tk.TOP)
        self._button2 = tk.Button(self._frame1, text = "Quit", command = self._parent.quite, bg = "white")                     
        self._button2.pack(side = tk.BOTTOM)
        
        self._frame2 = tk.Frame(self._master)
        self._frame2.pack(side = tk.LEFT, ipadx = 26)
        self._image1 = ImageTk.PhotoImage(image = Image.open("images/clock.gif").resize((60,75)))
        self._label1 = tk.Label(self._frame2, image = self._image1)
        self._label1.pack(side = tk.LEFT)
        self._label2 = tk.Label(self._frame2, text = "Time elapsed")
        self._label2.pack(pady = 5)
        self._label3 = tk.Label(self._frame2, text = "0m" + " 0s")
        self._id = self._master.after(1000, self.update_timer)
        self._label3.pack()
        
        self._frame3 = tk.Frame(self._master)
        self._frame3.pack(side = tk.LEFT, ipadx = 26)
        self._image2 = ImageTk.PhotoImage(image = Image.open("images/lightning.gif").resize((50,75)))
        self._label4 = tk.Label(self._frame3, image = self._image2)
        self._label4.pack(side = tk.LEFT)
        self._label5 = tk.Label(self._frame3, text = "Moves left")
        self._label5.pack(pady = 5)
        self._label6 = tk.Label(self._frame3, text = self._Moves_left + ' ' + "moves remaining")
        self._label6.pack()
        
    def update_timer(self):
        """
        Update time in every second.
        
        """
        self._seconds += 1
        self._label3.configure(text = "%im " % (self._seconds // 60) + "%is" % (self._seconds % 60))
        self._id = self._master.after(1000, self.update_timer)

    def stop_time(self):
        """
        Cancel the method of "after", stop the circle of time.

        """
        self._master.after_cancel(self._id)
        
    def update_move_remaining(self, num_moves_remaining):
        """
        Update the move remaining of player in status bar.
 
        Parameters:
            num_moves_remaining (int): the moves remaining of player.
        
        """
        self._label6.configure(text = str(num_moves_remaining) + ' ' + "moves remaining")

    def reset_timer(self):
        """
        Set time to 0m 0s.
        
        """
        self._seconds = 0
        self._label3.configure(text = "%im " % (self._seconds // 60) + "%is " % (self._seconds % 60))

    def save_time(self):
        """
        Save current time.
        
        """
        return self._label3['text']

    def continue_saved_time(self, seconds):
        """
        Continue saved time.

        Parameters:
            seconds(int): The saved seconds.
            
        """
        self._seconds = seconds
        self._label3.configure(text = "%im " % (self._seconds // 60) + "%is" % (self._seconds % 60))

class LivesRemaining(StatusBar):
    """
    StatusBar display.

    Displays the number of lives available.
    
    """
    def __init__(self, master, moveleft, parent):
        """
        Create a new window behind the Status bar.

        Parameters:
            master: the window of bar.
            moveleft (int): The number of steps the player has left.
            parent: the GameApp object.
            
        """
        super().__init__(master, Moves_left = moveleft, parent = parent)
        self._master = master
        self._parent = parent
        
        self._frame4 = tk.Frame(self._master)
        self._frame4.pack(side = tk.LEFT, ipadx = 26)
        self._image3 = ImageTk.PhotoImage(image = Image.open("images/lives.gif").resize((75,75)))
        self._label7 = tk.Label(self._frame4, image = self._image3)
        self._label7.pack(side = tk.LEFT)
        self._label8 = tk.Label(self._frame4, text = "Lives remaining : " + str(self._parent._lives_remaining))
        self._label8.pack(pady = 5)
        self._button3 = tk.Button(self._frame4, text = "Use life", command = self.use_life, bg = "white")
        self._button3.pack()

        self._life_record = []
        
    def use_life(self):
        """
        Gives the user a chance to undo the most recent move.
        
        """
        self.update_move_remaining(self._parent._game.get_player().moves_remaining())
        
        if self._parent._lives_remaining > 0:
            self._parent._lives_remaining -= 1
            self.update_live_times()
            stored_step = self._life_record
            past_information = stored_step[self._parent._lives_remaining-3]
            self.continue_saved_time(int(past_information[1][0]) * 60 + int(past_information[1][3]))
            self.update_move_remaining(past_information[2])
            self._parent._game.set_game_information(past_information[3])
            self._parent._game.get_player().set_position(past_information[0])
            self._parent._game.get_player().set_move_remaining(past_information[2])
            self._parent._view.draw_grid(past_information[3], past_information[0])

        else:
            return None

    def save_step(self, moveleft, player_pos, gameinformation):
        """
        Save every step of game.

        Parameters:
            moveleft (int): An integer representing the number of moves of Player.
            player_pos (tuple): The position of Player.
            gameinformation (dict): A dictionary containing the position
            and the corresponding Entity as the keys and values respectively.

        Returns:
            ((tuple<tuple<int, int>), (str), (int), (dict<tuple<int, int>: Entity)):
            Returns a tuple including all of the information of every step.
            
        """
        if self._parent._lives_remaining == 0:
            pass
        
        life_record_each = []
        
        self._moveleft = moveleft
        self._player_pos = player_pos
        self._time = self.save_time()
        self._gameinformation = gameinformation
        
        life_record_each.append(self._player_pos)
        life_record_each.append(self._time)
        life_record_each.append(self._moveleft)
        life_record_each.append(self._gameinformation)
        self._tuple_each = tuple(life_record_each)

        return self._tuple_each
    
    def store(self, step):
        """
        Store every step into a list.
        
        """
        self._life_record.append(step)
        return self._life_record

    def update_live_times(self):
        """
        Update the live times.
        
        """
        self._label8.configure(text = "Lives remaining : " + str(self._parent._lives_remaining))

    def reset_live_times(self):
        """
        Reset the live times to 3.
        
        """
        self._parent._lives_remaining = 3
    
class FileMenu:
    """
    The file menu for dungeon game.
    
    """
    def __init__(self, master, parent):
        """
        Create the file menu.

        Parameters:
            master: the view of File Menu.
            parent: the GameApp object.
        
        """
        self._master = master
        menu_bar = tk.Menu(self._master)
        self._master.config(menu = menu_bar)
        file_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(label = "File", menu = file_menu)
        file_menu.add_command(label = "Save game", command = parent.save_game)
        file_menu.add_command(label = "Load game", command = parent.load_game)
        file_menu.add_command(label = "New game", command = parent.new_game)
        file_menu.add_command(label = "Quit", command = parent.quite)
        file_menu.add_command(label = "High scores", command = parent.high_scores)
      
def main():
    """
    Main
    
    """
    root = tk.Tk()
    GameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
