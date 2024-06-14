from PIL import Image, ImageDraw, ImageFont
import random
import os
import subprocess

def clean_text_file(text_file_path):
    with open(text_file_path, 'w') as text_file:
        text_file.write('')

def write_path_on_text_file(text_file_path, file_path, label):
    with open(text_file_path, 'a') as text_file:
        text_file.write(file_path + '\t' + label + '\n')

def generate_images_with_pillow(file_path, output_folder_path, font_path, text_file_path):
    with open(file_path, "r") as read_file:
        lines = read_file.readlines()
        index = 0
        random.shuffle(lines)
        # shuffle the line
        clean_text_file(text_file_path)
        for line in lines:
            image_width, image_height = 1000, 100
            image = Image.new('RGB', (image_width, image_height), color="white")
            draw = ImageDraw.Draw(image) 
            font = ImageFont.truetype(font_path, 50)
            draw.text((20, 20), line, font=font, fill=(0,0,0))
            if (line.rstrip('\n') == '.' or line.rstrip('\n') == '/' ):
                print(True)
                continue
            try:
                image.save(os.path.join(output_folder_path, line.rstrip('\n') + ".png"))
                write_path_on_text_file(text_file_path, os.path.join("images/", line.rstrip('\n') + ".png"), line.rstrip('\n'))
                index += 1
            except:
                print("error")

def main():
    file_path = 'datasets/corpus.txt'
    output_folder_path = 'datasets/images'
    font_path = 'datasets/fonts/Sarabun/Sarabun-Regular.ttf'
    text_file_path = 'datasets/gt.txt'
    generate_images_with_pillow(file_path, output_folder_path, font_path, text_file_path)
    image_list = os.listdir(output_folder_path)
    for image in image_list:
        subprocess.run(["tesseract", os.path.join(output_folder_path, image), os.path.join(output_folder_path, image.split(".")[0]),"-l", "tha",  "batch.nochop", "makebox"])



if __name__ == '__main__':
    main()