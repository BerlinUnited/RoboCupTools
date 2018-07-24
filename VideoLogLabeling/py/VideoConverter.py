#!/usr/bin/env python
#encoding: UTF-8

import sys
import os
import glob
import argparse
import logging
import mimetypes
import re
import subprocess
import json
import signal
import copy

'''
    TODO:
        * creating thumbnail?!
        * using logger ?!
        * show warning, if the config string doesn't match the "file content" (example: muted)
    INFO:
        * https://github.com/senko/python-video-converter/blob/master/converter/ffmpeg.py
'''


class Converter:
    def __init__(self, video_file, config):
        self.video = video_file
        self.config = self._filterConfig(config)
        self.todo = []

    def _filterConfig(self, config):
        raise NotImplementedError("Not implemented: _filterConfig()")
        return []

    def getTodo(self):
        """Returns the configuration which should be converted."""
        # anaylzes the VideoFile if it wasn't analyzed before
        return self.todo if self.todo else self.analyze()
    
    def _prepareAnalyze(self):
        raise NotImplementedError("Not implemented: analyze()")
    
    def analyze(self):
        """Analyzes the given VideoFile if it met all requested configurations."""
        files = self._prepareAnalyze()
        for conf in self.config:
            # iterate over files of this video and ...
            for f in files:
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
                # before finally set the 'todo' flag, check if this configuration makes 'sense' (eg. upscaling is ignored)!
                conf['todo'] = self._checkConfigMeaningfulness(conf)
                conf['outfile'] = self._outputFileName(conf)
        # only set&return the configuration which needs to be converted
        self.todo = filter(lambda i: i['todo'], self.config)
        return self.todo

    def _config2ffmpeg(self, config):
        raise NotImplementedError("Not implemented: _config2ffmpeg()")

    def _outputFileName(self, config):
        """Creates the name of the output file based on the given configuration."""
        # determine file format, if nothing was set via configuration use the format of the source file
        extension = config['format'] if 'format' in config else self.video.getSourceExtension()
        # return the output file ...
        return self.video.getKey() + '.' + self._makeConfigString(config) + '.' + extension
    
    @staticmethod
    def _makeConfigString(config):
        """Creates a string representing the configuration."""
        result = []
        for i in config:
            # ignoring 'internal' todo-configuration and the format (should be used as extension)
            if i == 'todo' or i == 'format' or ('height' in config and 'width' in config):
                continue
            elif i == 'height':
                result.append(str(config[i]) + 'p')
            elif i == 'width':
                result.append(str(config[i]) + 'w')
            elif i == 'muted' and config[i]:
                result.append('m')
        if 'height' in config and 'width' in config:
            result.append(str(config['width']) + 'x' + str(config['height']))
        # seperate each configuration attribute by a dot - makes it easier to parse it later
        return '.'.join(result)
    
    def _checkConfigMeaningfulness(self, config):
        """Checks if all configuration options makes 'sense' for this video (eg. upscaling is ignored)."""
        # it makes no sense to upscale video.
        if 'height' in config and self.video.getSourceInfo()['height'] < config['height']:
            return False
        if 'width' in config and self.video.getSourceInfo()['width'] < config['width']:
            return False
        # INFO: other options can be added here ... (like max. bitrate)
        return True

    def __str__(self):
        """"String representation of the required conversion."""
        result = self.video.source
        for todo in self.getTodo():
            result += '\n\t* ' + str(todo)
        return result

    def convert(self, todo=None):
        """Converts the VideoFile with the given or pending configuration."""
        if todo is None:
            todo = self.getTodo()
        # assuming todo as list
        if not isinstance(todo, list):
            # ... make it one
            todo = [todo]
        # iterate over pending conversions
        for do in todo:
            outfile = do['outfile'] if 'outfile' in do else self._outputFileName(do)
            # by default the output file gets overwritten
            overwrite = 'y'
            # ask the user
            if os.path.exists(outfile):
                overwrite = question('Output file already exits ('+outfile+'). Overwrite? [Y]es/[N]o: ', '[Y|N]: ', ['y', 'n'])
            # proceed (and overwrite) if answer is 'yes'
            if overwrite.lower() == 'y':
                # convert the source file with the configuration to the outputfile
                ffmpeg.convert(self.video.source, outfile, self._config2ffmpeg(do))


class VideoConverter(Converter):
    """Class for converting VideoFile's."""

    def _filterConfig(self, config):
        return [conf for conf in config if 'format' not in conf or conf['format'] in ['mp4', 'webm']]

    def _prepareAnalyze(self):
        return self.video.files

    def _config2ffmpeg(self, config):
        """Translates the given configuration to ffmpeg arguments."""
        result = []
        # TODO: translation of the config to ffmpeg arguments
        if 'format' in config:
            if config['format'] == 'webm':
                #result.extend(['-vcodec', 'libvpx'])
                result.extend(['-vcodec', 'libvpx-vp9'])
                result.extend(['-preset', 'veryfast'])
                #result.extend(['-quality', 'good'])
                #result.extend(['-speed', '4'])
                result.extend(['-threads', '4'])
                # variable bitrate (on average, higher value -> better quality): -b:v 1M
                # constant quality (value from 4-63, lower -> better quality): -crf 10
                # constant bitrate (all values must be the same): -minrate 1M -maxrate 1M -b:v 1M
                # --best
                # --good
                # --rt
                # --cpu-used
            elif config['format'] == 'mp4':
                result.extend(['-c:v', 'libx264'])
                result.extend(['-preset', 'veryfast'])
            #-vcodec libvpx -crf 10 -preset veryfast -b:v 1M -acodec libvorbis "${name}".webm;
            #ffmpeg -i half1.mp4 -filter:v scale="trunc(oh*a/2)*2:144" -an half1.144p.an.mp4
        if 'height' in config:
            result.extend(['-filter:v', 'scale=trunc(oh*a/2)*2:'+str(config['height'])+''])
        if 'muted' in config:
            # mute the converted videos
            if config['muted']:
                result.append('-an')
        
        return result


class ThumbnailConverter(Converter):

    def _filterConfig(self, config):
        return [conf for conf in config if 'format' in conf and conf['format'] in ['jpg', 'png']]
    
    def _prepareAnalyze(self):
        formats = set([f['format'] for f in self.config])
        files = []
        for fmt in formats:
            for f in glob.glob(self.video.getKey() + '.*.' + fmt):
                info = ffmpeg.getMediaInfo(f)
                if 'format' not in info:
                    info['format'] = []
                if fmt not in info['format']:
                    info['format'].append(fmt)
                files.append(info)
        return files

    def _config2ffmpeg(self, config):
        """Translates the given configuration to ffmpeg arguments."""
        result = ['-vframes', '1']
        if 'height' in config and 'width' not in config:
            result.extend(['-filter:v', 'scale=-1:'+str(config['height'])+''])
        elif 'width' in config and 'height' not in config:
            result.extend(['-filter:v', 'scale='+str(config['width'])+':-1'])
        elif 'height' in config and 'width' in config:
            result.extend(['-filter:v', 'scale='+str(config['width'])+':'+str(config['height'])+''])
        return result


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
        self.files = [{
            'filename': file,
            'extension': m.group('ext').lower(),
            'config': self._parseConfig(m.group('config'))
        }]
    
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
    
    @staticmethod
    def _parseConfig(string):
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
        return set([f['extension'] for f in self.files if 'extension' in f])
    
    def getHeights(self):
        """Returns the available resolutions (heights) in this VideoFile."""
        return set([f['height'] for f in self.files if 'height' in f])
    
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
    """Wrapper class for executing FFMpeg."""
    
    def __init__(self, ffmpeg_path='ffmpeg', ffprobe_path='ffprobe'):
        """Initizialzes FFMpeg class and searches for the ffmpeg/ffprobe exceutables."""
        # check 'ffmpeg'
        ffmpeg_path = self.which(ffmpeg_path) if '/' not in ffmpeg_path else ffmpeg_path
        try:
            # try to execute ffmpeg and catch exceptions if it doesn't work!
            version = subprocess.check_output([ffmpeg_path, '-version'], stderr=subprocess.STDOUT)
            self.ffmpeg_path = ffmpeg_path
            getLogger().info('Using ffmpeg:%s', ffmpeg_path)
        except Exception as e:
            getLogger().error('Couldn\'t find ffmpeg!')
            self.ffmpeg_path = None
        # check 'ffprobe'
        ffprobe_path = self.which(ffprobe_path) if '/' not in ffprobe_path else ffprobe_path
        try:
            # try to execute ffprobe and catch exceptions if it doesn't work!
            version = subprocess.check_output([ffprobe_path, '-version'], stderr=subprocess.STDOUT)
            self.ffprobe_path = ffprobe_path
            getLogger().info('Using ffprobe:%s', ffprobe_path)
        except Exception as e:
            getLogger().error('Couldn\'t find ffprobe!')
            self.ffprobe_path = None

    @staticmethod
    def which(name):
        """Tries to locate the named executable.
        
        Therefore the 'which' program is used (on unix systems), otherwise the 
        environment PATH is checked if the executable can be found there.
        """
        getLogger().info('Searching for %s executable', name)
        try:
            # try to use 'which' program (on unix systems) ...
            return subprocess.check_output(['which', name]).strip()
        except:
            # ... if it fails, search envirnment PATH for the executable
            path = os.environ.get('PATH', os.defpath)
            for d in path.split(':'):
                fpath = os.path.join(d, name)
                if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                    return fpath
        # if nothing was found, return the given executable name, maybe there's an alias defined and so still callable!?
        return name
    
    def isValid(self):
        """Returns 'True' if both paths (ffmpeg/ffprobe) are set, 'False' otherwise."""
        return self.ffmpeg_path is not None and self.ffprobe_path is not None
    
    def getMediaInfo(self, file):
        """Retrieves some infos of the given (media/video) file and returns it in a defined format."""
        info = {}
        try:
            # loading media info with ffprobe as json
            data = subprocess.check_output([self.ffprobe_path, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', file], stderr=subprocess.STDOUT)
            # TODO: check result on error?!?
            js = json.loads(data)
            # set the infos
            info['filename'] = js['format']['filename']
            info['size'] = int(js['format']['size'])
            info['duration'] = float(0 if 'duration' not in js['format'] else js['format']['duration'])
            info['bitrate'] = int(0 if 'bit_rate' not in js['format'] else js['format']['bit_rate'])
            info['format'] = js['format']['format_name'].split(',')
            for stream in js['streams']:
                # only interessted in video streams
                if stream['codec_type'] == 'video':
                    # log multiple video streams
                    if 'width' in info:
                        getLogger().debug('There seems to more than one video stream in the file (%s)', file)
                    info['width'] = stream['width']
                    info['height'] = stream['height']
                elif stream['codec_type'] == 'audio':
                    info['muted'] = False
            # set muted, if the file doesn't contain an audio stream
            if 'muted' not in info:
                info['muted'] = True
        except Exception, e:
            getLogger().error('An error occurred parsing file info (%s): %s', file, e)
        return info
    
    def convert(self, infile, outfile, params, timeout=10):
        """Converts the given input file 'infile' into the ouput file 'outfile' with the given configuration 'params'.
        
        The ffmpeg command is created with the given configuration and executed in its own subprocess. This script 
        reads the ffmpeg output and displays the progress. If ffmpeg doesn't send any data for 'timeout' seconds, it is
        assumed 'ready' and the progess loop is quited. At the end the return code of ffmpeg is check in order to 
        report any errors.
        
        infile  - the video file which should be converted
        outfile - the name of the converted file
        params  - the configuration, a list with valid ffmpeg options
        timeout - the max. time (in seconds) before ffmpeg assumed 'dead' or not accessible
        """
        # make sure the file exists
        if not os.path.exists(infile):
            getLogger().error('File doesn\'t exists!')
            return False
        
        # prepare ffmpeg command and arguments
        cmds = [self.ffmpeg_path, '-i', infile]
        cmds.extend(params)
        cmds.extend(['-y', outfile])
        
        def on_sigint(*_):
            """Internal function handler for the SIGINT signal.
            Used for cleanup and shutdown gracefully.
            """
            if p is not None:
                # send SIGTERM to ffmpeg
                p.terminate()
                # set alarm off
                signal.alarm(0)
                # unregister handler for alarm signal
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                # show info
                getLogger().error('\nWaiting for ffmpeg to exit ...')
                # wait 'till ffmpeg exits
                p.communicate()
                # try to remove incomplete output file
                if os.path.exists(outfile) and os.path.isfile(outfile):
                    try:
                        os.remove(outfile)
                    except Exception:
                        pass
            raise Exception('interrupted!')
        
        # register SIGINT handler
        signal.signal(signal.SIGINT, on_sigint)
        
        # timeout needs to be positive
        if timeout:
            def on_sigalrm(*_):
                """Internal function handler for the ALARM signal.
                If ffmpeg doesn't respond after 'timeout' secends, an exception is raised.
                """
                # after calling the singal, reset alarm signal -> unregister handler
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                raise Exception('timed out while waiting for ffmpeg')
            # set the alarm handler to the signal
            signal.signal(signal.SIGALRM, on_sigalrm)
        
        try:
            # start ffmpeg subprocess
            getLogger().debug('Spawning ffmpeg with command: ' + ' '.join(cmds))
            p = subprocess.Popen(cmds, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
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
                # only interested in the progress
                if 'frame' == line[0:5]:
                    # show progress ...
                    print "\r%s" % line,
                    # the 'flush' is needed, otherwise the output buffer would be never or randomly flushed
                    # 'cause the previous data is always deleted '\r'!
                    sys.stdout.flush()
        
        if timeout:
            # unregister alarm signal handler
            signal.signal(signal.SIGALRM, signal.SIG_DFL)

        # wait for ffmpeg to exit
        p.communicate()
        
        # unregister SIGINT signal handler
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        # check return code
        if p.returncode != 0:
            # TODO: use logger or throw exception?!
            print 'Exited with code %d' % p.returncode
            print buffer


# TODO: add "pre-configuration" flag -> don't ask any questions!
def getArguments():
    # retrieve script arguments
    args = sys.argv[1:]
    # create namespace for argument parser
    ns = argparse.Namespace()

    # helper function for setting verbosity level
    def setVerboseLevel(name):
        """Helper function for handling verbosity level."""
        try:
            # if the following argument is an integer, use it as verbosity level
            level=int(args[args.index(name) + 1])
            # ... and remove it, otherwise argparse throws an exception/error
            args.pop(args.index(name) + 1)
        except ValueError:
            # cannot parse verbosity level - nothing was set, use default!
            level = 30  #logging.WARNING
        setattr(ns, 'level', level)
    # if 'verbose' is set, try to get level
    if '-v' in args or '--verbose' in args:
        setVerboseLevel('-v' if '-v' in args else '--verbose')
    
    """Parses the given script arguments."""
    parser = argparse.ArgumentParser(description='TODO ...') # TODO ...
    parser.add_argument('-v', '--verbose', 	action='store_true', help='sets the verbosity level to "WARNING". An optional verbosity level could be set, to explicitly define the verbosity level. Higher number means only displaying higher severity. Example: "-v 10" is the DEBUG level and "-v 50" is CRITICAL')
    parser.add_argument('--ffmpeg', action='store', default='ffmpeg', help='set the path to the ffmpeg executable.')
    parser.add_argument('--ffprobe', action='store', default='ffprobe', help='set the path to the ffprobe executable.')
    parser.add_argument('source', action='store', help='video file or directory with video files, which should be converted.')
    
    return parser.parse_args(args, ns)

def getLogger(suffix=None):
    """Helper function for retrieving the logger instance."""
    return logging.getLogger(os.path.splitext(os.path.basename(__file__))[0]+('.'+suffix if suffix is not None else ''))

def question(string, short, options):
    """User interaction function for asking questions with a defined set of answers."""
    choice = raw_input(string)
    # ask again, if answer was 'incorrect'
    while choice.lower() not in options:
        choice = raw_input(short)
    # return answer
    return choice

def searchVideoFiles(path):
    """Searches a given path recursively for video files."""
    assert os.path.isdir(path), 'Not a directoy!'
    result = {}
    # only interested in videos
    filter = re.compile('video/.*')
    mimetypes.init() # do we need this?!
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            f = os.path.join(dirpath, filename)
            # filter video files
            if mimetypes.guess_type(f)[0] is not None and filter.match(mimetypes.guess_type(f)[0]):
                # create VideoFile object
                video = VideoFile(f)
                # check if we already got this video
                if video.getKey() in result:
                    # add the 'new' file to the existing VideoFile object
                    result[video.getKey()].add(video)
                else:
                    # this is new
                    result[video.getKey()] = video
    # return the found VideoFiles
    return result

def createTodoList(path, formats, prefix=None):
    """Creates a list with VideoConverter objects, which needs something to convert."""
    path = os.path.abspath(path)  # make sure we got abs. path
    todo = []
    # search files
    files = searchVideoFiles(path)
    # filter VideoFiles not matching given prefix
    if prefix is not None:
        files = {k: v for k, v in files.iteritems() if k==prefix}
    # iterate over VideoFiles and collect converting todos
    for f in files:
        # analyze video files
        files[f].analyze()
        # setup converter, every converter needs its own format configuration!
        converter = VideoConverter(files[f], copy.deepcopy(formats))
        thm_converter = ThumbnailConverter(files[f], copy.deepcopy(formats))
        # something todo?
        if converter.getTodo():
            todo.append(converter)
        if thm_converter.getTodo():
            todo.append(thm_converter)
    
    return todo


if __name__ == "__main__":
    # parse arguments
    args = getArguments()
    
    # setup logger
    logging.basicConfig(level=args.level if args.verbose else logging.ERROR )
    
    # setup ffmpeg wrapper class
    ffmpeg = FFMpeg(args.ffmpeg, args.ffprobe)
    if not ffmpeg.isValid():
        exit(1)
    
    formats = [ {'format': 'mp4',  'height': 144, 'muted':True},
                {'format': 'webm', 'height': 144, 'muted':True},
                {'format': 'mp4',  'height': 240, 'muted':True},
                {'format': 'webm', 'height': 240, 'muted':True},
                {'format': 'mp4',  'height': 360, 'muted':True},
                {'format': 'webm', 'height': 360, 'muted':True},
                {'format': 'mp4',  'height': 480, 'muted':True},
                {'format': 'webm', 'height': 480, 'muted':True},
                {'format': 'mp4',  'height': 720, 'muted':True},
                {'format': 'webm', 'height': 720, 'muted':True},
                {'format': 'jpg', 'height': 500},
                {'format': 'jpg', 'width': 500, 'height': 300},
                {'format': 'jpg', 'width': 500},
                {'format': 'png', 'height': 400,},]
                
    todo_list = []
    
    if os.path.isfile(args.source):
        getLogger().info('Analyzing file')
        # we need to search the whole directory to find all files of this video!
        f = os.path.abspath(args.source)  # needing abs. path
        todo_list = createTodoList(os.path.dirname(f), formats, os.path.splitext(f)[0])
    elif os.path.isdir(args.source):
        getLogger().info('Analyzing directory')
        # find converting todos
        todo_list = createTodoList(args.source, formats)
    else:
        getLogger().error('Source is neither file nor directory ("%s").', args.source)
        exit(0)

    if not todo_list:
        print 'Nothing to do!'
        exit(0)
    
    print 'The following would be converted:'
    for i in todo_list:
        print '  - ', i
    
    choice = question("\nHow to continue? (cancel [C], convert all [A], ask every file [F], ask every format configuration [M]\n-> ", "[C,A,F,M]-> ", ['c','a','f','m'])
    
    if choice.lower() == 'c':
        exit()
    else:
        # TODO: catch exceptions!
        for video in todo_list:
            print '\n', video.video.source
            if choice.lower() == 'f':
                file_choice = question("\nProceed converting? [Y]es, [S]kip, [C]ancel -> ", "[Y,S,C]-> ", ['c','s','y'])
                if file_choice.lower() == 's':
                    continue
                elif file_choice.lower() == 'c':
                    break
            for todo in video.getTodo():
                if choice.lower() == 'm':
                    config_choice = question("\nContinue with configuration: "+str(todo)+"?\n[Y]es, [S]kip config, skip [F]ile, [C]ancel all -> ", "[Y,S,F,C]-> ", ['y','s','f','c'])
                    if config_choice.lower() == 's':
                        continue
                    elif config_choice.lower() == 'f':
                        break
                    elif config_choice.lower() == 'c':
                        exit(0)
                print '\nprocess config ', todo
                video.convert(todo)
