import json
import os

config_file = '../config'

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
    }
}

if os.path.isfile(config_file):
    try:
        config.update(json.load(open(config_file, 'r')))
    except:
        pass