import os
import sys

BASE_DIR = os.path.dirname(os.getcwd())
# config working dir
sys.path.append(BASE_DIR)

from core import handler

if __name__ == '__main__':
    handler.ArgvHandler(sys.argv)
