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

IMAGE_DIR = "img/"


def gen_gal_old(dir):
    """
    DEPRECATED, WILL BE DELETED

    """

    galleries = {}
                                                                         
    model = open("gallery.html")
    # template = jinja2.Template(model.read())
                                                                         
                                                                         
    for f in files:
        current_file = f.split("/")
        for cdir in current_file[:-1]:
            if cdir not in galleries:
                galleries[cdir] = []
                                                                         
            galleries[cdir].append(f)
                                                                         
    # print str(galleries)
                                                                         
    for gallery in galleries:
        files = galleries[gallery]
        gallery_content = template.render(files=files)
        file = open("export/" + str(gallery) + ".html","w")
        file.write(gallery_content)
        file.close()
        print("created file " + str("export/") + str(gallery) + ".html")
        return


def get_directory_tree(path):
    """
    Return a list of files in given folder with hierarchy preserved

    path -- path to list

    """

    # directories = [path]
    # tree = []

    # while directories:
    #     dir = directories.pop(0)
    #     res  = os.walk(dir)

    #     tree.append((str(dir), res[0], res[1]))
    #     directories.extend(res[0])

    file_list = []

    for dir_, _, files in os.walk(path):
        for filen in files:
            relative_path = os.path.relpath(dir_, path)
            file_list.append(os.path.join(relative_path, filen))
    print("(get_directory_tree) returning {}".format(str(file_list)))
    return file_list


def thumbnail(image_details): 
    """
    https://stackoverflow.com/questions/8631076/what-is-the-fastest-way-to-generate-image-thumbnails-in-python

    """

    size, filename = image_details
    try:
        Image.open(filename).thumbnail(size).save("thumbnail_%s" % filename)
        return 'OK'
    except Exception as e: 
        return e 


def generate_thumbnails(img_dir, thumb_dir, size):
    """
    generate thumbnails for given directory in another directory
    img_dir   -- directory of images to process
    thumb_dir -- directory in which thumbnails are written
    size      -- max size, in form of (x, y)

    """


    return


def main():
    """
    generate gallery based on configuration file.

    """

    # with open("structure.json") as structure:
    #     data = json.load(structure)

    files = get_directory_tree(IMAGE_DIR)
    # pprint.pprint(str(files))
    

    data = json.load(open('galleries.json'))

    data = data[0]
    pprint.pprint(str(data["galleries"][0]))
    galleries = data["galleries"]
    for gal in galleries:
        print(gal["name"])
        print(gal["default_img_name"])
        print(gal["dir"])
        print(gal["type"])
        print(gal["thumb"])
        print("sub galleries: ")
        for subg in gal["subgal"]:
            print("    {}".format(subg))

        print("---------")
        print("::" + gal["dir"] + " " + str(get_directory_tree(IMAGE_DIR + \
                                                               gal["dir"])))
        for img in get_directory_tree(gal["dir"]):
            print(str(img))

        print("=============")
    # print str(files)

    return


if __name__ == '__main__':
    main()
