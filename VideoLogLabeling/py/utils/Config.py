import json
import os

# the file to read the config from
config_file = '../config'
# the default config dict
config = {
    'paths': [],
    'game': {
        'regex': '(\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}-\\d{2})_(\\S+)_vs_(\\S+)_half([1,2])',
        'dirs': {
            'video': 'videos',
            'gc': 'gc_logs',
            'nao': 'game_logs',
            'data': 'extracted'
        },
        "video_file": "videos.json",
        'video_types': []
    },
    'event': {
        'regex': '(\\d{4}-\\d{2}-\\d{2})_(\\w+)'
    },
    'log': {
        'regex': '(\\d{1})_(\\d{2})_(\\w+)',
        'labels': ['labels', '.json'],
        'name': 'game.log',
        'sync': 'game.log.videoanalyzer.properties'
    },
    'gc': {
        'regex': 'teamcomm_\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}-\\d{2}-\\d{3}_(.+)_(.+)_\\d.{2}Half.log',
        'file': 'gc.json',
        'conv_ext': 'json',
        'conv_options': ['--gtc']
    }
}

# read the config file and apply the contents to the default config dict
if os.path.isfile(config_file):
    try:
        _config = json.load(open(config_file, 'r'))
        # TODO: update recursively
        config.update(_config)
    except:
        pass