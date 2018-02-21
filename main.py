#!/home/nemecle/anaconda3/bin/python3.6
"""
Gallery generation
"""

import json
import os
import jinja2
import pprint

from multiprocessing import Pool
from PIL import Image



#Jinja decoding issues
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

IMAGE_DIR = "/home/nemecle/transit/ne_art/pythim/export/img/"
HTML_DIR = "/home/nemecle/transit/ne_art/pythim/export/html/"
THUMB_DIR = "/home/nemecle/transit/ne_art/pythim/export/thumbnails/"
THUMB_SIZE = 500
CONFIG_FILE = "galleries.json"


def get_directory_tree(path):
    """
    Return a list of files in given folder with hierarchy preserved

    path -- path to list

    """

    file_list = []

    for dir_, _, files in os.walk(path):
        for filen in files:
            relative_path = os.path.relpath(dir_, path)
            file_list.append(os.path.join(relative_path, filen))
    # print("(get_directory_tree) returning {}".format(str(file_list)))
    return file_list


def thumbnail(img, directory): 
    """
    create a thumbnail for a given img and store in directory

    """

    filename = img.split("/")[-1]
    print("thumbnailing {} to {}".format(filename, directory))
    try:
        print("opening")
        image = Image.open(img)

        print("thumbnail'd")
        image.thumbnail((THUMB_SIZE,THUMB_SIZE), Image.NEAREST)

        print("saved")
        image.save(directory + filename)

        return 0

    except Exception as e: 
        print("(thumbnail) " + str(e))


def main():
    """
    generate gallery based on configuration file.

    """

    files = get_directory_tree(IMAGE_DIR)
    # pprint.pprint(str(files))
    data = json.load(open(CONFIG_FILE))

    model = open("home.html")
    template = jinja2.Template(model.read())


    # for f in files:
    #     thumbnail(IMAGE_DIR + f, THUMB_DIR)



    data = data[0]
    galleries = data["galleries"]

    name_to_path = {}

    for name, gallery in galleries.items():
        name_to_path[name] = gallery["dir"]

    for name, gallery in galleries.items():

        list_imgs = []
        list_subs = []

        #build name <-> path list for sub galleries
        for sub in gallery["subgal"]:
            list_subs.append((galleries[sub]["name"], HTML_DIR + sub + ".html"))


            
        print("=============")

        list_imgs = get_directory_tree(IMAGE_DIR + gallery["dir"])
        list_imgs = [IMAGE_DIR + gallery["dir"] + "/" + s for s in list_imgs]
        list_imgs = [THUMB_DIR + s.split("/")[-1] for s in list_imgs]

        dir_tree = gallery["dir"].split("/")[:-1]

        path = []
        for direc in dir_tree: # building breadcrumb links
            path.append((direc, HTML_DIR + direc + ".html"))

        print("length of path: {}".format(len(path)))

        print("number of files: {}".format(len(list_imgs)))
        gallery_content = template.render(name=gallery["name"], files=list_imgs, path=path, subs=list_subs)


        # os.makedirs(os.path.dirname("export/" + str(gallery["dir"]) + ".html"), exist_ok=True)
        file = open(HTML_DIR + name + ".html","w")
        file.write(gallery_content)
        file.close()
        print("created file " + str("export/") + str(gallery["dir"]) + ".html")

    return


if __name__ == '__main__':
    main()
