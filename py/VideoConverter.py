#!/usr/bin/env python
#encoding: UTF-8

import sys
import os
import argparse
import logging
import mimetypes
import re
import subprocess
import json
import signal

'''
    TODO:
        * search for video files
        * determine which files are missing (thumbnail, format, quality)
        * start converting files (ask before?)
        * show progress
        * implement ability to get progress from extern (eg. php)
    INFO:
        * https://github.com/senko/python-video-converter/blob/master/converter/ffmpeg.py
'''

class VideoConverter:
    """Class for converting VideoFile's."""

    def __init__(self, video, config):
        self.video = video
        self.config = config
        self.todo = {}

    def analyze(self):
        """Analyzes the given VideoFile if it met all requested configurations."""
        for conf in self.config:
            # iterate over files of this video and ...
            for f in self.video.files:
                hasAllAttributes = True
                # ... check if the given configuration applies to one file ...
                for attr in conf:
                    hasAllAttributes = hasAllAttributes and attr in f and (conf[attr] == f[attr] if not isinstance(f[attr], list) else conf[attr] in f[attr])
                # ... if it does, the VideoFile doesn't need to be converted for this configuration
                if hasAllAttributes:
                    conf['todo'] = False
                    # skip the rest since a valid file for the configuration was found
                    break
            # if there's no file matching the configuration, the VideoFile should be converted.
            if 'todo' not in conf:
                # TODO: 'unconvertable' heights should be ignored here!
                conf['todo'] = True
        # only set&return the configuration which needs to be converted
        self.todo = filter(lambda i: i['todo'] ,self.config)
        return self.todo
    
    def getTodo(self):
        """Returns the configuration which should be converted."""
        # anaylzes the VideoFile if it wasn't analyzed before
        return self.todo if self.todo else self.analyze()
    
    def __str__(self):
        """"String representation of the required conversion."""
        result = self.video.source
        for todo in self.getTodo():
            result += '\n\t* ' + str(todo)
        return result
    
    def _makeConfigString(self, config):
        """Creates a string representing the configuration."""
        result = []
        for i in config:
            # ignoring 'internal' todo-configuration and the format (should be used as extension)
            if i == 'todo' or i == 'format':
                continue
            elif i == 'height':
                result.append(str(config[i]) + 'p')
            elif i == 'muted' and config[i]:
                result.append('m')
        # seperate each configuration attribute by a dot - makes it easier to parse it later
        return '.'.join(result)
    
    def convert(self, todo = None):
        """Converts the VideoFile with the given or pending configuration."""
        if todo is None:
            todo = self.getTodo()
        # assuming todo as list
        if not isinstance(todo, list):
            # ... make it one
            todo = [todo]
        # iterate over pending conversions
        for do in todo:
            # it makes no sense to scale video UP.
            if 'height' in do and self.video.getSourceInfo()['height'] < do['height']:
                getLogger().debug('Skipping height configuration.')
            else:
                # determine file format, if nothing was set via configuration use the format of the source file
                extension = do['format'] if 'format' in do else self.video.getSourceExtension()
                # the output file ...
                outfile = self.video.getKey() + '.' + self._makeConfigString(do) + '.' + extension
                # by default the output file gets overwritten
                overwrite = 'y'
                # ask the user
                if os.path.exists(outfile):
                    overwrite = question('Output file already exits ('+outfile+'). Overwrite? [Y]es/[N]o: ', '[Y|N]: ', ['y','n'])
                # proceed (and overwrite) if answer is 'yes'
                if overwrite.lower() == 'y':
                    # convert the source file with the configuration to the outputfile
                    ffmpeg.convert(self.video.source, outfile, do)

class VideoFile:
    """Class representing one video.
    
    A video can consists of multiple files, corresponding to different video configurations.
    For example differents resolution, quality, bitrates and so on.
    """
    
    def __init__(self, file):
        """Constructor, analyzes the given file based on the file name and sets the internal state appropiatly."""
        file = os.path.abspath(file)
        m = re.match('(?P<name>[^\.]+)(\.(?P<config>.+))?\.(?P<ext>.+)', os.path.basename(file))
        # the video 'source' file has no configuration string in its file name
        self.source = file if m.group('config') is None else None
        # all additional files have the same directory path and file name (only different file name suffixes)
        self.path = os.path.dirname(file)
        self.name = m.group('name')
        self.files = [ {
            'filename': file,
            'extension': m.group('ext').lower(),
            'config': self._parseConfig(m.group('config'))
        } ]
    
    def add(self, video):
        """Adds another file to this video."""
        # the other video file should be a VideoFile object
        if isinstance(video, str):
            video = VideoFile(video)
        # the other file is only added if its representing the same video
        if self.getKey() != video.getKey():
            getLogger().debug('Files doesn\'t represents same video content!')
        else:
            # only one file can represent the source file
            self.source = video.source if self.source is None else self.source
            self.files += video.files
    
    def __repr__(self):
        """The representation of the VideoFile."""
        return str(self.files)
    
    def __str__(self):
        """The string representation of the VideoFile."""
        return str(self.__repr__())
    
    def getKey(self):
        """The key of the VideoFile is defined by its path and basename."""
        return self.path + os.sep + self.name
    
    def analyze(self):
        """Analyzes each file of this video and updates its configuration."""
        for file in self.files:
            file.update(ffmpeg.getMediaInfo(file['filename']))
    
    def _parseConfig(self, string):
        """Parses the configuration part of the file name and returns it as dict."""
        if string is None:
            return None
        
        config = {}
        for part in string.split('.'):
            if part == 'm':
                config['muted'] = True
            elif re.match('\d+p', part):
                config['height'] = part
        return config

    def getExtensions(self):
        """Returns the available extensions in this VideoFile."""
        return set([ f['extension'] for f in self.files if 'extension' in f ])
    
    def getHeights(self):
        """Returns the available resolutions (heights) in this VideoFile."""
        return set([ f['height'] for f in self.files if 'height' in f ])
    
    def getMaxHeight(self):
        """Returns the max. resolution (height) in this VideoFile."""
        return max(self.getHeights())
    
    def getSourceInfo(self):
        """Returns the configuration (info) of the source video file (if available)."""
        result = filter(lambda f: (self.source == f['filename']), self.files)
        if result:
            return result[0]
        return None
    
    def getSourceExtension(self):
        """Returns the source extension of this VideoFile (if available)."""
        if self.source is None:
            return None
        return self.getSourceInfo()['extension']
        

class FFMpeg:
    '''Wrapper class for executing FFMpeg.'''
    
    def __init__(self, ffmpeg_path='ffmpeg', ffprobe_path='ffprobe'):
        # check 'ffmpeg'
        ffmpeg_path = self.which(ffmpeg_path) if '/' not in ffmpeg_path else ffmpeg_path
        try:
            # try to execute ffmpeg and catch exceptions if it doesn't work!
            subprocess.check_output([ffmpeg_path, '-version'], stderr=subprocess.STDOUT)
            self.ffmpeg_path = ffmpeg_path
        except Exception as e:
            getLogger().error('Couldn\'t find ffmpeg!')
            self.ffmpeg_path = None
        # check 'ffprobe'
        ffprobe_path = self.which(ffprobe_path) if '/' not in ffprobe_path else ffprobe_path
        try:
            # try to execute ffprobe and catch exceptions if it doesn't work!
            subprocess.check_output([ffprobe_path, '-version'], stderr=subprocess.STDOUT)
            self.ffprobe_path = ffprobe_path
        except Exception as e:
            getLogger().error('Couldn\'t find ffprobe!')
            self.ffprobe_path = None

    def which(self, name):
        try:
            return subprocess.check_output(['which', name]).strip()
        except:
            path = os.environ.get('PATH', os.defpath)
            for d in path.split(':'):
                fpath = os.path.join(d, name)
                if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                    return fpath
        return name
    
    def isValid(self):
        return self.ffmpeg_path is not None and self.ffprobe_path is not None
    
    def getMediaInfo(self, file):
        info = {}
        try:
            # loading media info with ffprobe as json
            data = subprocess.check_output([self.ffprobe_path, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', file], stderr=subprocess.STDOUT)
            # TODO: check result on error?!?
            js = json.loads(data)
            # set the infos
            info['filename'] = js['format']['filename']
            info['size'] = int(js['format']['size'])
            info['duration'] = float(js['format']['duration'])
            info['bitrate'] = int(js['format']['bit_rate'])
            info['format'] = js['format']['format_name'].split(',')
            for stream in js['streams']:
                if stream['codec_type'] == 'video':
                    # log multiple video streams
                    if 'width' in info:
                        getLogger().debug('There seems to more than one video stream in the file (%s)', file)
                    info['width'] = stream['width']
                    info['height'] = stream['height']
        except Exception, e:
            getLogger().error('An error occurred parsing file info (%s): %s', file, e)
        return info
    
    def _spawn(self, cmds):
        getLogger().debug('Spawning ffmpeg with command: ' + ' '.join(cmds))
        return subprocess.Popen(cmds, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    
    def convert(self, infile, outfile, params, timeout=10):
        if not os.path.exists(infile):
            getLogger().error('File doesn\'t exists!')
        
        cmds = [self.ffmpeg_path, '-i', infile]
        cmds.extend(self._config2ffmpeg(params))
        cmds.extend(['-y', outfile])
        
        def on_sigint(*_):
            if p is not None:
                # send SIGTERM to ffmpeg
                p.terminate()
                # set alarm off
                signal.alarm(0)
                # unregister handler for alarm signal
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                #
                getLogger().error('Waiting for ffmpeg to exit ...')
                # wait 'till ffmpeg exits
                p.communicate()
            raise Exception('interrupted!')
        
        # register SIGINT handler
        signal.signal(signal.SIGINT, on_sigint)
        
        # timeout needs to be positive
        if timeout:
            def on_sigalrm(*_):
                # after calling the singal, reset alarm signal -> unregister handler
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                raise Exception('timed out while waiting for ffmpeg')
            # set the alarm handler to the signal
            signal.signal(signal.SIGALRM, on_sigalrm)
        
        try:
            p = self._spawn(cmds)
        except OSError:
            raise Exception('Error while calling ffmpeg binary')
        
        buffer = ''
        while True:
            if timeout:
                # set alarm to "timeout" seconds
                signal.alarm(timeout)
            
            # try to read data from ffmpeg output
            ret = p.stderr.read(10)
            
            if timeout:
                # we got data from ffmpeg, disable alarm
                signal.alarm(0)
            
            # if we didn't get any new data from ffmpeg, we're done ...
            if not ret:
                break
                
            buffer += ret
            
            if '\r' in buffer:
                line, buffer = buffer.split('\r', 1)
                if 'frame' == line[0:5]:
                    print "\r%s"%line,
                    sys.stdout.flush()
        
        if timeout:
            # unregister alarm signal handler
            signal.signal(signal.SIGALRM, signal.SIG_DFL)

        # wait for ffmpeg to exit
        p.communicate()
        
        if p.returncode != 0:
            # TODO: use logger or throw exception?!
            print 'Exited with code %d' % p.returncode
            print buffer
            
    def _config2ffmpeg(self, config):
        result = []
        if 'format' in config:
            if config['format'] == 'webm':
                #result.extend(['-vcodec','libvpx'])
                result.extend(['-vcodec','libvpx-vp9'])
                result.extend(['-preset','veryfast'])
                result.extend(['-threads','4'])
            elif config['format'] == 'mp4':
                result.extend(['-c:v','libx264'])
                result.extend(['-preset','veryfast'])
            #-vcodec libvpx -crf 10 -preset veryfast -b:v 1M -acodec libvorbis "${name}".webm;
            #ffmpeg -i half1.mp4 -filter:v scale="trunc(oh*a/2)*2:144" -an half1.144p.an.mp4
        if 'height' in config:
            result.extend(['-filter:v','scale=trunc(oh*a/2)*2:'+str(config['height'])+''])
        
        result.append('-an')
        
        return result
        
    
# TODO: add "pre-configuration" flag -> don't ask any questions!
def getArguments():
	parser = argparse.ArgumentParser(description='TODO ...') # TODO ...
	parser.add_argument('-f', '--file', 	action='store', help='video file which should be converted.')
        parser.add_argument('-d', '--directory',action='store', help='log directory where the video files should be searched.')
        parser.add_argument('-v' ,'--verbose', 	action='store_true', help='print everything')
	return parser


def getLogger(suffix=None):
    return logging.getLogger(os.path.splitext(os.path.basename(__file__))[0]+('.'+suffix if suffix is not None else ''))

def question(string, short, options):
    choice = raw_input(string)
    while choice.lower() not in options:
        choice = raw_input(short)
    return choice

def searchVideoFiles(self, path):
    assert os.path.isdir(path), 'Not a directoy!'
    result = {}
    filter = re.compile('video/.*')
    mimetypes.init() # do we need this?!
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            f = os.path.join(dirpath, filename)
            # filter video files
            if mimetypes.guess_type(f)[0] is not None and filter.match(mimetypes.guess_type(f)[0]):
                video = VideoFile(f)
                if video.getKey() in result:
                    result[video.getKey()].add(video)
                else:
                    result[video.getKey()] = video
    return result
if __name__ == "__main__":
    args = getArguments().parse_args()
    
    # setup logger
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO )
    
    # setup ffmpeg wrapper class
    ffmpeg = FFMpeg()
    if not ffmpeg.isValid():
        exit(1)
    
    # TODO: add muted config
    formats = [ { 'format': 'mp4',  'height': 144 },
                { 'format': 'webm', 'height': 144 },
                { 'format': 'mp4',  'height': 240 },
                { 'format': 'webm', 'height': 240 },
                { 'format': 'mp4',  'height': 360 },
                { 'format': 'webm', 'height': 360 },
                { 'format': 'mp4',  'height': 480 },
                { 'format': 'webm', 'height': 480 },
                { 'format': 'mp4',  'height': 720 },
                { 'format': 'webm', 'height': 720 }, ]
                
    todo_list = []
    
    if args.file is not None:
        # TODO: process file
        assert os.path.isfile(args.file), 'Not a file!'
        files = searchVideoFiles(os.path.dirname(args.file))
        for f in files:
            if args.file.startswith(f):
                files[f].analyze()
                converter = VideoConverter(files[f], formats)
                todo_list.append(converter)
    elif args.directory is not None:
        # TODO: process log directory
        try:
            files = VideoLocator().search(args.directory)
            for key in files:
                files[key].analyze()
                converter = VideoConverter(files[key], formats)
                todo_list.append(converter)
        except Exception as e:
            getLogger().error(e)
    else:
        getArguments().print_help()
        exit()

    print 'The following would be converted:'
    for i in todo_list:
        print '  - ', i
    
    choice = question("\nHow to continue? (cancel [C], convert all [A], ask every file [F], ask every format configuration [M]\n-> ", "[C,A,F,M]-> ", ['c','a','f','m'])
    
    if choice.lower() == 'c':
        exit()
    else:
        # TODO: catch exceptions!
        for video in todo_list:
            print '\n',video.video.source
            if choice.lower() == 'f':
                file_choice = question("\nProceed converting? [Y]es, [S]kip, [C]ancel -> ", "[Y,S,C]-> ", ['c','s','y'])
                if file_choice.lower() == 's':
                    continue
                elif file_choice.lower() == 'c':
                    break
            for todo in video.getTodo():
                if choice.lower() == 'm':
                    config_choice = question("\nContinue with configuration: "+str(todo)+"? [Y]es, [S]kip config, skip [F]ile, [C]ancel all -> ", "[Y,S,F,C]-> ", ['y','s','f','c'])
                    if config_choice.lower() == 's':
                        continue
                    elif config_choice.lower() == 'f':
                        break
                    elif config_choice.lower() == 'c':
                        exit()
                video.convert(todo)
