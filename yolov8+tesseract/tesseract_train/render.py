from PIL import Image, ImageDraw
import os

def main():
    input_path = "datasets/images"
    label_path = "datasets/labels"
    list_images = os.listdir(input_path)
    for images in list_images:
        if (images.split(".")[1] == "png"):
            image = Image.open(os.path.join(input_path, images))
            for box in list_images:
                if (box.split(".")[1] == "box" and box.split(".")[0] == images.split(".")[0]):
                    with open(os.path.join(input_path, box), 'r') as f:
                        lines = f.readlines()
                        print(images.split(".")[0])
                        draw = ImageDraw.Draw(image)
                        for line in lines:
                            print(line)
                            line = line.split(" ")
                            x1, y1, x2, y2 = int(line[1]), int(line[2]), int(line[3]), int(line[4])
                            draw.rectangle([x1, y1, x2, y2], outline="black", width=3)
                            image.save(os.path.join(label_path, images))
            image.show()

if __name__ == '__main__':
    main()