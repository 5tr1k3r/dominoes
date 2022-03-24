import math
from itertools import combinations_with_replacement
from typing import Tuple, List, Dict

import arcade
from arcade import Window, View, Text

import config as cfg
from models import Game, Player, is_ui_requires_update, Tile

WIDTH = 1000
HEIGHT = 1000
TITLE = 'Dominoes'

TILE_WIDTH = 208
TILE_HEIGHT = 374


class MenuView(View):
    def __init__(self):
        super().__init__()

        self.vertical_margin = 80

        self.play_text = Text("Play", WIDTH / 2, HEIGHT / 2 + self.vertical_margin,
                              arcade.color.YELLOW, 42, anchor_x='center', anchor_y='center')
        self.help_text = Text("Help", WIDTH / 2, HEIGHT / 2,
                              arcade.color.YELLOW, 42, anchor_x='center', anchor_y='center')
        self.quit_text = Text("Quit", WIDTH / 2, HEIGHT / 2 - self.vertical_margin,
                              arcade.color.YELLOW, 42, anchor_x='center', anchor_y='center')
        self.is_play_text_hovered = False
        self.is_help_text_hovered = False
        self.is_quit_text_hovered = False

    def on_show(self):
        arcade.set_background_color(arcade.color.WARM_BLACK)

    def on_draw(self):
        self.clear()
        self.play_text.draw()
        self.help_text.draw()
        self.quit_text.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.is_play_text_hovered = self.change_text_color_on_hover(self.play_text, x, y,
                                                                    self.is_play_text_hovered)
        self.is_help_text_hovered = self.change_text_color_on_hover(self.help_text, x, y,
                                                                    self.is_help_text_hovered)
        self.is_quit_text_hovered = self.change_text_color_on_hover(self.quit_text, x, y,
                                                                    self.is_quit_text_hovered)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.is_play_text_hovered:
            self.window.show_view(GameView())

        if self.is_help_text_hovered:
            self.window.show_view(HelpView())

        if self.is_quit_text_hovered:
            arcade.close_window()

    def change_text_color_on_hover(self, text: Text, mouse_x: float, mouse_y: float, status: bool,
                                   color_on: Tuple[int, int, int] = arcade.color.GREEN,
                                   color_off: Tuple[int, int, int] = arcade.color.YELLOW) -> bool:
        is_text_hovered_now = self.is_text_hovered_over(text, mouse_x, mouse_y)
        if is_text_hovered_now != status:
            status = is_text_hovered_now
            text.color = color_on if status else color_off

        return status

    @staticmethod
    def is_text_hovered_over(text: Text, mouse_x: float, mouse_y: float) -> bool:
        half_width = text.content_width / 2
        half_height = text.content_height / 2
        a = text.x - half_width
        b = text.x + half_width
        c = text.y - half_height
        d = text.y + half_height
        return a <= mouse_x <= b and c <= mouse_y <= d


class HelpView(View):
    def __init__(self):
        super().__init__()
        line = 'not ready yet'
        self.help = Text(line, WIDTH / 2, HEIGHT / 2,
                         arcade.color.YELLOW, 30, anchor_x='center', anchor_y='center',
                         multiline=True, width=400)

    def on_show(self):
        arcade.set_background_color(arcade.color.WARM_BLACK)

    def on_draw(self):
        self.clear()
        self.help.draw()

        arcade.draw_rectangle_outline(self.help.x, self.help.y,
                                      self.help.content_width, self.help.content_height,
                                      arcade.color.RED)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(MenuView())


class GTile(arcade.Sprite):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.is_face_up = False
        self.image_file = f'assets/tiles/{x}{y}.png'
        self.face_down_image = 'assets/tiles/face_down.png'

        image = self.image_file if cfg.all_hands_are_shown else self.face_down_image

        super().__init__(image, hit_box_algorithm='None')

    def turn_face_down(self):
        if cfg.all_hands_are_shown:
            return

        self.texture = arcade.load_texture(self.face_down_image)
        self.is_face_up = False

    def turn_face_up(self):
        self.texture = arcade.load_texture(self.image_file)
        self.is_face_up = True

    def is_horizontal(self):
        return self.angle == 0

    def is_vertical(self):
        return self.angle == -90.0


class GameView(View):
    def __init__(self):
        super().__init__()

        self.ui_width = WIDTH * 0.12

        self.game: Game = self.window.game
        self.game.started = True

        self.all_tiles: Dict[int, GTile] = {int(f'{x}{y}'): GTile(x, y)
                                            for x, y in combinations_with_replacement(range(7), 2)}

        self.hand_tiles = arcade.SpriteList()
        self.suitable_gtiles = arcade.SpriteList()
        self.players_names = self.render_players_names()

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        self.clear()
        self.draw_board()
        self.draw_ui()
        self.draw_stock_tile_count()
        self.draw_players_names()
        self.draw_hands()
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

        # if symbol == arcade.key.ESCAPE:
        #     self.game.is_done = True
        #     self.window.show_view(MenuView())

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        suitable_gtiles = arcade.get_sprites_at_point((x, y), self.suitable_gtiles)
        if not suitable_gtiles:
            return

        # noinspection PyUnresolvedReferences
        x, y = suitable_gtiles[0].x, suitable_gtiles[0].y
        self.game.players[self.game.current_player_id].chosen_move = Tile(x, y)

    def draw_ui(self):
        colors = [arcade.color.DARK_SLATE_GRAY] * 4
        colors[self.game.current_player_id] = arcade.color.DARK_GREEN

        arcade.draw_lrtb_rectangle_filled(self.ui_width, WIDTH,
                                          self.ui_width, 0,
                                          colors[0])
        arcade.draw_lrtb_rectangle_filled(0, WIDTH - self.ui_width,
                                          HEIGHT, HEIGHT - self.ui_width,
                                          colors[1])
        arcade.draw_lrtb_rectangle_outline(self.ui_width, WIDTH,
                                           self.ui_width, 0,
                                           arcade.color.BLACK, border_width=2)
        arcade.draw_lrtb_rectangle_outline(0, WIDTH - self.ui_width,
                                           HEIGHT, HEIGHT - self.ui_width,
                                           arcade.color.BLACK, border_width=2)

        if self.game.player_count > 2:
            arcade.draw_lrtb_rectangle_filled(0, self.ui_width,
                                              HEIGHT - self.ui_width, 0,
                                              colors[2])
            arcade.draw_lrtb_rectangle_filled(WIDTH - self.ui_width, WIDTH,
                                              HEIGHT, self.ui_width,
                                              colors[3])
            arcade.draw_lrtb_rectangle_outline(0, self.ui_width,
                                               HEIGHT - self.ui_width, 0,
                                               arcade.color.BLACK, border_width=2)
            arcade.draw_lrtb_rectangle_outline(WIDTH - self.ui_width, WIDTH,
                                               HEIGHT, self.ui_width,
                                               arcade.color.BLACK, border_width=2)

    def draw_hands(self):
        self.hand_tiles.draw()

    def draw_board(self):
        pass

    def on_update(self, delta_time: float):
        if is_ui_requires_update.is_set():
            self.update_players_hands()
            is_ui_requires_update.clear()

    def update_players_hands(self):
        available_space = WIDTH - self.ui_width
        tile_margin = 5  # distance between tiles

        self.hand_tiles.clear()
        self.suitable_gtiles.clear()
        for i, player in enumerate(self.game.players):
            tile_count = player.get_tile_count()
            if tile_count == 0:
                continue

            # 0 - bottom, 1 - top, 2 - left, 3 - right
            is_top_or_bottom = i in (0, 1)
            is_left_or_right = i in (2, 3)

            new_scale = self.calculate_tile_scale_in_ui(tile_count)
            graphic_tile_w = math.ceil(TILE_WIDTH * new_scale)
            graphic_tile_h = math.ceil(TILE_HEIGHT * new_scale)

            total_width_of_tiles = graphic_tile_w * tile_count + tile_margin * (tile_count - 1)

            tile_left = (available_space - total_width_of_tiles) // 2 + self.ui_width
            tile_bottom = (self.ui_width - graphic_tile_h) // 2

            if i == 1:
                tile_left -= self.ui_width
                tile_bottom = HEIGHT - tile_bottom - graphic_tile_h

            if is_left_or_right:
                tile_left = (self.ui_width - graphic_tile_h) // 2
                tile_bottom = (available_space - total_width_of_tiles) // 2

            if i == 3:
                tile_left = WIDTH - tile_left - graphic_tile_h
                tile_bottom += self.ui_width

            for tile in player.hand:
                graphic_tile = self.all_tiles[int(f'{tile.x}{tile.y}')]
                graphic_tile.alpha = 255

                if i == self.game.current_player_id:
                    graphic_tile.turn_face_up()
                    if tile not in self.game.get_suitable_tiles(player):
                        graphic_tile.alpha = 120
                    else:
                        self.suitable_gtiles.append(graphic_tile)

                elif graphic_tile.is_face_up:
                    graphic_tile.turn_face_down()

                graphic_tile.angle = -90.0 if is_top_or_bottom else 0

                graphic_tile.scale = new_scale
                graphic_tile.left = tile_left
                graphic_tile.bottom = tile_bottom

                if is_top_or_bottom:
                    tile_left += graphic_tile_w + tile_margin
                else:
                    tile_bottom += graphic_tile_w + tile_margin

                self.hand_tiles.append(graphic_tile)

    def calculate_tile_scale_in_ui(self, tile_count: int) -> float:
        available_space = WIDTH - self.ui_width
        margin = 5  # distance from all borders of ui
        tile_margin = 3  # distance between tiles
        w = TILE_WIDTH
        h = TILE_HEIGHT
        max_pos_w = (available_space - margin * 2 - tile_margin * (tile_count - 1)) // tile_count
        max_pos_h = self.ui_width - margin * 2
        scale_w = max_pos_w / w
        scale_h = max_pos_h / h

        return min(scale_w, scale_h)

    def draw_stock_tile_count(self):
        margin = 7
        arcade.draw_text(f'Stock: {len(self.game.stock)}',
                         self.ui_width + margin, self.ui_width + margin,
                         anchor_x='left', anchor_y='baseline',
                         font_size=16)

    def draw_players_names(self):
        for name in self.players_names:
            name.draw()

    def render_players_names(self) -> List[Text]:
        result = []
        margin = 8
        size = 20
        data = [
            (WIDTH / 2, self.ui_width + margin, 'bottom', 0),
            (WIDTH / 2, HEIGHT - self.ui_width - margin, 'top', 0),
            (self.ui_width + margin, HEIGHT / 2, 'bottom', -90.0),
            (WIDTH - self.ui_width - margin, HEIGHT / 2, 'bottom', 90.0),
        ]

        names = [player.name for player in self.game.players]
        for i in range(self.game.player_count):
            result.append(Text(f'{names[i]}', data[i][0], data[i][1],
                               anchor_x='center', anchor_y=data[i][2],
                               font_size=size, rotation=data[i][3]))

        return result


class Dominoes(Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE, center_window=True)

        self.game = Game([
            Player('John'),
            Player('Tom'),
            Player('Patrick'),
            Player('Tamara'),
            # AI('easy', difficulty=1)
        ])
        self.game.start()

        # menu_view = MenuView()
        menu_view = GameView()
        self.show_view(menu_view)


def main():
    Dominoes()
    arcade.run()


if __name__ == '__main__':
    main()
