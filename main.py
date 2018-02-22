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


## test config
# CONFIG_FILE = "galleries.json"

# BASE_DIR  = "export/html/"
# HTML_DIR  = BASE_DIR + ""
# IMAGE_DIR = "img/"
# THUMB_DIR = "thumbnails/"

CONFIG_FILE = "nem.json"

BASE_DIR  = "export/html/"
HTML_DIR  = BASE_DIR + ""
IMAGE_DIR = "img/"
THUMB_DIR = "thumbnails/"



GENERATE_THUMBNAILS = False
THUMB_SIZE = 1000


def get_directory_tree(path):
    """
    Return a list of files in given folder with hierarchy preserved

    path -- path to list

    """

    file_list = []

    try:
        os.stat(path)
    except:
        print("(get_directory_tree) {} does not exist.".format(path))

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


    if GENERATE_THUMBNAILS:
        for f in files:
            thumbnail(IMAGE_DIR + f, BASE_DIR + THUMB_DIR)



    data = data[0]
    galleries = data["galleries"]

    name_to_path = {}

    for name, gallery in galleries.items():
        name_to_path[name] = gallery["dir"]

    for name, gallery in galleries.items():

        print("=============")
        print("building: {}".format(name))

        list_imgs = []
        list_subs = []

        #build name <-> path list for sub galleries
        for sub in gallery["subgal"]:
            list_subs.append((galleries[sub]["name"], sub + ".html"))


            
        print("working with: " + IMAGE_DIR + gallery["dir"])

        list_imgs = get_directory_tree(IMAGE_DIR + gallery["dir"])
        # list_imgs = [IMAGE_DIR + gallery["dir"] + "/" + s for s in list_imgs]
        # list_imgs = [THUMB_DIR + s.split("/")[-1] for s in list_imgs]

        print("number of files: {}".format(len(list_imgs)))


        list_thumbs = [THUMB_DIR + s.split("/")[-1] for s in list_imgs]
        list_imgs = [IMAGE_DIR + gallery["dir"] + "/" + s for s in list_imgs]

        imgs = list(zip(list_thumbs, list_imgs))

        dir_tree = gallery["dir"].split("/")[:-1]

        path = []
        for direc in dir_tree: # building breadcrumb links
            path.append((direc, direc + ".html"))

        gallery_content = template.render(
                                          name=gallery["name"], \
                                          files=imgs, \
                                          path=path, \
                                          subs=list_subs, \
                                          description=gallery["description"] \
                                          )


        # os.makedirs(os.path.dirname("export/" + str(gallery["dir"]) + ".html"), exist_ok=True)
        file = open(HTML_DIR + name + ".html","w")
        file.write(gallery_content)
        file.close()
        print("created file " + HTML_DIR + str(name) + ".html")

    return


if __name__ == '__main__':
    main()
