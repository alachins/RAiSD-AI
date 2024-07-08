import sys, time, os
import getopt
import argparse
import shutil

from Logic import Architecture
from contextlib import redirect_stdout




def main(argv):

	opts, ars = getopt.getopt(argv, "d:n:h:w:e:m:o:", ["directory=", "mode=", "height=", "width=", "epoch=", "model=", "outpath="])
    
	for opt, arg in opts:
		if opt in ("-d", "--directory"):
			direct = arg
		elif opt in ("-n", "--mode"):
    			mod = arg
		elif opt in ("-h", "--height"):
			height = arg
		elif opt in ("-w", "--width"):
			width = arg
		elif opt in ("-e", "--epoch"):
			epoch = arg
		elif opt in ("-m", "--model"):
			model = arg
		elif opt in ("-o", "--outpath"):
			out = arg
	
	
# modelname, inputpath, outputpath(folder)
# add imageheight, imagewidth, epochs
# how ASDEC generates images,  python script randomly generate the images
# recognized by 
# 
# call ASDEC with input (training) commond, copy the images to another folder, call my script
	
	
	if (mod == "train"):
		
		trainModel = Architecture.Training(direct, int(float(height)), int(float(width)), int(epoch), model, out)
		trainModel.traingModel()
		
		
		
	if (mod == "predict"):
		if not os.path.exists(out):
			os.makedirs(out)
		else:
			shutil.rmtree(out)
			os.makedirs(out)
		
		loadModel = Architecture.Load(model, direct, height, width, out, 1)
		numberOfImages = loadModel.imageFolder()
		loadModel.generateReport()
		
	
	
	
if __name__ == "__main__":
    main(sys.argv[1:])	
