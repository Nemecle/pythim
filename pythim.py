#!/home/nemecle/anaconda3/bin/python3.6
# C:\Users\Nemecle\Anaconda3\python.exe
"""
Static gallery generation in python
put images in img/ and modify galleries.json

"""

import json
import os
import jinja2
import pprint
import hashlib
import shutil


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

OUTPUT_DIR = "output/"
# BASE_DIR  = "export/html/"
# HTML_DIR  = BASE_DIR + ""
FILE_DIR = "img/"
IMAGE_DIR = OUTPUT_DIR + "img/"
THUMB_DIR = OUTPUT_DIR + "thumbnails/"
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


def thumbnail(img, directory, force=False):
    """
    create a thumbnail for a given img and store in directory
    EXIF code:
      https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image/6218425#6218425
    """

    # filename = img.split("/")[-1]
    # print("thumbnailing {} to {}".format(filename, directory))

    try:
        #   print("opening")
        image = Image.open(img)

        if os.path.isfile(directory + get_hash(img) + ".jpg") and not force:
            print("thumbnail for {} already exists".format(img))
            return
        

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)

    except Exception as e:
        pass
        # print("(thumbnail) EXIF: " + str(e))

    try:
        #print("thumbnail'd")
        image.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.NEAREST)
        image = image.convert('RGB')

        #print("saved")
        filename = get_hash(img) + ".jpg"
        image.save(directory + filename)

        return 0

    except Exception as e:
        print("(thumbnail) saving: " + str(e))


def get_file_list(galleries):
    """
    get list of images of all galleries combined

    """

    file_list = []
    for _, gal in enumerate(galleries):
        print(gal)
        for img in galleries[gal]:
            file_list.append(img)

    return file_list

def main():
    """
    generate gallery based on configuration file.

    """

    image_data    = []
    galleries = {}

    with open("gallery.yml", "r") as gallery_file:
        for line in gallery_file:
            i_path, categories, _ = line.split(";")
            im_path = i_path.replace("\"", "") 
            img_path = im_path.strip()

            cat = categories.split(",")

            for category in cat:
                if not category in galleries:
                    galleries[category] = []

                galleries[category].append(img_path)
                # print("appended {} to {}".format(file_path, category))


#     for _, gal in enumerate(galleries):
#         print(gal)
#         for img in galleries[gal]:
#             print("  " + img)

            # image_data.append({"file": file_path, "categories": categories.split(",")})

    # TODO: expand patterns such as '*'
    #       automatically create directories

    # cp img to img directory
    for file_path in get_file_list(galleries):
        try:
            if not os.path.isfile(IMAGE_DIR + file_path):
                shutil.copy2(FILE_DIR + file_path,\
                             IMAGE_DIR + file_path)
            else:
                print("(skipped) " + FILE_DIR + file_path)

        except Exception as e:
            print("Failed copying file: " + str(e))

        thumbnail(FILE_DIR + file_path, THUMB_DIR)
    # generate thumbnail

    # generate gallery

    return


if __name__ == '__main__':
    main()
