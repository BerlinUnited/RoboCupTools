'''
Here should be all actions defined, which should be parsed from a log file.
'''

def ready(symbols, option):
    return symbols['game.state'] == 1

def finish(symbols, option):
    return symbols['game.state'] == 4

def penalized(symbols, option):
    return symbols['game.state'] == 5

def turn(symbols, option):
    return 'turn_to_attack_direction' in option

def kick_right(symbols, option):
    return 'sidekick' in option and option['sidekick']['state'].name == 'sidekick_left_foot'

def kick_left(symbols, option):
    return 'sidekick' in option and option['sidekick']['state'].name == 'sidekick_right_foot'

def kick_short(symbols, option):
    return 'fast_forward_kick' in option

def kick_long(symbols, option):
    return 'kick_with_foot' in option

def sidekick_right(symbols, option):
    return 'path_striker2018' in option and option['path_striker2018']['state'].name == 'sidekick_right'

def sidekick_left(symbols, option):
    return 'path_striker2018' in option and option['path_striker2018']['state'].name == 'sidekick_left'

def forwardkick_left(symbols, option):
    return 'path_striker2018' in option and option['path_striker2018']['state'].name == 'forwardkick_left'

def forwardkick_right(symbols, option):
    return 'path_striker2018' in option and option['path_striker2018']['state'].name == 'forwardkick_right'

def fallen(symbols, option):
    return 'fall_down_and_stand_up' in option and option['fall_down_and_stand_up']['state'].name == 'stand_up'