#!/home/nemecle/anaconda3/bin/python3.6
"""
Dirty copy of original creation dates (actually, modification date,
due to unix limitations) to img directory)
Copy and paste of python interactive session, might not work as is

"""

import os
from main import get_directory_tree

SOURCE_DIR = "/media/nemecle/DATA/pictbidouille/"
TARGET_DIR = "/home/nemecle/transit/ne_art/pythim/img_t/"

imgs = get_directory_tree(SOURCE_DIR)

files = {}
for i in imgs:
    ctime = os.stat(SOURCE_DIR + i).st_ctime
    # files.append((i.split("/")[-1], ctime))
    files[i.split("/")[-1]] =  ctime

for index, f in enumerate(files):
    img, ti = f
    print("{} {} {}".format(index, img, ti))

i_numb = {}
for f, t in files:
    i_numb[f.split("/")[-1]] = 0

for f, t in files:
    i_numb[f.split("/")[-1]] += 1

dup = {}
for k, v in i_numb.items():
    if v > 1:
        dup[k] = v

s = 0
failed = 0
for f in rec_files:
    try:
        os.utime(TARGET_DIR + f, (files_s[f.split("/")[-1]], files_s[f.split("/")[-1]]))
    except Exception as e:
        print("skipped " + f + ": " + str(e))