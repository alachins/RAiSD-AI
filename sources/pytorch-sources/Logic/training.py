import torch
import numpy as np
import time
from Logic.testing import test_model, test_model_double_label


def train_model(model, train_loader, epochs, infofilename, lr, platform, loss_weights=None, val_loader=None, mini_batch_size=None):
    
    device = torch.device(platform)
    
    model.train(True)
    if loss_weights != None:
        loss_weights=torch.tensor(loss_weights, device=platform)
        
    loss_fn = torch.nn.CrossEntropyLoss(weight=loss_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=0)
    batch_accuracies = []
    val_accuracies = []
    batch_losses = []
    prev_val_acc = 0
    
    if mini_batch_size == None:
        mini_batch_size = train_loader.batch_size
    
    model.to(device)
    start_time = time.perf_counter()
    for epoch in range(epochs):
        running_loss = 0
        batch_correct = 0
        batch_total = 0
        
        for i, super_batch in enumerate(train_loader):
            super_paths, super_inputs, super_labels = super_batch
            super_inputs, super_labels = super_inputs.to(device), super_labels.to(device) 
            for inputs, labels in zip(torch.split(super_inputs, mini_batch_size, dim=0), torch.split(super_labels, mini_batch_size, dim=0)):
                optimizer.zero_grad()
                outputs = model(inputs)
                # if labels is probability over classes, correct is label closest to classes
                if len(labels.shape) == 1:
                    batch_correct += torch.sum((torch.argmax(outputs, dim=1) == labels))
                else:
                    batch_correct += torch.sum((torch.argmax(outputs, dim=1) == torch.argmax(labels, dim=1)))
                    
                batch_total += labels.shape[0]
                
                loss = loss_fn(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
            
            
        batch_accuracy = batch_correct / batch_total
        batch_loss = running_loss / len(train_loader)
        batch_accuracies.append(batch_accuracy)
        batch_losses.append(batch_loss)
        
        if val_loader != None:
            _, val_outputs, val_labels, _ = test_model(model, val_loader, platform=platform)
            model.train(True)
            
            # if labels is probability over classes, correct is label closest to classes
            if len(val_labels.shape) == 1:
                num_correct = np.sum((np.argmax(val_outputs, axis=1) == val_labels))
            else:
                num_correct = np.sum((np.argmax(val_outputs, axis=1) == np.argmax(val_labels, axis=1)))
            
            num_total = val_labels.shape[0]
            val_accuracy = num_correct / num_total
            val_accuracies.append(val_accuracy)
            #print("epoch {}, loss {}, acc {}, val_acc {}".format(epoch, batch_loss, batch_accuracy, val_accuracy))
            if val_accuracy > prev_val_acc:
           	#print("Epoch {}, loss {}, acc {}, val_acc {}".format(epoch, batch_loss, batch_accuracy, val_accuracy))
                with open(infofilename, "a") as f:
                    f.write("Epoch {}: loss {}, acc {}, val_acc {} [SAVING BEST MODEL, ACCURACY: {}]\n".format(epoch, batch_loss, batch_accuracy, val_accuracy, val_accuracy))
                print("Epoch {}: loss {}, acc {}, val_acc {} [SAVING BEST MODEL, ACCURACY: {}]".format(epoch, batch_loss, batch_accuracy, val_accuracy, val_accuracy))
                prev_val_acc = val_accuracy
                best_state = {}
                for key in model.state_dict():
                    best_state[key] = model.state_dict()[key].clone()
            else:
                with open(infofilename, "a") as f:
                    f.write("Epoch {}: loss {}, acc {}, val_acc {}\n".format(epoch, batch_loss, batch_accuracy, val_accuracy))
                print("Epoch {}: loss {}, acc {}, val_acc {}".format(epoch, batch_loss, batch_accuracy, val_accuracy))
        else:
            with open(infofilename, "a") as f:
                    f.write("epoch {}, loss {}, acc {}\n".format(epoch, batch_loss, batch_accuracy))         
            print("epoch {}, loss {}, acc {}".format(epoch, batch_loss, batch_accuracy))
        
    end_time = time.perf_counter()
    inference_time = end_time-start_time
    batch_accuracies = np.array(torch.Tensor(batch_accuracies).cpu())
    batch_losses = np.array(torch.Tensor(batch_losses).cpu())
    val_accuracies = np.array(val_accuracies)
    
    if val_loader != None:
        model.load_state_dict(best_state)
        
    return model, (batch_accuracies, batch_losses, inference_time, val_accuracies)
    


def train_model_double_label(model, train_loader, epochs, infofilename, lr, platform, loss_weights=None, val_loader=None, mini_batch_size=None):   

    device = torch.device(platform)   

    model.train(True)
    if loss_weights != None:
        loss_weights=torch.tensor(loss_weights, device=platform)       

    loss_fn = torch.nn.CrossEntropyLoss(weight=loss_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=0)
    batch_accuracies = []
    val_accuracies = []
    batch_losses = []
    prev_val_acc = 0   

    if mini_batch_size == None:
        mini_batch_size = train_loader.batch_size
   
    model.to(device)
    start_time = time.perf_counter()
    for epoch in range(epochs):
        running_loss = 0
        correct_1 = 0
        correct_2 = 0
        batch_total = 0       

        for i, super_batch in enumerate(train_loader):
            super_paths, super_inputs, super_labels = super_batch
            super_labels = torch.stack(super_labels, dim=1)
            super_inputs, super_labels = super_inputs.to(device), super_labels.to(device)
            for inputs, labels in zip(torch.split(super_inputs, mini_batch_size, dim=0), torch.split(super_labels, mini_batch_size, dim=0)):
                optimizer.zero_grad()
                outputs = model(inputs)
                # if labels is probability over classes, correct is label closest to classes
                labels_1 = labels[:,0]
                labels_2 = labels[:,1]
                outputs_1 = outputs[:,0,:]
                outputs_2 = outputs[:,1,:]               

                correct_1 += torch.sum(torch.argmax(outputs_1, dim=1) == labels_1)
                correct_2 += torch.sum(torch.argmax(outputs_2, dim=1) == labels_2)                   

                batch_total += labels.shape[0]               

                loss_1 = loss_fn(outputs_1, labels_1)
                loss_1.backward(retain_graph=True)
                loss_2 = loss_fn(outputs_2, labels_2)
                loss_2.backward()
                optimizer.step()
                running_loss += (loss_1.item() + loss_2.item())          

        accuracy_1 = correct_1 / batch_total
        accuracy_2 = correct_2 / batch_total
        batch_loss = running_loss / len(train_loader)
        batch_accuracies.append((accuracy_1, accuracy_2))
        batch_losses.append(batch_loss)       

        if val_loader != None:
            _, val_outputs, val_labels, _ = test_model_double_label(model, val_loader, platform=platform)
            model.train(True)           

            val_labels_1 = val_labels[:,0]
            val_labels_2 = val_labels[:,1]
            val_outputs_1 = val_outputs[:,0,:]
            val_outputs_2 = val_outputs[:,1,:]           

            val_correct_1 = np.sum(np.argmax(val_outputs_1, axis=1) == val_labels_1)
            val_correct_2 = np.sum(np.argmax(val_outputs_2, axis=1) == val_labels_2)
            # if labels is probability over classes, correct is label closest to classes           

            num_total = val_labels.shape[0]
            val_accuracy_1 = val_correct_1 / num_total
            val_accuracy_2 = val_correct_2 / num_total
            val_accuracies.append((val_accuracy_1, val_accuracy_2))
         #   print("epoch {}, loss {}, acc_1 {}, acc_2 {}, val_acc_1 {}, val_acc_2 {}".format(epoch, batch_loss, accuracy_1, accuracy_2, val_accuracy_1, val_accuracy_2))
         #   if val_accuracy_1*val_accuracy_2 >= prev_val_acc:
         #       print("Saving best model")
         #       prev_val_acc = val_accuracy_1*val_accuracy_2
         #       best_state = {}
         #       for key in model.state_dict():
         #           best_state[key] = model.state_dict()[key].clone()
        #else:        
        #    print("epoch {}, loss {}, acc_1 {}, acc_2 {}".format(epoch, batch_loss, accuracy_1, accuracy_2))
            
            if val_accuracy_1*val_accuracy_2 > prev_val_acc:
                #print("Epoch {}, loss {}, acc {}, val_acc {}".format(epoch, batch_loss, batch_accuracy, val_accuracy))
                with open(infofilename, "a") as f:
                    f.write("Epoch {}: loss {}, acc_1 {}, acc_2 {}, val_acc1 {}, val_acc2 {} [SAVING BEST MODEL, ACCURACY: {}]\n".format(epoch, batch_loss, accuracy_1, accuracy_2, val_accuracy_1, val_accuracy_2, val_accuracy_1*val_accuracy_2))
                print("Epoch {}: loss {}, acc_1 {}, acc_2 {}, val_acc1 {}, val_acc2 {} [SAVING BEST MODEL, ACCURACY: {}]".format(epoch, batch_loss, accuracy_1, accuracy_2, val_accuracy_1, val_accuracy_2, val_accuracy_1*val_accuracy_2))
                prev_val_acc = val_accuracy_1*val_accuracy_2
                best_state = {}
                for key in model.state_dict():
                    best_state[key] = model.state_dict()[key].clone()
            else:
                with open(infofilename, "a") as f:
                    f.write("Epoch {}: loss {}, acc_1 {}, acc_2 {}, val_acc1 {}, val_acc2 {}\n".format(epoch, batch_loss, accuracy_1, accuracy_2, val_accuracy_1, val_accuracy_2))
                print("Epoch {}: loss {}, acc_1 {}, acc_2 {}, val_acc1 {}, val_acc2 {}".format(epoch, batch_loss, accuracy_1, accuracy_2, val_accuracy_1, val_accuracy_2))
        else:
            with open(infofilename, "a") as f:
                    f.write("epoch {}, loss {}, acc {}, acc2 {}\n".format(epoch, batch_loss, accuracy_1, accuracy_2))         
            print("epoch {}, loss {}, acc1 {}, acc2 {}".format(epoch, batch_loss, accuracy_1, accuracy_2))
            
                   

    end_time = time.perf_counter()
    inference_time = end_time-start_time
    batch_accuracies = np.array(torch.Tensor(batch_accuracies).cpu())
    batch_losses = np.array(torch.Tensor(batch_losses).cpu())
    val_accuracies = np.array(val_accuracies)   

    if val_loader != None:
        model.load_state_dict(best_state)       

    return model, (batch_accuracies, batch_losses, inference_time, val_accuracies)

