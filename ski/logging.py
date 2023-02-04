import logging

def init():
    # Configure points log
    points_log = logging.getLogger('points')
    points_log.setLevel(logging.ERROR)
    points_log_hander = logging.FileHandler('points.log', mode='w')
    points_log_hander.formatter = logging.Formatter(fmt='{asctime} {message}', style='{')
    points_log_hander.setLevel(logging.INFO)
    points_log.addHandler(points_log_hander)

