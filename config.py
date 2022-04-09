import logging

import arcade
import toml

try:
    with open('custom_config.toml') as f:
        cc = toml.load(f)
except FileNotFoundError:
    cc = {}

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

# ============================================ GAME RULES ============================================
tiles_to_draw_if_two_players = cc.get('tiles_to_draw_if_two_players', 7)
tiles_to_draw_if_more_than_two_players = cc.get('tiles_to_draw_if_more_than_two_players', 5)
points_for_zero_zero = cc.get('points_for_zero_zero', 10)
goat_score = cc.get('goat_score', 101)

# ============================================ INTERFACE =============================================
# ----------------------------------------------- MENU -----------------------------------------------
menu_vertical_margin = cc.get('menu_vertical_margin', 80)
menu_font_size = cc.get('menu_font_size', 42)

# ----------------------------------------------- GAME -----------------------------------------------
WIDTH = cc.get('WIDTH', 1000)
HEIGHT = cc.get('HEIGHT', 1000)
TITLE = cc.get('TITLE', 'Dominoes')
TILE_WIDTH = cc.get('TILE_WIDTH', 208)
TILE_HEIGHT = cc.get('TILE_HEIGHT', 374)

all_hands_are_shown = cc.get('all_hands_are_shown', False)
ui_width_ratio = cc.get('ui_width_ratio', 0.12)
starting_zoom = cc.get('starting_zoom', 0.25)
zoom_step = cc.get('zoom_step', 0.04)
camera_speed = cc.get('camera_speed', 0.3)
camera_max_speed = cc.get('camera_max_speed', 7)

table_outline_border_width = cc.get('table_outline_border_width', 2)
table_tile_margin = cc.get('table_tile_margin', 5)
unsuitable_tile_alpha = cc.get('unsuitable_tile_alpha', 120)
border_margin = cc.get('border_margin', 5)
stock_font_margin = cc.get('stock_font_margin', 7)
stock_font_size = cc.get('stock_font_size', 16)
players_font_margin = cc.get('players_font_margin', 8)
players_font_size = cc.get('players_font_size', 20)

board_tile_margin = cc.get('board_tile_margin', 5)

# ----------------------------------------------- HELP -----------------------------------------------
help_top_margin = cc.get('help_top_margin', 20)
help_margin = cc.get('help_margin', 15)
help_step = cc.get('help_step', 50)
help_pad = cc.get('help_pad', 18)
help_font = cc.get('help_font', "Courier New")
help_title_font_size = cc.get('help_title_font_size', 50)
help_font_size = cc.get('help_font_size', 30)
help_border_width = cc.get('help_border_width', 3)

# ========================================== GAMEVIEW TEXT ===========================================
# margin
text_left_margin = cc.get('text_left_margin', 7)

# help tip
help_tip_top_margin = cc.get('help_tip_top_margin', 7)
help_tip_font_size = cc.get('help_tip_font_size', 16)
help_tip_color = arcade.color.RED

# current round text
round_text_top_margin = cc.get('round_text_top_margin', 30)
round_text_font_size = cc.get('round_text_font_size', 12)
round_text_color = arcade.color.WHITE

# ============================================== COLORS ==============================================
# not customizable with custom_config.toml, change it here instead
menu_font_color = arcade.color.YELLOW
menu_active_color = arcade.color.GREEN
menu_bg_color = arcade.color.WARM_BLACK

menu_help_font_color = arcade.color.YELLOW
menu_help_bg_color = arcade.color.WARM_BLACK

game_bg_color = arcade.color.EERIE_BLACK
table_color = arcade.color.DARK_SLATE_GRAY
active_table_color = arcade.color.DARK_GREEN
table_outline_color = arcade.color.BLACK
help_font_color = arcade.color.BLACK
help_bg_color = arcade.color.ASH_GREY + (230,)
lane_marker_outline_color = arcade.color.GREEN
lane_marker_color = arcade.color.GREEN + (50,)
lane_marker_hovered_color = arcade.color.GREEN + (150,)

# =============================================== MISC ===============================================
separator_line_length = cc.get('separator_line_length', 40)
is_sound_on = cc.get('is_sound_on', True)
