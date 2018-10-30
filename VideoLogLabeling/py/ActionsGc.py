'''
Here should be all actions defined, which should be parsed from a gamecontroller log file.

def gamstatechanges(msg:dict, type='gtc'):
    # is it a gamecontroller message
    if 'packetNumber' in msg:
        print(msg)
'''

def ready(msg:dict):
    # is it a gamecontroller message and the gamestate is 'READY'
    if 'packetNumber' in msg and 'gameState' in msg and msg['gameState'] == 1:
        return True
    return False
