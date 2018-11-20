import os
import sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DIR = BASE_DIR + r'\User'
sys.path.append(USER_DIR)
__all__ = ['user']
