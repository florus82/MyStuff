import os

######## ex1 & ex2
stor = '/home/florian/Geodata_with_Python/session2/assign'
path = '/home/florian/Geodata_with_Python/session2/assign/Assignment01_data/Part01_Landsat'

ex1 = []
L_scene = {'L4': 0, 'L5': 0, 'L7': 0, 'L8': 0}

for i1 in os.listdir(path):
    dum = os.listdir(path+"/"+i1)
    v = []
    for i2 in dum:
        v.append(i2[3])  # for exercise 1
        if len(os.listdir(path+"/"+i1+"/"+i2)) > L_scene['L'+i2[3]]:  # get the maximum amount of files per sensor
            L_scene['L'+i2[3]] = len(os.listdir(path+"/"+i1+"/"+i2))  # to compare against to for exercise 2
    ex1.append([i1, v.count(str(4)), v.count(str(5)), v.count(str(7)), v.count(str(8))])  # solution for exercise 1

for i in ex1:
    print(i)

fout = open(stor + '/' + 'ex2.txt', 'w')
for i1 in os.listdir(path):
    for i2 in os.listdir(path + '/' + i1):
        if len(os.listdir(path + "/" + i1 + "/" + i2)) < L_scene['L' + i2[3]]:
            fout.write(path + "/" + i1 + "/" + i2+'\n')
fout.close()

################## ex3

path = '/home/florian/Geodata_with_Python/session2/assign/Assignment01_data/Part02_GIS-Files'

t = []
for a, b, c in os.walk(path):
    for i in c:
        t.append(i.split('.')[-1])
print(t.count('shp'))
print(t.count('tif'))

################## ex4

n = []
for a, b, c in os.walk(path):
    for i in c:
        if i.split('.')[-1] == 'shp':
            n.append(i.split('.')[0])  # check for tif not needed as a tif is all you need


fout = open(stor + '/' + 'ex4.txt', 'w')
for j in n:
    if os.path.isfile(path + '/' + j + '.prj') == False or os.path.isfile(path + '/' + j + '.dbf') == False:
        fout.write(path + '/' + j + '\n')
fout.close()

