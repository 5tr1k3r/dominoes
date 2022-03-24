import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

tiles_to_draw_if_two_players = 7
tiles_to_draw_if_more_than_two_players = 5
points_for_zero_zero = 10

separator_line_length = 40

all_hands_are_shown = False
