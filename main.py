#!/home/nemecle/anaconda3/bin/python3.6
"""
Static gallery generation in python
put images in img/ and modify galleries.json

"""

import json
import os
import jinja2
import pprint
import hashlib

from multiprocessing import Pool
from operator import itemgetter
from PIL import Image
from PIL import ExifTags



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

CONFIG_FILE = "galleries.json"
DEFAULT_TEMPLATE = "home.html"

BASE_DIR  = "output/html/"
HTML_DIR  = BASE_DIR + ""
IMAGE_DIR = "img/"
THUMB_DIR = "thumbnails/"



GENERATE_THUMBNAILS = False
THUMB_SIZE = 1000


def get_mtime(path):
    """
    return modification time (mtime)

    """

    return os.stat(path).st_ctime


def get_hash(s):
    """
    return sha256 hash of given string

    """

    return str(int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16) % 10**16)


def get_directory_tree(path):
    """
    Return a list of files in given folder with hierarchy preserved

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


def get_directory_tree_with_time(path):
    """
    Return a list of files with their mtime in given folder with hierarchy preserved
    format: [[<file_path, <mtime>],... ]

    """

    file_list = []

    try:
        os.stat(path)
    except:
        print("(get_directory_tree) {} does not exist.".format(path))

    for dir_, _, files in os.walk(path):
        for filen in files:
            relative_path = os.path.relpath(dir_, path)
            file_path = os.path.join(relative_path, filen)

            file_list.append([file_path, get_mtime(dir_ + "/" + filen)])
    # print("(get_directory_tree) returning {}".format(str(file_list)))
    return file_list



def thumbnail(img, directory): 
    """
    create a thumbnail for a given img and store in directory
    EXIF code:
      https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image/6218425#6218425

    """

    # filename = img.split("/")[-1]
    # print("thumbnailing {} to {}".format(filename, directory))

    try:
        #   print("opening")
        image = Image.open(img)

        for orientation in ExifTags.TAGS.keys() : 
            if ExifTags.TAGS[orientation]=='Orientation' : break

        exif=dict(image._getexif().items())

        if   exif[orientation] == 3 : 
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6 : 
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8 : 
            image=image.rotate(90, expand=True)

    except Exception as e: 
        pass
        # print("(thumbnail) EXIF: " + str(e))

    try:
        #print("thumbnail'd")
        image.thumbnail((THUMB_SIZE,THUMB_SIZE), Image.NEAREST)
        image = image.convert('RGB')

        #print("saved")
        filename = get_hash(img) + ".jpg"
        image.save(directory + filename)

        return 0

    except Exception as e: 
        print("(thumbnail) saving: " + str(e))


def main():
    """
    generate gallery based on configuration file.

    """

    print("working in: " + str(os.getcwd()))

    files = get_directory_tree_with_time(IMAGE_DIR)
    # files = get_directory_tree(IMAGE_DIR)

    data = json.load(open(CONFIG_FILE))


    if GENERATE_THUMBNAILS:
        file_number = len(files)
        for i, (f, t) in enumerate(files):
            # f = f, t # remove mtime
            print("", end="\r")
            print("thumbnails: {}% ({} files processed)".format(int(i * 100/file_number), i), end="\r")
            thumbnail(IMAGE_DIR + f, BASE_DIR + THUMB_DIR)

    print()


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

        if gallery["template"]:
            model = open(gallery["template"])
            template = jinja2.Template(model.read())
        else:
            model = open(DEFAULT_TEMPLATE)
            template = jinja2.Template(model.read())

        #build name <-> path list for sub galleries
        for sub in gallery["subgal"]:
            list_subs.append((galleries[sub]["name"], sub + ".html"))


            
        print("working with: " + IMAGE_DIR + gallery["dir"])
        list_imgs = get_directory_tree_with_time(IMAGE_DIR + gallery["dir"])

        print("number of files: {}".format(len(list_imgs)))

        # list_thumbs = [(THUMB_DIR + s.split("/")[-1], t) for s, t in list_imgs]
        # list_imgs = [(IMAGE_DIR + gallery["dir"] + "/" + s, t) for s, t in list_imgs]


                #THUMB_DIR + s.split("/")[-1], \
        imgs = [ \
                (IMAGE_DIR + gallery["dir"] + "/" + s, \
                get_hash(s) + ".jpg", \
                t)\
        for s, t in list_imgs]

        imgs.sort(key=itemgetter(2))


        #imgs = list(zip(list_thumbs, list_imgs))

        # lb = [x for x in la if not x.startswith(l)]



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
