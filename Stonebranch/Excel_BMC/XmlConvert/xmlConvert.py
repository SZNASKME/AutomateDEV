import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createFile import createJson, createExcel
from utils.readFile import loadText



XML_PATH = './Stonebranch/Excel_BMC/XmlConvert/Open-CTE1-20092024.xml'





def main():
    XML_text = loadText(XML_PATH)
    


if __name__ == '__main__':
    main()