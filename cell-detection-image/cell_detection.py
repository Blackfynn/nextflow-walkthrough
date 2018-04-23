import os
import sys
import numpy as np
from scipy import misc

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def detect_cells(input_file, threshold):
    tile_prefix = os.path.splitext(os.path.basename(input_file))[0]
    tile_parts = tile_prefix.split('_')
    output_prefix = tile_parts[1].zfill(2) + '_' + tile_parts[0].zfill(2)
    output_file = '{}_binary.jpeg'.format(output_prefix)
    output_path = os.path.join(output_directory, output_file)

    img = misc.imread(input_file)
    img = rgb2gray(img)
    img = img/255.0
    binary_img = np.uint8(img > threshold)*255
    
    misc.imsave(output_path, binary_img)
    
threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15

input_path = sys.argv[1]
output_directory = sys.argv[2]

if os.path.isdir(input_path):
    for filename in os.listdir(input_path):
        input_file = os.path.join(input_path, filename)
        detect_cells(input_file, threshold)
else:
    detect_cells(input_path, threshold)
