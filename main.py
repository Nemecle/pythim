#!/usr/bin/python
"""
Gallery generation
"""

import json


def main():
    """
    generate gallery based on configuration file.

    """

    with open("structure.json") as structure:
        data = json.load(structure)



    return


if __name__ == '__main__':
    main()
