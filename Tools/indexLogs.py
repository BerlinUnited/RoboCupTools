#!/usr/bin/python

import os
import os.path

from naoth.LogReader import LogReader

import json

if __name__ == "__main__":
    index = {}

    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".log")]:
            f = os.path.join(dirpath, filename)
            
            try: 
                reader = LogReader(f)
            except:
                print('scanning ',f,' failed')
            else:
                for rep in reader.names:
                    if(rep in index.keys()):
                        index[rep].append(f)
                    else:
                        index[rep] = [f]

    with open('index.json','w') as index_file:
        json.dump(index, index_file, indent=4, sort_keys=True)
