import torch
import numpy as np
import time

def test_model(model, test_loader, platform):
    
    device = torch.device(platform)
    
    path_list = []
    output_list = []
    label_list = []
    
    model.to(device)
    model.eval()
    with torch.no_grad():
        num_correct = 0
        num_total = 0
        
        start_time = time.perf_counter()
        for i, data in enumerate(test_loader):
            paths, inputs, labels = data
            inputs, labels = inputs.to(device), labels.to(device)          
            outputs = model(inputs)
            
            # if labels is probability over classes, correct is label closest to classes
            if len(labels.shape) == 1:
                num_correct += torch.sum((torch.argmax(outputs, dim=1) == labels))
            else:
                num_correct += torch.sum((torch.argmax(outputs, dim=1) == torch.argmax(labels, dim=1)))
            
            num_total += labels.shape[0]
            output_list.append(outputs)
            label_list.append(labels)
            path_list += list(paths)
            
       # print("Acc: ", num_correct.item()/num_total)
        
        end_time = time.perf_counter()
        inference_time = end_time-start_time
        output_list = np.array(torch.concatenate(output_list, axis=0).cpu())
        label_list = np.array(torch.concatenate(label_list, axis=0).cpu())
    return path_list, output_list, label_list, inference_time
    
def test_model_double_label(model, test_loader, platform):   

    device = torch.device(platform)   

    path_list = []
    output_list = []
    label_list = []   

    model.to(device)
    model.eval()
    with torch.no_grad():
        num_correct = 0
        num_total = 0       

        start_time = time.perf_counter()
        for i, data in enumerate(test_loader):
            paths, inputs, labels = data
            labels = torch.stack(labels, dim=1)
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            num_correct += torch.sum(torch.all(torch.argmax(outputs, dim=2) == labels, dim=1))           

            num_total += labels.shape[0]
            output_list.append(outputs)
            label_list.append(labels)
            path_list += list(paths)           

        #print("Acc: ", num_correct.item()/num_total)      

        end_time = time.perf_counter()
        inference_time = end_time-start_time
        output_list = np.array(torch.concatenate(output_list, axis=0).cpu())
        label_list = np.array(torch.concatenate(label_list, axis=0).cpu())
    return path_list, output_list, label_list, inference_time
