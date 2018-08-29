#!/usr/bin/bash

ignore_dest=false

while getopts "hf" opt; do
  case  $opt in
    h)
      echo "usage: combine [OPTIONS] SOURCE1 SOURCE2... DEST"
      echo "-h : this help"
      echo "-f : ignore existing DEST"
      echo "NOTE: all files MUST have the same streams (same codecs, same time base, etc.)."
      exit 0
      ;;
    f) 
      ignore_dest=true
      ;;
  esac
done

# remove parsed getopts arguments from input list
shift $((OPTIND-1))

if [ $# -lt 3 ]; then
  echo "ERROR: there are at least 2 source files and one destination file needed"
  exit 3
fi

# create temporay file and ensure clean up with a trap
tmpfile=$(mktemp)
trap 'rm "$tmpfile"' 0

#determine target file
for i in $@; do :; done
target_file=$i

if [ "$ignore_dest" = false -a -f $target_file ]; then
  echo "ERROR: target file $target_file exists"  
  exit 2
fi

# store the absolute path of all input files into tmpfile as list
for var in "$@"
do
  if [ ! -f $var ]; then
      echo "ERROR: file $var doesn't exist" 
      exit 1
  fi

  if [ $var != $target_file ]; then
	  echo "file '$(realpath $var)'" >> $tmpfile
  fi
done

# do concatenation of files listed in tmpfile on stream level and copy them int target_file
# all files must have the same streams (same codecs, same time base, etc.).
# -y        : overwrite output files without asking
# -f concat : use virtual concatenation script demuxer
# -safe 0   : enable absolute paths
# -c copy   : prevent reencoding
ffmpeg -y -f concat -safe 0 -i $tmpfile -c copy $target_file > ffmpeg.log 2> ffmpeg_err.log
