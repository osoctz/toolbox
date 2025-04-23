import asyncio
import os
import re
import sys

import PIL
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server.recog_service import arecog_chain


def natural_sort_key(s):
    """Convert text to a list of integers and non-integer substrings to sort naturally."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]


def recog_ouput(origin_dir, result_path, sheet_name):
    imgsize = (720 / 4, 1280 / 4)
    wb = load_workbook(result_path)
    ws = wb.active
    ws.column_dimensions['B'].width = imgsize[0] * 0.14
    sheet = wb[sheet_name]

    files = recursive_listdir(origin_dir)
    # files = sorted(files, key=natural_sort_key)
    for index, file_path in enumerate(files):

        # origin_path = os.path.join(origin_dir, file)
        if os.path.isfile(file_path):
            # suffix = file[file.rfind('.'):]
            before, sep, suffix = file_path.rpartition('.')
            # print(f"before={before}, sep={sep}, suffix={suffix}")
            if suffix == 'png' or suffix == 'jpg' or suffix == 'jpeg':
                origin_img = Image(file_path)  # 缩放图片
                origin_img.width, origin_img.height = imgsize

                ws.add_image(origin_img, 'B' + str(index + 2))
                ws.row_dimensions[index + 2].height = imgsize[1] * 0.78

                sheet['A' + str(index + 2)].value = index + 1
                # sheet['B' + str(index + 2)].value = file
                _, _, _, result = asyncio.run(arecog_chain([PIL.Image.open(file_path)]))
                lang = result[0]['lang']
                document_type = result[0]['document_type']
                text = result[0]['text']
                print(f"{index + 1}:{lang} - {document_type} ")
                sheet['C' + str(index + 2)].value = lang
                sheet['D' + str(index + 2)].value = document_type
                sheet['E' + str(index + 2)].value = text

    wb.save("result.xlsx")


def recursive_listdir(path):
    result = []
    files = os.listdir(path)
    for file in files:

        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            result.append(file_path)
        elif os.path.isdir(file_path):
            result.extend(recursive_listdir(file_path))
    return result


if __name__ == '__main__':
    recog_ouput('/xx/Downloads/fail',
                "/xx/1.xlsx", "Sheet1")
