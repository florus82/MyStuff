import os
import pandas as pd
import math

def getFilelist(originpath, ftyp):
    files = os.listdir(originpath)
    out   = []
    for i in files:
        if i.split('.')[-1] in ftyp:
            if originpath.endswith('/'):
                out.append(originpath + i)
            else:
                out.append(originpath + '/' + i)
        # else:
        #     print("non-matching file - {} - found".format(i.split('.')[-1]))
    return out


# zip folder
allZips = getFilelist('X:/MSc_outside_Seafile/RS_Data/S1/Raw', '.zip')

# works only if all the chunks have the sime size!!!!!!!!!!!!!
chunks = int(math.floor(float(len(allZips)) / 35))

chunkList = [allZips[i:i+chunks] for i in range(0,len(allZips),chunks)]


# export into scenelists
for i, scenes in enumerate(chunkList):
    df = pd.DataFrame(scenes, columns = ['col'])
    df.to_csv('X:/MSc_outside_Seafile/RS_Data/S1/Raw/scencelists/sceneList_' + str(i) + '.csv', index = False, header = False)

