from Logic.dataLoad import get_loader
from Logic.models import SweepNet, FAST_NN, SweepNetRecombination
from Logic.testing import test_model, test_model_double_label
from Logic.training import train_model, train_model_double_label
import torch
import numpy as np
import os
import getopt
import time
import sys
import json
    
def train(height, width, epochs, batch, platform, opath, ipath, model_class, use_bp_distance, load_binary, train_detect, infofilename, reduction, hotspot, labelnames):
    #print("Training model", opath, end=' ')
    
    with open(opath + "/classLabels.txt", "w") as f:
        classes = sorted(entry.name for entry in os.scandir(ipath) if entry.is_dir())
        f.write("***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n")
        f.write(str(len(classes)))
        f.write("\n")
        for i, class_name in enumerate(classes):
            f.write(class_name)
            f.write(" ({})\n".format(i))
        f.write("***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***")
       
    lr = 0.5e-3
    if use_bp_distance:
        channels = 2
    else:
        channels = 1
        
    if hotspot:
        outputs = 2
    else:
        outputs = 1
    
    if model_class == "FAST-NN":
        model = FAST_NN(height, width, channels=channels, outputs=outputs)
    elif model_class == "SweepNetRecombination":
        model = SweepNetRecombination(height, width, channels=channels, outputs=outputs)
        lr = 5e-3
    elif model_class == "SweepNet":
        model = SweepNet(height, width, channels=channels, outputs=outputs)
    else:
        raise ValueError("Unknown model class")
        
    validation = True
    if train_detect:
        validation == False
        
    train_loader, val_loader = get_loader(ipath, 128, class_folders=True, shuffle=True, load_binary=load_binary, shuffle_row=True, mix_images=False, validation=validation, train_detect=train_detect, reduction=reduction, hotspot=hotspot, label_names=labelnames)
    if hotspot:
        model, history = train_model_double_label(model, train_loader, epochs, infofilename, lr=lr, loss_weights=None, platform=platform, val_loader=val_loader, mini_batch_size=batch)
    else:  
        model, history = train_model(model, train_loader, epochs, infofilename, lr=lr, loss_weights=None, platform=platform, val_loader=val_loader, mini_batch_size=batch)
    torch.save(model.state_dict(), os.path.join(opath, 'model.pt'))
    
        
def test(height, width, platform, mpath, ipath, opath, model_class, use_bp_distance, load_binary, reduction, hotspot, labelnames):
    #print("Testing model ", mpath)
    
    # set class folders to false for production
    test_loader, _ = get_loader(ipath, batch_size=128, class_folders=False, shuffle=False, load_binary=load_binary, shuffle_row=False, mix_images=False, validation=False, train_detect=False, reduction=reduction, hotspot=hotspot, label_names=labelnames)
              
    if use_bp_distance:
        channels = 2
    else:
        channels = 1        

    if hotspot:
        outputs = 2
    else:
        outputs = 1    

    if model_class == "FAST-NN":
        model = FAST_NN(height, width, channels=channels, outputs=outputs)
    elif model_class == "SweepNetRecombination":
        model = SweepNetRecombination(height, width, channels=channels, outputs=outputs)
    elif model_class == "SweepNet":
        model = SweepNet(height, width, channels=channels, outputs=outputs)
    else:
        raise ValueError("Unknown model class")    

    init_state = torch.load(os.path.join(mpath, 'model.pt'), map_location=torch.device(platform))
    model.load_state_dict(init_state)    

    if hotspot:
        start = time.perf_counter()
        path_list, output_list, label_list, inference_time = test_model_double_label(model, test_loader, platform=platform)
        #print(time.perf_counter() - start)
        resultsData = np.empty((0, 7), float)
        probability_tensor_1 = torch.nn.functional.softmax(torch.Tensor(output_list)[:,0,:], dim=1)[:, 1]
        probability_tensor_2 = torch.nn.functional.softmax(torch.Tensor(output_list)[:,1,:], dim=1)[:, 1]
        for path, probability_1, probability_2, label in zip(path_list, probability_tensor_1, probability_tensor_2, label_list):
            path = os.path.split(path)[1]
            resultsData = np.append(resultsData,
                                    np.array([[path,
                                            label[0],
                                            label[1],
                                            float(1-probability_1),
                                            float(probability_1),
                                            float(1-probability_2),
                                            float(probability_2)
                                            ]]),
                                    axis=0)
    else:
        start = time.perf_counter()
        path_list, output_list, label_list, inference_time = test_model(model, test_loader, platform=platform)
        #print(time.perf_counter() - start)        

        resultsData = np.empty((0, 4), float)
        probability_tensor = torch.nn.functional.softmax(torch.Tensor(output_list), dim=1)[:, 1]
        for path, probability, label in zip(path_list, probability_tensor, label_list):
            path = os.path.split(path)[1]
            resultsData = np.append(resultsData,
                                    np.array([[path,
                                            label,
                                            float(1-probability),
                                            float(probability)
                                            ]]),
                                    axis=0)    

    resultsData = resultsData[resultsData[:, 0].argsort()]
    np.savetxt(os.path.join(opath, 'PredResults.txt'), resultsData[:][:], fmt="%s")


        

# a parameter to select which model to use is required to be implemented.
def main(argv):

    opts, args = getopt.getopt(argv, "m:p:t:a:r:e:i:o:d:h:w:c:f:x:y:b:l:n:H", ["mode=", "platform=", "threads=", "infofilename=", "reduce=","epochs=", "ipath=", "opath=", "modeldirect=", "height=", "width=", "class=", "file=", "distance=", "detect=", "batch", "hotspot=", "labelnames=", "help"])
 
    labelnames = "[]"
    hotspot = 0 
    for opt, arg in opts:
        if opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-p", "--platform"):
            platform = arg
        elif opt in ("-t", "--threads"):
            threads = arg
        elif opt in ("-a", "--infofilename"):
            infofilename = arg
        elif opt in ("-r", "--reduce"):
            allelefreq = arg
        elif opt in ("-e", "--epochs"):
            epochs = arg
        elif opt in ("-i", "--ipath"):
            ipath = arg
        elif opt in ("-o", "--opath"):
            opath = arg
        elif opt in ("-d", "--modeldirect"):
            mpath = arg
        elif opt in ("-h", "--height"):
            height = arg
        elif opt in ("-w", "--width"):
            width = arg
        elif opt in ("-c", "--class"):
            model_class = arg
        elif opt in ("-f", "--file"):
            load_binary = arg
        elif opt in ("-x", "--distance"):
            use_bp_distance = arg
        elif opt in ("-y", "--detect"):
            train_detect = arg
        elif opt in ("-b", "--batch"):
            batch = arg
        elif opt in ("-l", "--hotspot"):
            hotspot = arg
        elif opt in ("-n", "--labelnames"):
            labelnames = arg
        elif opt in ("-H", "--help"):
            help()
            return 0
	
    if not os.path.exists(opath):
        os.makedirs(opath)
        
    torch.set_num_threads(int(threads))

    if (mode == "train"):
        start=time.time()
        train(int(height), int(width), int(epochs), int(batch), platform, opath, ipath, model_class, int(use_bp_distance), int(load_binary), int(train_detect), infofilename, int(allelefreq), int(hotspot), json.loads(labelnames))
        end=time.time()
       # with open(opath + "/image-dimensions.txt", "w") as f:
        #    f.write(str(str(height) + " " + str(width)))
            
            
    elif (mode == "predict"):
        start=time.time()
        test(int(height), int(width), platform, mpath, ipath, opath, model_class, int(use_bp_distance), int(load_binary), int(allelefreq), int(hotspot), json.loads(labelnames))
        end=time.time()
        
    else:
        print("No valid mode detected")
        return 0
			
if __name__ == "__main__":
    main(sys.argv[1:])		
