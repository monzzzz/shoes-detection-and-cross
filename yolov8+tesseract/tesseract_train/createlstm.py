import subprocess
import os

# with open('datasets/gt.txt', 'r') as reader:
#     lines = reader.readlines()
#     for line in lines:
#         txt = line.split('\t')[1]
#         txt = txt.replace('\n', '')
#         # tesseract /path/to/training_data/example.png /path/to/training_data/example --psm 6 lstm.train
#         subprocess.run(['tesseract', f'datasets/images/{txt}.png', f'datasets/lstm/{txt}', '--psm', '6', 'lstm.train'])
        

list_lstm = os.listdir('datasets/lstm')
for file in list_lstm:
    with open("datasets/lstm.txt", 'a') as writer:
        writer.write(f"lstm/{file}\n")