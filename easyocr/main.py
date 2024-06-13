import os
import tools
import cv2
from PIL import Image

input_dir_path = "datasets/KLM"
preprocess_dir_path = "preprocess"

def main():
    files_list = os.listdir(input_dir_path)
    shoes_list = []
    for file in files_list:
        image = cv2.imread(os.path.join(input_dir_path, file))
        image = tools.pre_process_image(image, invert=True, denoise= True)
        cv2.imwrite(os.path.join(preprocess_dir_path, file), image)
        processed_image = Image.open(os.path.join(preprocess_dir_path, file))
        shoes_dict = tools.easy_ocr(processed_image, file, prob=0.5)
        shoes_list.append(shoes_dict)
        print(shoes_dict["name"])
        for detail in shoes_dict["detail"]:
            print("color: ", detail["color"], " prob: ", detail["prob"])


if __name__ == '__main__':
    main()