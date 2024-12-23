from ultralytics import YOLO
from PIL import Image, ImageDraw
import os
import pytesseract
import pandas as pd
import Levenshtein

# AI PART

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

def trian_yolov8(model_path, image_path):
    model = YOLO(model_path)
    results = model(image_path)
    print(results[0].boxes.xyxy)
    return results[0].boxes.xyxy


def screenshot(image_path, coor, index, output_path):
    image = Image.open(image_path)
    crop_box = [int(coordinate.item()) for coordinate in coor.round()]
    cropped_image = image.crop((crop_box[0], crop_box[1], crop_box[2], crop_box[3]))
    image_name = os.path.basename(image_path).split(".")[0]

    # remove the folder if it already exists
    if (index == 0 and os.path.exists(os.path.join(output_path, image_name))):
        os.system(f"rm -rf {os.path.join(output_path, image_name)}")
    
    # create the folder if it does not exist
    if (index == 0 and not os.path.exists(os.path.join(output_path, image_name))):
        os.makedirs(os.path.join(output_path, image_name))
    
    cropped_image.save(os.path.join(output_path, image_name, f"{index}.jpg"))

def tesseract(image):
    text = pytesseract.image_to_string(image, lang="tha", config="--psm 6")
    return text

def normalize_text(text):
    text = text.replace("\n", "")
    text = text.replace(" ", "")
    text = text.lower()
    return text

def check_similarity(word1, word2):
    distance = Levenshtein.distance(word1, word2)
    max_len = max(len(word1), len(word2))
    similarity = 1 - (distance / max_len)
    return similarity



# EXCEL PART

def read_column_a_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="Sheet1")
    column_a = df['shoes-code']
    column_a_list = column_a.to_list()
    return column_a_list
            
def check_excel_from_list(column_list, shoes_code):
    excel_color_list = []
    for code in column_list:
        transformed_code = ""
        for char in code:
            if (ord(char) > 0x0E00 and ord(char) < 0x0E7F):
                break
            transformed_code += char
        if (normalize_text(transformed_code) == shoes_code):
            color = ""
            for char_shoes in code:
                if (ord(char_shoes) > 0x0E00 and ord(char_shoes) < 0x0E7F):
                    color += char_shoes
            excel_color_list.append(color)
    return excel_color_list



# IMAGE PATH PART

def main():
    text_model_path = "yolo-model/text-yolov8-350img.pt"
    input_dir_path = "datasets/SH"
    screenshot_path = "screenshot"
    # open excel file
    excel_path = "datasets/shoes-detection-excel-2.xlsx"
    column_a_list = read_column_a_excel(excel_path)
    print(column_a_list)  

    #list all the file and color in the list dict
    # list all the image in the input directory
    input_list = os.listdir(input_dir_path)
    shoes_list = []
    for input_file in input_list:
        image_path = os.path.join(input_dir_path, input_file)
        shoes_dict = {"name": input_file, "detail": []}
        coor_list = trian_yolov8(text_model_path, image_path)
        image = Image.open(image_path)
        # get coordinate for each shoes color in the image
        for index, coor in enumerate(coor_list):
            draw = ImageDraw.Draw(image)
            draw.rectangle([coor[0], coor[1], coor[2], coor[3]], outline="black", width=3)
            screenshot(image_path, coor, index, screenshot_path)
            image = Image.open(os.path.join(screenshot_path, os.path.basename(image_path).split(".")[0], f"{index}.jpg"))
            text = tesseract(image)
            check = True
            text = normalize_text(text)
            for char in text:
                if ord(char) < 0x0E00 or ord(char) > 0x0E7F:
                    check = False
                    break
            if (check):
                print(text)
                shoes_dict["detail"].append({"coor": (coor[0] + (coor[2] - coor[0])/2, coor[1] + (coor[3] - coor[1])/2), "text": text})
        shoes_list.append(shoes_dict)

        # list all the color that the shoe have in the excel file
        color_list = check_excel_from_list(column_a_list, normalize_text(os.path.basename(image_path).split(".")[0]))

        # no color 
        if (len(color_list) == 0):
            print("No color list found in the excel file")
            continue
        # use nlp to normalize the shoes list
        remove_list = []
        for detail in shoes_dict["detail"]:
            text = normalize_text(detail["text"])
            max = 0
            with open("datasets/color_list.txt", "r") as reader:
                lines = reader.readlines()
                for line in lines:
                    line = line.replace("\n", "")
                    similarity = check_similarity(text, line)
                    if (similarity > max):
                        max = similarity
                        detail["text"] = normalize_text(line)
            if (max < 0.2):
                remove_list.append(detail["text"])
        # delete those color from the image detail list
        # results
        print("results: ")
        print(shoes_dict["detail"])
        for detail in shoes_dict["detail"]:
            if (detail["text"] in color_list):
                remove_list.append(detail["text"])
        print("remove list:")
        print(remove_list)
        for remove in remove_list:
            for detail in shoes_dict["detail"]:
                if (detail["text"] == remove):
                    shoes_dict["detail"].remove(detail)

        # get the coordinate of every shoes
        coor_shoes_list = trian_yolov8("yolo-model/image-yolov8-500img.pt", image_path)
        cross_shoes_list = []
        for detail in shoes_dict["detail"]:
            min = 1280
            min_coor_shoes = (0, 0, 0, 0)
            for coor_shoes in coor_shoes_list:
                x_center = coor_shoes[0] + (coor_shoes[2] - coor_shoes[0])/2
                y_center = coor_shoes[1] + (coor_shoes[3] - coor_shoes[1])/2
                if (abs(detail["coor"][0] - x_center) + abs(detail["coor"][1] - y_center) < min):
                    min = abs(detail["coor"][0] - x_center) + abs(detail["coor"][1] - y_center)
                    min_coor_shoes = (coor_shoes[0], coor_shoes[1], coor_shoes[2], coor_shoes[3])
            cross_shoes_list.append(min_coor_shoes)

        # cross out shoes
        image = Image.open(image_path)
        for coor_shoes in cross_shoes_list:
            # search image to draw before
            draw = ImageDraw.Draw(image)
            x_center = coor_shoes[0] + (coor_shoes[2] - coor_shoes[0])/2
            y_center = coor_shoes[1] + (coor_shoes[3] - coor_shoes[1])/2
            draw.line((x_center - 100, y_center - 100, x_center + 100, y_center + 100), fill="red", width=25)
            draw.line((x_center - 100, y_center + 100, x_center + 100, y_center - 100), fill="red", width=25)
            
        image.save(os.path.join("results", os.path.basename(image_path)))

    # print(shoes_list)
    # for shoe in shoes_list:
    #     print(shoe["name"])
    #     for detail in shoe["detail"]:
    #         print("coor: ", detail["coor"], " text: ", detail["text"])
    
if __name__ == '__main__':
    main()