import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

highest_tile_value = 6
tiles_to_draw_if_two_players = 7
tiles_to_draw_if_more_than_two_players = 5
points_for_zero_zero = 10

separator_line_length = 40
