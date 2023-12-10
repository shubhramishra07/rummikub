import random
import collections
from dataclasses import dataclass
import copy
import graphics
from typing import Union

@dataclass
class Color:
    def __init__(self, color: str):
        self.color = color

    def __str__(self):
        return f'{self.color}'
    
    def __eq__(self, other):
        return self.color == other.color
    
    def __hash__(self):
        return hash(self.color)

@dataclass
class Tile:
    def __init__(self, color: Color, number: int, is_joker=False):
        self.color = color
        self.number = number
        self.on_board = False
        self.is_joker = is_joker
    
    def __eq__(self, other):
        if isinstance(other, Tile):
            return self.number == other.number and self.color == other.color and self.on_board == other.on_board
        return False
        
    def __hash__(self):
        # Use a combination of the value and color as a hash
        return hash((self.number, self.color))
        
    def __str__(self):
        if not self.is_joker:
            return f'({self.color}, {self.number})'
        else:
            return f'(JOKER, {self.color}, {self.number})'

@dataclass
class Group:
    tiles: list

    def __str__(self):
        return f'{[str(tile) for tile in self.tiles]}'

@dataclass
class Run:
    tiles: list

    def __str__(self):
        return f'{[str(tile) for tile in self.tiles]}'
       
@dataclass
class TempSet:
    tiles: list

    def __str__(self):
        return f'{[str(tile) for tile in self.tiles]}'
        
Set = Group | Run
# Set = Union[Group, Run]

@dataclass
class Board:
    def __init__(self):
        self.sets = []

    def __str__(self):
        return f'{self.sets}'

    def check_run_validity(self, run):
        total = 0
        for i in range(len(run.tiles)):
            if run.tiles[i].is_joker:
                if i==0:
                    run.tiles[i].number = run.tiles[i + 1].number - 1
                    run.tiles[i].color = run.tiles[i+1].color
                else:
                    run.tiles[i].number = run.tiles[i - 1].number + 1
                    run.tiles[i].color = run.tiles[i - 1].color
            total += run.tiles[i].number
        for j in range(len(run.tiles) - 1):
            if run.tiles[j].number != run.tiles[j+1].number - 1 or run.tiles[j].color != run.tiles[j+1].color:
                return False
        return True, total
           
    def check_group_validity(self, group):
        total = 0
        if len(group.tiles) > 4:
            return False, None
        # checks for different colors
        if len(group.tiles) != len(set(group.tiles)):
            return False, None
        for i in range(len(group.tiles)):
            if group.tiles[i].is_joker:
                if i==0:
                    group.tiles[i].number = group.tiles[i + 1].number
                else:
                    group.tiles[i].number = group.tiles[i - 1].number
            total += group.tiles[i].number
        for j in range(len(group.tiles) - 1):
            if group.tiles[j].number != group.tiles[j+1].number:
                return False, None
        return True, total
        
    def check_board_validity(self, player):
        total = 0
        for s in self.sets:
            # runs/groups should not be smaller than size 3
            if len(s.tiles) < 3:
                return False
            # for each run, we want to check if all values are consecutive
            if isinstance(s, Run):
                if not self.check_run_validity(s):
                    return False
            # for each group, we want to make sure that we have all tiles with the same number, and no two tiles of the same color
            if isinstance(s, Group):
                if not self.check_group_validity(s):
                    return False
            # a tempset is a set of tile put down by the user. we don't know if it's a group or a run yet, but our if/else statements check for it
            if isinstance(s, TempSet):
                # tempset is potentially a group
                if s.tiles[0].number == s.tiles[1].number or s.tiles[1].number == s.tiles[2].number or s.tiles[0].number == s.tiles[2].number:
                    group_val, x = self.check_group_validity(s)
                    if not group_val:
                        return False
                # tempset is potentially a run
                if s.tiles[0].number == s.tiles[1].number - 1 or s.tiles[1].number == s.tiles[2].number - 1 or s.tiles[0].number == s.tiles[2].number - 2:
                    run_val, x = self.check_run_validity(s)
                    if not run_val:
                        return False
                if player.in_quarantine:
                    total += x
        if player.in_quarantine and total < 30:
            return False
        return True
        
    def fix_board(self):
        for s in self.sets:
            for tile in s.tiles:
                tile.on_board = True
            if isinstance(s, TempSet):
                self.sets.remove(s)
                # group
                if s.tiles[0].number == s.tiles[1].number:
                    new_group = Group(s.tiles)
                    self.sets.append(new_group)
                # run
                if s.tiles[0].number == s.tiles[1].number - 1:
                    new_run = Run(s.tiles)
                    self.sets.append(new_run)
        
@dataclass
class Pouch:
    def __init__(self, num_jokers: int, colors: list):
        self.num_jokers = num_jokers
        self.tiles = []
        for _ in range(2):
            for color in colors:
                for number in range(1, 14):
                    t = Tile(color, number)
                    self.tiles.append(t)
                
        for i in range(num_jokers):
            self.tiles.append(Tile(Color("JOKER"), 30, True))

        # shuffling initial tile order to make sure all players are getting random tiles
        self.tiles = random.sample(self.tiles, len(self.tiles))

    def __str__(self):
        return f'{[str(tile) for tile in self.tiles]}'

@dataclass
class Rack:
    def __init__(self, pouch):
        self.pouch = pouch
        tiles = self.generate_random_rack()
        self.tiles = tiles
        
    def generate_random_rack(self) -> []:
        rack = random.sample(self.pouch.tiles, 14)
        return rack
        
    def __str__(self):
        return f'{[str(tile) for tile in self.tiles]}'
        
@dataclass
class Player:
    def __init__(self, in_quarantine: bool, pouch: Pouch):
        self.in_quarantine = in_quarantine
        self.pouch = pouch
        self.rack = Rack(self.pouch)
        self.score = sum(tile.number for tile in self.rack.tiles)
        self.first_move = True

    def __str__(self):
        return f'(in_quarantine: {self.in_quarantine}, score: {self.score}, rack: {[str(tile) for tile in self.rack.tiles]})'
    

@dataclass
class Split:
    def __init__(self, to_split, split_at):
        # either a group or a run
        self.to_split = to_split
        self.split_at = split_at
    
    def __str__(self):
        return f'split {self.to_split} at position {self.split_at}'
    
    def __eq__ (self, other):
        if isinstance(other, Split):
            return self.to_split == other.to_split and self.split_at == other.split_at
        return False
        
@dataclass
class Add:
    def __init__(self, tile, set_to_add, pos_to_add):
        self.tile = tile
        self.set_to_add = set_to_add
        self.pos_to_add = pos_to_add
    
    def __str__(self):
        return f'add {self.tile} to set {self.set_to_add} at position {self.pos_to_add}'
        
    def __eq__(self, other):
        if isinstance(other, Add):
            return self.tile == other.tile and self.set_to_add == other.set_to_add and self.pos_to_add == other.pos_to_add
        return False
  
@dataclass
class PickTile:
    def __init__(self, pouch):
        self.pouch = pouch
        self.tile = random.choice(pouch.tiles)
    
@dataclass
class Game:
    def create_board(self):
        graphics.main(self.players[0].rack.tiles)
        
    def __init__(self, num_players: int, num_jokers: int, colors: list):
        # create a beginning board
        self.board = Board()
        pouch = Pouch(num_jokers=num_jokers, colors=colors)
        # print(pouch)
        players = []
        for _ in range(num_players):
            p = Player(in_quarantine=True, pouch=pouch)
            for tile in p.rack.tiles:
                pouch.tiles.remove(tile)
            players.append(p)
        self.players = players
        self.pouch = pouch
        self.end = False
        # self.create_board()
    
    def possible_moves(self, player):
        # check any tiles that you can directly add to a group
        possible_moves = []
        # single tiles available on the board
        single_tiles = []
        # choosing a tile
        if player.first_move:
            possible_moves.append(PickTile(self.pouch))
        for s in self.board.sets:
            # splitting sets
            if len(s.tiles) == 1:
                single_tiles.append(s.tiles[0])
            for set_tile_pos in range(1, len(s.tiles)):
                move = Split(s, set_tile_pos)
                if move not in possible_moves:
                    possible_moves.append(move)
        for tile in player.rack.tiles:
            for s in self.board.sets:
                possible_moves.append(Add(tile, s, 0))
                possible_moves.append(Add(tile, s, len(s.tiles)))
        for tile in single_tiles:
            for s in self.board.sets:
                possible_moves.append(Add(tile, s, 0))
                possible_moves.append(Add(tile, s, len(s.tiles)))
                """
                # adding to a group
                if tile.is_joker:
                    possible_moves.append(Add(tile, s, 0))
                    possible_moves.append(Add(tile, s, len(s.tiles)))
                    continue
                if isinstance(s, Group) or (isinstance(s, TempSet) and len(s.tiles) == 1):
                    if s.tiles[0].number == tile.number:
                        if tile.color not in [set_tile.color for set_tile in s.tiles]:
                            move = Add(tile, s, 0)
                            if move not in possible_moves:
                                possible_moves.append(move)
                # adding to a run
                if isinstance(s, Run) or (isinstance(s, TempSet) and len(s.tiles) == 1):
                    if s.tiles[0].color == tile.color:
                        if s.tiles[0].number == tile.number + 1:
                            move = Add(tile, s, 0)
                            if move not in possible_moves:
                                possible_moves.append(move)
                        if s.tiles[-1].number == tile.number - 1:
                            move = Add(tile, s, len(s.tiles))
                            if move not in possible_moves:
                                possible_moves.append(move)
                # adding to a tempset
                if isinstance(s, TempSet) and len(s.tiles) > 1:
                    is_run = False
                    is_group = False
                    if s.tiles[0].number == s.tiles[1].number:
                        is_group = True
                    if s.tiles[0].number == s.tiles[1].number - 1:
                        is_run = True
                    if is_group:
                        if s.tiles[0].number == tile.number:
                            if tile.color not in [set_tile.color for set_tile in s.tiles]:
                                move = Add(tile, s, 0)
                                if move not in possible_moves:
                                    possible_moves.append(move)
                    if is_run:
                        if s.tiles[0].color == tile.color:
                            if s.tiles[0].number == tile.number + 1:
                                move = Add(tile, s, 0)
                                if move not in possible_moves:
                                    possible_moves.append(move)
                            if s.tiles[-1].number == tile.number - 1:
                                move = Add(tile, s, len(s.tiles))
                                if move not in possible_moves:
                                    possible_moves.append(move)
                """
                
        for tile in player.rack.tiles:
            possible_moves.append(Add(tile, TempSet([]), 0))
        return possible_moves
                        
    def make_move(self, player, move):
        # when a player splits a group or a run
        if isinstance(move, Split):
            self.board.sets.remove(move.to_split)
            self.board.sets.append(TempSet(move.to_split.tiles[0:move.split_at]))
            self.board.sets.append(TempSet(move.to_split.tiles[move.split_at:]))
        # when a player is adding a tile
        if isinstance(move, Add):
            # tile comes from player's rack
            if move.tile in player.rack.tiles:
                player.first_move = False
            # tile comes from the board
            else:
                for s in self.board.sets:
                    if len(s.tiles) == 1 and s.tiles[0] == move.tile:
                        self.board.sets.remove(s)
                        break
            # if the tile is not being added to a run/group that already exists
            if move.set_to_add.tiles == []:
                self.board.sets.append(TempSet([move.tile]))
            # append tile at the end
            if move.pos_to_add == len(move.set_to_add.tiles):
                for s in self.board.sets:
                    if s == move.set_to_add:
                        s.tiles.append(move.tile)
                        
            # insert tile at the beginning
            if move.pos_to_add == 0:
                for s in self.board.sets:
                    if s == move.set_to_add:
                        s.tiles.insert(0, move.tile)
            if move.tile.on_board == False:
                player.rack.tiles.remove(move.tile)
        if isinstance(move, PickTile):
            player.first_move = False
            t = PickTile(self.pouch).tile
            player.rack.tiles.append(t)
            self.pouch.tiles.remove(t)

    
             
    def __str__(self):
        return f'board: {self.board}, players: {[str(player) for player in self.players]}'
        
    

if __name__ == '__main__':
    colors = [Color("red"), Color("blue"), Color("orange"), Color("black")]
    num_players = 2
    game = Game(num_players = num_players, num_jokers = 2, colors=colors)
    print(game)
    while not game.end:
        for i, player in enumerate(game.players):
            player.first_move = True
            initial_board = copy.deepcopy(game.board)
            initial_player_tiles = copy.deepcopy(player.rack.tiles)
            player.rack.tiles = sorted(player.rack.tiles, key=lambda x: (str(x.color), x.number), reverse=False)
            for s in game.board.sets:
                print(str(s))
            while True:
                possible_moves = game.possible_moves(player)
                for j, move in enumerate(possible_moves):
                    print(str(j)+ ": " + str(move))
                user_input = input("what move would you like to make?")
                if user_input.lower() == "done":
                    print(f"Player {i} hit done. Moving to player {(i+1) % len(game.players)}.")
                    break  # Move to the next player
                try:
                    user_move = int(user_input)
                    game.make_move(player, possible_moves[user_move])
                    if isinstance(possible_moves[user_move], PickTile):
                        print(f"Player {i} picked a tile. Moving to player {(i+1) % len(game.players)}.")
                        break
                except ValueError:
                    print("Invalid input. Please enter a valid integer.")
                
            if game.board.check_board_validity(player):
                if player.first_move:
                    game.make_move(player, PickTile(game.pouch))
                    print(f"Player {i} hit done without picking a tile or adding to the board. Adding a tile to their rack.")
                else:
                    game.board.fix_board()
                    # print(f"Player {i} made a valid move! Moving onto the next player.")
            else:
                print(f"Player {i} made an invalid move! Resetting the board and adding a tile to their rack.")
                game.board = initial_board
                player.rack.tiles = initial_player_tiles
                game.make_move(player, PickTile(game.pouch))
            print(game.board.sets)
            """
            if user_move == 0:
                game.make_move(player, possible_moves[user_move])
            else:
                while user_move != 0:
                    print("hi")
                    for tile in player.rack.tiles:
                        print(tile)
                    game.make_move(player, possible_moves[user_move])
                    possible_moves = game.possible_moves(player)
                    user_input = input("what move would you like to make?")
                    try:
                        user_move = int(user_input)
                        break  # Break out of the loop if conversion is successful
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
            """
            """
            print("Player " + str(i % num_players) + ", here's your rack: ")
            for tile in player.rack.tiles:
                print(tile)
            move = input("What move would you like to make? Type pass if you do not want to make a move.")
            if move == "pass":
                continue
            else:
                while move != "pass":
                    moves = move.split(',')
                    print(moves)
                    move = input("What moves would you like to make? Type pass if you do not want to make any moves, say pass.")
            """
