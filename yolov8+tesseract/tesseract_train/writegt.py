import os


with open('datasets/gt.txt', 'r') as reader:
    lines = reader.readlines()
    for line in lines:
        txt = line.split('\t')[1]
        with open(f'datasets/images/{txt}.gt.txt', 'w') as writer:
            writer.write(txt)
        