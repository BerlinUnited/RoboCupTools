#!/usr/bin/python3
import sys
import os
import shutil

# simplify matching during file-game-matching with a unique list of characteristic names for each team
search_keys = {
    'AstroNAOtas'         : ['astro'],
    'Aztlan'              : ['aztlan'],
    'B-Human'             : ['human'],
    'B-Swift'             : ['b-swift'],
    'Bembelbots'          : ['bembel'],
    'Berlin United'       : ['berlin'],
    'Camellia Dragons'    : ['dragon'],
    'DoBerMan'            : ['doberman'],
    'Dutch Nao Team'      : ['dutch'],
    'HULKs'               : ['hulk'],
    'MiPal'               : ['mipal'],
    'NTU RoboPAL'         : ['ntu'],
    'Nao Devils Dortmund' : ['devils'],
    'Nao-Team HTWK'       : ['htwk'],
    'Naova EST'           : ['naova'],
    'NomadZ'              : ['nomadz'],
    'Rinobot'             : ['rino'],
    'SPQR'                : ['spqr'],
    'TJArk'               : ['tjark'],
    'Team-Team'           : ['team-team'],
    'UChile'              : ['uchile'],
    'UPennalizers'        : ['upenn'],
    'UT Austin Villa'     : ['austin'],
    'UnBeatables'         : ['beat'],
    'rUNSWift'            : ['unsw']
}

# requried for easier construction of the games list
day = [
        '2018-06-18',
        '2018-06-19',
        '2018-06-20',
        '2018-06-21'
      ]

# requried for easier construction of the games list
slot = {
        '09' : ['09-00-00', '09-15-00', '09-30-00', '09-45-00'],
        '10' : ['10-00-00', '10-15-00', '10-30-00', '10-45-00'],
        '11' : ['11-00-00', '11-15-00', '11-30-00', '11-45-00'],
        '12' : ['12-00-00', '12-15-00', '12-30-00', '12-45-00'],
        '13' : ['13-00-00', '13-15-00', '13-30-00', '13-45-00'],
        '14' : ['14-00-00', '14-15-00', '14-30-00', '14-45-00'],
        '15' : ['15-00-00', '15-15-00', '15-30-00', '15-45-00'],
        '16' : ['16-00-00', '16-15-00', '16-30-00', '16-45-00'],
        '17' : ['17-00-00', '17-15-00', '17-30-00', '17-45-00'],
        '18' : ['18-00-00', '18-15-00', '18-30-00', '18-45-00'],
        '19' : ['19-00-00', '19-15-00', '19-30-00', '19-45-00']
       }

games = [
        # e.g. ('2018-06-18','15-00-00','Team1','Team2'),
        (day[0], slot['09'][0], 'Bembelbots','UnBeatables'),
        (day[0], slot['09'][0], 'B-Human','UPennalizers'),
        (day[0], slot['09'][2], 'MiPal','NTU RoboPAL'),
        (day[0], slot['10'][0], 'UT Austin Villa','HULKs'),
        (day[0], slot['10'][2], 'Nao Devils Dortmund','UChile'),
        (day[0], slot['11'][0], 'Dutch Nao Team','Aztlan'),
        (day[0], slot['11'][0], 'Nao-Team HTWK','Camellia Dragons'),
        (day[0], slot['11'][2], 'TJArk','UPennalizers'),
        (day[0], slot['12'][0], 'Bembelbots','SPQR'),
        (day[0], slot['12'][2], 'MiPal','Rinobot'),
        (day[0], slot['13'][0], 'HULKs','Berlin United'),
        (day[0], slot['13'][0], 'Nao Devils Dortmund','NomadZ'),
        (day[0], slot['13'][2], 'rUNSWift','Camellia Dragons'),
        (day[0], slot['14'][0], 'Dutch Nao Team','Naova EST'),
        (day[0], slot['14'][2], 'B-Human','TJArk'),
        (day[0], slot['15'][0], 'UChile','NomadZ'),
        (day[0], slot['15'][0], 'UT Austin Villa','Berlin United'),
        (day[0], slot['15'][2], 'UnBeatables','SPQR'),
        (day[0], slot['16'][0], 'Nao-Team HTWK','rUNSWift'),
        (day[0], slot['16'][2], 'Aztlan','Naova EST'),
        (day[0], slot['17'][0], 'NTU RoboPAL','Rinobot'),
        (day[0], slot['17'][2], 'DoBerMan','Team-Team'),
        (day[0], slot['18'][0], 'B-Swift','AstroNAOtas'),

        (day[1], slot['09'][0], 'UPennalizers','Bembelbots'),
        (day[1], slot['09'][0], 'UChile','NTU RoboPAL'),
        (day[1], slot['09'][3], 'UT Austin Villa','Naova EST'),
        (day[1], slot['09'][3], 'Camellia Dragons','SPQR'),
        (day[1], slot['10'][3], 'AstroNAOtas','Team-Team'),
        (day[1], slot['10'][3], 'B-Swift','DoBerMan'),
        (day[1], slot['12'][0], 'Rinobot','Aztlan'),
        (day[1], slot['12'][2], 'UPennalizers','MiPal'),
        (day[1], slot['12'][2], 'B-Human','HULKs'),
        (day[1], slot['13'][0], 'rUNSWift','UT Austin Villa'),
        (day[1], slot['13'][2], 'TJArk','UChile'),
        (day[1], slot['14'][0], 'Naova EST','UnBeatables'),
        (day[1], slot['14'][0], 'Nao-Team HTWK','NomadZ'),
        (day[1], slot['14'][2], 'Camellia Dragons','Aztlan'),
        (day[1], slot['15'][2], 'UPennalizers','Rinobot'),
        (day[1], slot['15'][2], 'Nao Devils Dortmund','rUNSWift'),
        (day[1], slot['16'][0], 'HULKs','SPQR'),
        (day[1], slot['16'][2], 'Naova EST','Dutch Nao Team'),
        (day[1], slot['17'][0], 'Berlin United','TJArk'),
        (day[1], slot['17'][2], 'MiPal','Aztlan'),
        (day[1], slot['18'][0], 'NomadZ','Bembelbots'),
        (day[1], slot['18'][2], 'NTU RoboPAL','Dutch Nao Team'),
        (day[1], slot['18'][2], 'Camellia Dragons','Rinobot'),
        (day[1], slot['19'][2], 'DoBerMan','AstroNAOtas'),
        (day[1], slot['19'][2], 'B-Swift','Team-Team'),

        (day[2], slot['09'][0], 'B-Human','SPQR'),
        (day[2], slot['09'][2], 'Nao-Team HTWK','Bembelbots'),
        (day[2], slot['10'][0], 'Nao Devils Dortmund','UT Austin Villa'),
        (day[2], slot['10'][2], 'Berlin United','UChile'),
        (day[2], slot['11'][0], 'NTU RoboPAL','UnBeatables'),
        (day[2], slot['11'][2], 'Camellia Dragons','MiPal'),
        (day[2], slot['12'][2], 'UPennalizers','Aztlan'),
        (day[2], slot['13'][0], 'Nao Devils Dortmund','Bembelbots'),
        (day[2], slot['13'][2], 'NomadZ','UT Austin Villa'),
        (day[2], slot['14'][0], 'HULKs','UChile'),
        (day[2], slot['14'][2], 'Berlin United','SPQR'),
        (day[2], slot['15'][0], 'Rinobot','MiPal'),
        (day[2], slot['15'][2], 'Dutch Nao Team','UnBeatables'),
        (day[2], slot['16'][0], 'Camellia Dragons','UPennalizers'),
        (day[2], slot['16'][2], 'NTU RoboPAL','Naova EST'),
        (day[2], slot['17'][0], 'TJArk','UT Austin Villa'),
        (day[2], slot['17'][2], 'rUNSWift','HULKs'),
        (day[2], slot['18'][0], 'Nao-Team HTWK','Berlin United'),
        (day[2], slot['18'][2], 'B-Human','Nao Devils Dortmund'),
        (day[2], slot['19'][0], 'UPennalizers','Naova EST'),
        (day[2], slot['19'][2], 'NTU RoboPAL','Camellia Dragons')

        #day[3] not required
        ]

# create the base folder name based on a game tuple
def get_base_folder_name(game):
    return (game[0] +'_' + game[1] + '_' + game[2] + '_vs_' + game[3] + '_' + 'half1',
            game[0] +'_' + game[1] + '_' + game[2] + '_vs_' + game[3] + '_' + 'half2')

# creates a stub folder structure under dest for a game tuple
def create_rudimentary_structure(dest, game):
    game_folder = get_base_folder_name(game)
    if os.path.exists(dest + '/' + game_folder[0]):
        print('Warning: folder ' + game_folder[0] + ' already exists ...')

    for gf in game_folder:
        os.makedirs(dest + '/' + gf + '/extracted', exist_ok = True)
        os.makedirs(dest + '/' + gf + '/gc_logs', exist_ok = True)
        os.makedirs(dest + '/' + gf + '/videos', exist_ok = True)
        if not os.path.exists(dest + '/' + gf + '/videos/external_resources'):
            f = open(dest + '/' + gf + '/videos/external_resources','w+')
            f.write('TODO: add links to youtube or other platforms here')
            f.close()
        if game[2] == 'Berlin United' or game[3] == 'Berlin United':
            os.makedirs(dest + '/' + gf + '/game_logs', exist_ok = True)

    return True

# checks it the candidate file belongs to game by checking the date first and then for characteristic names for each team in file name
def candiate_matches(candidate, game):
    if game[0] in candidate:
        try:
            if all(x in candidate.casefold() for x in search_keys[game[2]]) and all(x in candidate.casefold() for x in search_keys[game[3]]):
                return True
        except KeyError as e:
            print("Error: can't get search key for team " + str(e), file=sys.stderr)
    return False

# test if candidate matches and moves file if it does
def found_candidate(c, dest, game):
    c_folder = c[0]
    c_file   = c[1]
    if candiate_matches(c_file, game):
        if '1st' in c_file:
            half = get_base_folder_name(game)[0]
        elif '2nd' in c_file:
            half = get_base_folder_name(game)[1]
        else:
            print('Error: ' + c_file + ' in ' + c_folder + ' has no half', file=sys.stderr)
            return False

        src = os.path.join(c_folder, c_file)
        d   = os.path.join(dest, half,  'gc_logs', c_file)
        print("move " + src + " to " + d)
        shutil.move(src, d)
        return True
    return False

# iterates over the list of candidates and removes any matching one
def find_gc_logs(candidates, dest, game):
    n_before = len(candidates) 
    candidates[:] = [c for c in candidates if not found_candidate(c, dest, game)]
    if n_before == len(candidates):
        print("Warning: couldn't find a gc log for " + game[2] + ' vs ' + game[3])

# iterates over the list of candidates and removes any matching one
def find_gc_json_logs(candidates, dest, game):
    n_before = len(candidates) 
    candidates[:] = [c for c in candidates if not found_candidate(c, dest, game)]
    if n_before == len(candidates):
        print("Warning: couldn't find a gc_json log for " + game[2] + ' vs ' + game[3])

# checks it the candidate file belongs to game by checking the date first and then for characteristic names for each team in file name
def played_vs(candidate, date, opponent):
    if date not in candidate:
        return False
    try:
        if all(x in candidate.casefold() for x in search_keys[opponent]) and 'Test'.casefold() not in candidate.casefold():
            return True
    except KeyError as e:
        print("Error: can't get search key for team " + str(e), file=sys.stderr)
    return False

def rename_and_move(src, dst):
    log_folders = [d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d))]
    log_folders = map(lambda x: os.path.join(src,x), log_folders)

    # parse nao info
    for f in log_folders:
        player_number = None
        body = None
        head = None
        with open(f+'/nao.info') as naoinfo:
            for line in naoinfo:
                if 'playerNumber' in line:
                    player_number = line[-2]
                    continue
                if 'Nao' in line and not 'TH' in line:
                    body = line[:-1]
                    continue
                if 'Number' in line:
                    head = line[line.find('=')+1:-1]
                    continue

        if player_number and body and head:
            d = os.path.join(dst, player_number + '_' + head + '_' + body)
            print("move " + f + " to " + d)
            shutil.move(f, d)
    try:
        os.removedirs(src)
    except OSError as e:
        print("Error: couldn't delete folder " + str(e) + ". Directory not empty.", file=sys.stderr)

def find_game_logs(candidates, dest, game):
    if game[2] not in ('Berlin United','DoBerMan'):
        opponent = game[2]
    else:
        opponent = game[3]

    cs = [c for c in candidates if played_vs(c, game[0], opponent)]

    if not cs:
        print("Error: couldn't find a folder for a game vs " + opponent + " on " + game[0], file=sys.stderr)
        return

    if len(cs) > 1:
        print("Error: couldn't find unique folder for a game vs " + opponent + " on " + game[0], file=sys.stderr)
        print("Candidates are:", file=sys.stderr)
        for c in cs:
            print(c, file=sys.stderr)
        return

    game_folder = get_base_folder_name(game)

    if os.path.exists(cs[0] + '/half1'):
        rename_and_move(cs[0] + '/half1', dest + '/' + game_folder[0] + '/game_logs')
    if os.path.exists(cs[0] + '/half2'):
        rename_and_move(cs[0] + '/half2', dest + '/' + game_folder[1] + '/game_logs')

    candidates.remove(*cs)

def main():
    # check for correct and enough input arguments
    if (len(sys.argv) < 3):
        print("Error: not enough arguements", file=sys.stderr)
        sys.exit(1)
    if (len(sys.argv) > 3):
        print("Error: too much arguements", file=sys.stderr)
        sys.exit(2)
    if not os.path.exists(sys.argv[1]):
        print("Error: source directory doesn't exists", file=sys.stderr)
        sys.exit(3)
    if not os.path.exists(sys.argv[2]):
        print("Warning: target directory doesn't exist")
        print("creating target directory")
        os.makedirs(sys.argv[2])

    src  = sys.argv[1]
    dest = sys.argv[2]

    # get all teamcoms files
    gc_src_candidates = []
    for root, folders, files in  os.walk(src + '/logs_teamcomm'):
        for f in files:
            gc_src_candidates.append((root,f))

    # get all teamcom files in json format
    gc_json_src_candidates = []
    for root, folders, files in  os.walk(src + '/logs_teamcomm_json'):
        for f in files:
            gc_json_src_candidates.append((root,f))

    # get all folders for game logs
    game_log_src_folders = [d for d in os.listdir(src+'/game_logs') if os.path.isdir(os.path.join(src+'/game_logs', d))]
    game_log_src_folders = list(map(lambda x: os.path.join(src,'game_logs',x), game_log_src_folders))

    for game in games:
        create_rudimentary_structure(dest, game)

        find_gc_logs(gc_src_candidates, dest, game)
        find_gc_json_logs(gc_json_src_candidates, dest, game)

        if game[2] in ('Berlin United','DoBerMan') or game[3] in ('Berlin United','DoBerMan'):
            find_game_logs(game_log_src_folders, dest, game)

    print("Note: couldn't find a game for following gc_logs:")
    for c in gc_src_candidates:
        print(os.path.join(*c))

    print("Note: couldn't find a game for following gc_json_logs:")
    for c in gc_json_src_candidates:
        print(os.path.join(*c))

    print("Note: couldn't find a game for following game log folders:")
    for c in game_log_src_folders:
        print(c)


if __name__ == "__main__":
        main()
