from dataclasses import dataclass, field
from itertools import combinations_with_replacement, cycle
from random import shuffle
from typing import Optional, List

import config as cfg


class Tile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f'{self.x} {self.y}'

    def __repr__(self):
        return self.__str__()

    def is_double(self) -> bool:
        return self.x == self.y

    @property
    def weight(self) -> int:
        return self.x + self.y

    def __lt__(self, other):
        return self.x <= other.x and self.y < other.y

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self.x == other.x and self.y == other.y)

    def __gt__(self, other):
        return self.x >= other.x and self.y > other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y


@dataclass
class Path:
    index: int = field(repr=False)
    value: int
    depth: int


class Board:
    def __init__(self):
        self.tiles = []
        self.paths = []

    def add_starting_tile(self, tile: Tile):
        self.tiles.append(tile)
        if tile.is_double():
            for i in range(4):
                self.paths.append(Path(index=i, value=tile.x, depth=1))
        else:
            self.paths.append(Path(index=0, value=tile.x, depth=1))
            self.paths.append(Path(index=1, value=tile.y, depth=1))

    def show(self):
        print(f'Tiles: {self.tiles}')
        print(f'Open paths: {self.paths}')

    def process_new_tile(self, tile: Tile):
        # we already know that the tile is suitable for the board
        self.tiles.append(tile)

        # filtering out paths that are not suitable for the tile
        paths = [path for path in self.paths if tile.x == path.value or tile.y == path.value]

        # sorting paths by depth so it prioritizes lowest depth first
        paths.sort(key=lambda x: x.depth)

        # using the first suitable path
        # todo handle cases when tile has two different values that are both suitable
        chosen_path = self.paths[paths[0].index]
        if tile.x == chosen_path.value:
            chosen_path.value = tile.y
        else:
            chosen_path.value = tile.x
        chosen_path.depth += 1


class Player:
    def __init__(self, index: int):
        self.index = index
        self.hand = []
        self.is_move_available = True
        self.score = 0

    def show_hand(self):
        for tile in self.hand[:-1]:
            print(tile, end=', ')
        print(self.hand[-1])

    def get_total_weight(self) -> int:
        return sum(x.weight for x in self.hand)

    def take_tile_out_of_hand(self, tile: Tile) -> Optional[Tile]:
        if tile not in self.hand:
            return

        return self.hand.pop(self.hand.index(tile))

    def get_highest_rank_tile(self) -> Tile:
        return sorted(self.hand, key=lambda tile: (tile.x, tile.y), reverse=True)[0]

    def is_empty_hand(self) -> bool:
        return not self.hand

    def is_a_goat(self) -> bool:
        return self.score >= 101


class Game:
    def __init__(self):
        self.players = [Player(i) for i in range(cfg.player_count)]
        self.stock = None
        self.board = None

        if cfg.player_count < 2:
            raise RuntimeError('not enough players, need at least 2')
        if cfg.player_count > 4:
            raise RuntimeError('too many players, can only have 2-4 players')

    def run(self):
        round_number = 1
        while not self.is_game_over():
            self.start_round(round_number)

            for player in cycle(self.players):
                print('-' * cfg.separator_line_length)
                if self.is_tie() or self.is_someone_finished():
                    self.write_down_scores()
                    break

                self.board.show()
                self.make_move(player)

            round_number += 1

    def start_round(self, n: int):
        self.stock = [Tile(x, y) for x, y in combinations_with_replacement(range(cfg.highest_tile_value + 1), 2)]
        self.board = Board()

        round_line = f' ROUND {n} '.center(cfg.separator_line_length, '=')
        print(round_line)

        self.refresh_players()
        self.draw_tiles_from_stock()
        self.make_opening_move()
        self.show_players_hands()

    def make_move(self, player: Player):
        suitable_tiles = self.get_suitable_tiles(player)
        while not self.get_suitable_tiles(player):
            print(f'Player {player.index} turn, available tiles {player.hand}, suitable tiles {suitable_tiles}')

            if not self.stock:
                print(f'Player {player.index} has no suitable tiles, but the stock is empty. Aborting the move.')
                player.is_move_available = False
                return

            new_tile_from_stock = self.stock.pop()
            player.hand.append(new_tile_from_stock)
            print(f'Player {player.index} has no suitable tiles, taking one tile from stock... {new_tile_from_stock}')
            suitable_tiles = self.get_suitable_tiles(player)

        print(f'Player {player.index} turn, available tiles {player.hand}, suitable tiles {suitable_tiles}')

        player.is_move_available = True
        valid_move = False
        move = None

        # todo decide if need to allow the blocking move for a double
        while not valid_move:
            try:
                move = Tile(*map(int, input().split()))
            except (ValueError, TypeError):
                print('invalid move')
                continue

            if move not in player.hand:
                print(f"there is no {move} in the player's hand")
            elif move not in suitable_tiles:
                print(f'{move} is not a suitable move')
            else:
                valid_move = True

        move = player.take_tile_out_of_hand(move)
        self.board.process_new_tile(move)

    # Shuffle the entire stock before drawing tiles from it
    def draw_tiles_from_stock(self):
        if cfg.player_count == 2:
            tiles_to_draw = cfg.tiles_to_draw_if_two_players
        else:
            tiles_to_draw = cfg.tiles_to_draw_if_more_than_two_players

        shuffle(self.stock)
        for player in self.players:
            for _ in range(tiles_to_draw):
                player.hand.append(self.stock.pop())

    # Priority for opening move:
    # - lowest double except 0 0
    # - 0 0
    # - highest rank tile such as 5 6
    def make_opening_move(self):
        for double in [Tile(i, i) for i in range(1, cfg.highest_tile_value + 1)]:
            for i, player in enumerate(self.players):
                if double in player.hand:
                    print(f'player {i} has {double}, they start')
                    self.board.add_starting_tile(player.take_tile_out_of_hand(double))

                    # move the player to the last position because they already made the first move
                    self.players.append(self.players.pop(i))
                    return

        zero_double = Tile(0, 0)
        for i, player in enumerate(self.players):
            if zero_double in player.hand:
                print(f'player {i} has {zero_double}, they start')
                self.board.add_starting_tile(player.take_tile_out_of_hand(zero_double))
                self.players.append(self.players.pop(i))
                return

        highest_rank_tile = Tile(0, 0)
        hrt_player_index = 0
        for i, player in enumerate(self.players):
            players_highest_rank_tile = player.get_highest_rank_tile()
            if players_highest_rank_tile > highest_rank_tile:
                highest_rank_tile = players_highest_rank_tile
                hrt_player_index = i

        print(f'player {hrt_player_index} has {highest_rank_tile}, they start')
        self.board.add_starting_tile(self.players[hrt_player_index].take_tile_out_of_hand(highest_rank_tile))
        self.players.append(self.players.pop(hrt_player_index))

    def show_players_hands(self):
        for player in self.players:
            player.show_hand()

    def get_suitable_tiles(self, player: Player) -> List[Tile]:
        suitable_tiles = []
        openings = set((x.value for x in self.board.paths))
        for tile in player.hand:
            if tile.x in openings or tile.y in openings:
                suitable_tiles.append(tile)

        return suitable_tiles

    def is_tie(self) -> bool:
        result = all(not player.is_move_available for player in self.players)
        if result:
            print('Tie! Рыба!')

        return result

    def write_down_scores(self):
        print('-' * cfg.separator_line_length)

        self.players.sort(key=lambda x: x.index)
        for player in self.players:
            delta = player.get_total_weight()

            # handling the `0 0 left` case
            if delta == 0 and not player.is_empty_hand():
                delta = cfg.points_for_zero_zero

            player.score += delta
            delta_line = f' (+{delta})' if delta else ''
            print(f"Player {player.index}: {player.score} points{delta_line}")

    def is_someone_finished(self) -> bool:
        for player in self.players:
            if player.is_empty_hand():
                print(f'Player {player.index} has no more tiles!')
                return True

        return False

    def is_game_over(self) -> bool:
        is_goat_detected = False
        for player in self.players:
            if player.is_a_goat():
                print(f'Player {player.index} has {player.score} points and is a goat!')
                is_goat_detected = True

        return is_goat_detected

    def refresh_players(self):
        for player in self.players:
            player.hand = []
            player.is_move_available = True


if __name__ == '__main__':
    game = Game()
    game.run()
