import torch
from math import floor


class SweepNet(torch.nn.Module):
    
    def __init__(self, H, W, channels, outputs=1, channel_select=0):
        super(SweepNet, self).__init__()
        
        conv1_kernel = (2,2)
        conv2_kernel = (2,2)
        conv3_kernel = (2,2)
        
        conv1_stride = (1, 1)
        conv2_stride = (1, 1)
        conv3_stride = (1, 1)
        
        conv1_channels = 32
        conv2_channels = 32
        conv3_channels = 32
        
        pool1_kernel = 2
        pool2_kernel = 2
        pool3_kernel = 2
        
        pool1_stride = 1
        pool2_stride = 1
        pool3_stride = 1
        
        self.outputs = outputs
        self.channel_select = channel_select
        self.channels = channels        
        self.conv1 = torch.nn.Conv2d(channels, conv1_channels, kernel_size=conv1_kernel, stride=conv1_stride, padding=0)
        self.pool1 = torch.nn.MaxPool2d(pool1_kernel, pool1_stride)
        self.relu1 = torch.nn.ReLU()
        
        self.conv2 = torch.nn.Conv2d(conv1_channels, conv2_channels, kernel_size=conv2_kernel, stride=conv2_stride, padding=0)
        self.pool2 = torch.nn.MaxPool2d(pool2_kernel, pool2_stride)
        self.relu2 = torch.nn.ReLU()
        
        self.conv3 = torch.nn.Conv2d(conv2_channels, conv3_channels, kernel_size=conv3_kernel, stride=conv3_stride, padding=0)
        self.pool3 = torch.nn.MaxPool2d(pool3_kernel, pool3_stride)
        self.relu3 = torch.nn.ReLU()
        
        # compute output size to FC
        out_conv1 = self.compute_out_shape((H, W), conv1_kernel, conv1_stride)
        out_pool1 = self.compute_out_shape(out_conv1, (pool1_kernel, pool1_kernel), (pool1_stride, pool1_stride))
        out_conv2 = self.compute_out_shape(out_pool1, conv2_kernel, conv2_stride)
        out_pool2 = self.compute_out_shape(out_conv2, (pool2_kernel, pool2_kernel), (pool2_stride, pool2_stride))
        out_conv3 = self.compute_out_shape(out_pool2, conv3_kernel, conv3_stride)
        out_pool3 = self.compute_out_shape(out_conv3, (pool3_kernel, pool3_kernel), (pool3_stride, pool3_stride))
        
        # init SE block layers
        r = 16
        self.se_pool = torch.nn.AvgPool2d(out_pool3)
        self.se_conv1 = torch.nn.Conv2d(in_channels=conv3_channels, out_channels=conv3_channels//r, kernel_size=1, stride=1)
        self.se_relu1 = torch.nn.ReLU()
        self.se_conv2 = torch.nn.Conv2d(in_channels=conv3_channels//r, out_channels=conv3_channels, kernel_size=1, stride=1)
        self.se_sig = torch.nn.Sigmoid()
        
        # init output layers
        self.fc1 = torch.nn.Linear(conv3_channels, 32)
        self.out_relu = torch.nn.ReLU()
        self.out_pool = torch.nn.AvgPool2d(out_pool3)
        self.fc2 = torch.nn.Linear(32, 2*self.outputs)
        self.softmax = torch.nn.Softmax(dim=1)
        
    def compute_out_shape(self, I, k, s):
        out_H = floor(((I[0] - (k[0] - 1) - 1) / s[0]) + 1)
        out_W = floor(((I[1] - (k[1] - 1) - 1) / s[1]) + 1)
        return (out_H, out_W)
    
        # execute SE block
    def SE_block(self, x_0):
        x = self.se_pool(x_0)      
        x = self.se_conv1(x)
        x = self.se_relu1(x)
        x = self.se_conv2(x)
        x = self.se_sig(x)
        x = torch.multiply(x_0, x)
        return x  
    
    def forward(self, x):
        if self.channels == 1:
            x = x[:,2,:,:].unsqueeze(1) # get one b/w channel, keep channels dim
        elif self.channels == 2:
            x_snp = x[:,2,:,:].unsqueeze(1)
            x = torch.cat((x[:,self.channel_select,:,:].unsqueeze(1), x_snp), dim=1)
        else:
            x = x[:,0:3,:,:]
        
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.relu1(x)
        
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.relu2(x)
        
        x = self.conv3(x)
        x = self.pool3(x)
        x = self.relu3(x)

        x = self.SE_block(x)
        x = torch.movedim(x, 1, -1)
        x = self.fc1(x)
        x = self.out_relu(x)
        x = torch.movedim(x, -1, 1)
        x = self.out_pool(x)
        x = x.flatten(1)
        x = self.fc2(x)
        x = x.reshape(-1, self.outputs, 2)
        x = x.squeeze(1)
        return x

    
    
class FAST_NN(torch.nn.Module):
    
    def __init__(self, H, W, outputs, channels):
        super(FAST_NN, self).__init__()
        
        conv1_kernel = 2
        conv2_kernel = 2
        conv3_kernel = 2
        
        conv1_stride = 1
        conv2_stride = 1
        conv3_stride = 1
        
        conv1_channels = 80
        conv2_channels = 80
        conv3_channels = 80
        
        pool1_kernel = 2
        pool2_kernel = 2
        pool3_kernel = 2
        
        pool1_stride = 2
        pool2_stride = 2
        pool3_stride = 2
                
        self.outputs = outputs
        self.channels = channels
        self.conv1 = torch.nn.Conv1d(channels, conv1_channels, kernel_size=conv1_kernel, stride=conv1_stride, padding=0)
        self.pool1 = torch.nn.MaxPool1d(pool1_kernel, pool1_stride)
        self.relu1 = torch.nn.ReLU()
        
        self.conv2 = torch.nn.Conv1d(conv1_channels, conv2_channels, kernel_size=conv2_kernel, stride=conv2_stride, padding=0)
        self.pool2 = torch.nn.MaxPool1d(pool2_kernel, pool2_stride)
        self.relu2 = torch.nn.ReLU()
        
        self.conv3 = torch.nn.Conv1d(conv2_channels, conv3_channels, kernel_size=conv3_kernel, stride=conv3_stride, padding=0)
        self.pool3 = torch.nn.MaxPool1d(pool3_kernel, pool3_stride)
        self.relu3 = torch.nn.ReLU()
        
        
        # compute output size to FC
        out_conv1 = self.compute_out_shape((H, W), (conv1_kernel, conv1_kernel), (conv1_stride, conv1_stride))
        out_pool1 = self.compute_out_shape(out_conv1, (pool1_kernel, pool1_kernel), (pool1_stride, pool1_stride))
        out_conv2 = self.compute_out_shape(out_pool1, (conv2_kernel, conv2_kernel), (conv2_stride, conv2_stride))
        out_pool2 = self.compute_out_shape(out_conv2, (pool2_kernel, pool2_kernel), (pool2_stride, pool2_stride))
        out_conv3 = self.compute_out_shape(out_pool2, (conv3_kernel, conv3_kernel), (conv3_stride, conv3_stride))
        out_pool3 = self.compute_out_shape(out_conv3, (pool3_kernel, pool3_kernel), (pool3_stride, pool3_stride))
        
        # init output layers
        self.fc1 = torch.nn.Linear(conv3_channels, 32)
        self.out_relu = torch.nn.ReLU()
        self.out_pool = torch.nn.AvgPool1d(out_pool3[1])
        self.fc2 = torch.nn.Linear(32, 2*self.outputs)
        self.softmax = torch.nn.Softmax(dim=1) 
        
    def compute_out_shape(self, I, k, s):
        out_H = floor(((I[0] - (k[0] - 1) - 1) / s[0]) + 1)
        out_W = floor(((I[1] - (k[1] - 1) - 1) / s[1]) + 1)
        return (out_H, out_W)
        
    def forward(self, x):
        
        if self.channels == 1:
            x = x[:,2,:,:].unsqueeze(1)
        elif self.channels == 2:
            x = x[:,1:3,:,:] 
        else:
            x = x[:,0:3,:,:]        
        x = torch.mean(x, dim=2)       
        
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.relu1(x)

        x = self.conv2(x)
        x = self.pool2(x)
        x = self.relu2(x)

        x = self.conv3(x)
        x = self.pool3(x)
        x = self.relu3(x)

        x = torch.movedim(x, 1, -1)  
        x = self.fc1(x)
        x = self.out_relu(x)
        x = torch.movedim(x, -1, 1)
        x = self.out_pool(x)
        x = x.flatten(1)
        x = self.fc2(x)
        x = x.reshape(-1, self.outputs, 2)
        x = x.squeeze(1)
        return x
    
    
class FASTER_NN(torch.nn.Module):
    def __init__(self, H, W, outputs, channels):
        super(FASTER_NN, self).__init__()
        
        conv1_kernel = 3
        conv2_kernel = 3
        conv3_kernel = 3
        conv4_kernel = 6
        conv5_kernel = 6
        conv6_kernel = 6
        
        conv1_stride = 1
        conv2_stride = 1
        conv3_stride = 1
        conv4_stride = 2
        conv5_stride = 2
        conv6_stride = 2
        
        conv1_channels = 32
        conv2_channels = 32
        conv3_channels = 32
        conv4_channels = 32
        conv5_channels = 32
        conv6_channels = 32
        
        pool1_kernel = 2
        pool2_kernel = 2
        pool3_kernel = 2
        
        pool1_stride = 2
        pool2_stride = 2
        pool3_stride = 2
                
        self.outputs = outputs
        self.channels = channels
        self.conv1 = torch.nn.Conv1d(channels, conv1_channels, kernel_size=conv1_kernel, stride=conv1_stride, padding=0)
        self.pool1 = torch.nn.MaxPool1d(pool1_kernel, pool1_stride)
        self.relu1 = torch.nn.ReLU()
        
        self.conv2 = torch.nn.Conv1d(conv1_channels, conv2_channels, kernel_size=conv2_kernel, stride=conv2_stride, padding=0)
        self.pool2 = torch.nn.MaxPool1d(pool2_kernel, pool2_stride)
        self.relu2 = torch.nn.ReLU()
        
        self.conv3 = torch.nn.Conv1d(conv2_channels, conv3_channels, kernel_size=conv3_kernel, stride=conv3_stride, padding=0)
        self.pool3 = torch.nn.MaxPool1d(pool3_kernel, pool3_stride)
        self.relu3 = torch.nn.ReLU()
        
        self.conv4 = torch.nn.Conv1d(conv3_channels, conv4_channels, kernel_size=conv4_kernel, stride=conv4_stride, padding=0) # padding was 3
        self.relu4 = torch.nn.ReLU()
        
        self.conv5 = torch.nn.Conv1d(conv4_channels, conv5_channels, kernel_size=conv5_kernel, stride=conv5_stride, padding=0) # padding was 3
        self.relu5 = torch.nn.ReLU()
        
        self.conv6 = torch.nn.Conv1d(conv5_channels, conv6_channels, kernel_size=conv6_kernel, stride=conv6_stride, padding=0) # padding was 3
        self.relu6 = torch.nn.ReLU()
        
        
        # compute output size to FC
        out_conv1 = self.compute_out_shape((H, W), (conv1_kernel, conv1_kernel), (conv1_stride, conv1_stride))
        out_pool1 = self.compute_out_shape(out_conv1, (pool1_kernel, pool1_kernel), (pool1_stride, pool1_stride))
        out_conv2 = self.compute_out_shape(out_pool1, (conv2_kernel, conv2_kernel), (conv2_stride, conv2_stride))
        out_pool2 = self.compute_out_shape(out_conv2, (pool2_kernel, pool2_kernel), (pool2_stride, pool2_stride))
        out_conv3 = self.compute_out_shape(out_pool2, (conv3_kernel, conv3_kernel), (conv3_stride, conv3_stride))
        out_pool3 = self.compute_out_shape(out_conv3, (pool3_kernel, pool3_kernel), (pool3_stride, pool3_stride))
        out_conv4 = self.compute_out_shape((out_pool3[0], out_pool3[1]), (conv4_kernel, conv4_kernel), (conv4_stride, conv4_stride))
        out_conv5 = self.compute_out_shape((out_conv4[0], out_conv4[1]), (conv5_kernel, conv5_kernel), (conv5_stride, conv5_stride))
        out_conv6 = self.compute_out_shape((out_conv5[0], out_conv5[1]), (conv5_kernel, conv5_kernel), (conv5_stride, conv5_stride))
        
        # init output layer
        self.fc = torch.nn.Linear(out_conv6[1]*32, 2*self.outputs)
        
        
    def compute_out_shape(self, I, k, s):
        out_H = floor(((I[0] - (k[0] - 1) - 1) / s[0]) + 1)
        out_W = floor(((I[1] - (k[1] - 1) - 1) / s[1]) + 1)
        return (out_H, out_W)
        
    def forward(self, x):
        
        if self.channels == 1:
            x = x[:,2,:,:].unsqueeze(1)
        elif self.channels == 2:
            x = x[:,1:3,:,:] 
        else:
            x = x[:,0:3,:,:]        
        x = torch.mean(x, dim=2)
        
        
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.relu1(x)

        x = self.conv2(x)
        x = self.pool2(x)
        x = self.relu2(x)

        x = self.conv3(x)
        x = self.pool3(x)
        x = self.relu3(x)
        
        x = self.conv4(x)
        x = self.relu4(x)
        
        x = self.conv5(x)
        x = self.relu5(x)
        
        x = self.conv6(x)
        x = self.relu6(x)

        x = x.flatten(1)
        x = self.fc(x)
        x = x.reshape(-1, self.outputs, 2)
        x = x.squeeze(1)

        return x
    
    
class FASTER_NN_grouped(torch.nn.Module):
    def __init__(self, H, W, outputs, channels):
        super(FASTER_NN_grouped, self).__init__()
        
        conv1_kernel = 3
        conv2_kernel = 3
        conv3_kernel = 3
        conv4_kernel = 6
        conv5_kernel = 6
        conv6_kernel = 6
        
        conv1_stride = 1
        conv2_stride = 1
        conv3_stride = 1
        conv4_stride = 2
        conv5_stride = 2
        conv6_stride = 2
        
        conv_channels = 32
        conv1_channels = conv_channels
        conv2_channels = conv_channels
        conv3_channels = conv_channels
        conv4_channels = conv_channels
        conv5_channels = conv_channels
        conv6_channels = conv_channels
        
        pool1_kernel = 2
        pool2_kernel = 2
        pool3_kernel = 2
        
        pool1_stride = 2
        pool2_stride = 2
        pool3_stride = 2
                
        self.outputs = outputs
        self.channels = channels
        self.groups = 16
        self.group_size = 8
        self.height = H
        self.conv1 = torch.nn.Conv1d(channels, conv1_channels, kernel_size=conv1_kernel, stride=conv1_stride, padding=0)
        self.pool1 = torch.nn.MaxPool1d(pool1_kernel, pool1_stride)
        self.relu1 = torch.nn.ReLU()
        
        self.conv2 = torch.nn.Conv1d(8+conv1_channels, conv2_channels, kernel_size=conv2_kernel, stride=conv2_stride, padding=0)
        self.pool2 = torch.nn.MaxPool1d(pool2_kernel, pool2_stride)
        self.relu2 = torch.nn.ReLU()
        
        self.conv3 = torch.nn.Conv1d(8+conv2_channels, conv3_channels, kernel_size=conv3_kernel, stride=conv3_stride, padding=0)
        self.pool3 = torch.nn.MaxPool1d(pool3_kernel, pool3_stride)
        self.relu3 = torch.nn.ReLU()
        
        self.conv4 = torch.nn.Conv1d(8+conv3_channels, conv4_channels, kernel_size=conv4_kernel, stride=conv4_stride, padding=0) # padding was 3
        self.relu4 = torch.nn.ReLU()
        
        self.conv5 = torch.nn.Conv1d(8+conv4_channels, conv5_channels, kernel_size=conv5_kernel, stride=conv5_stride, padding=0) # padding was 3
        self.relu5 = torch.nn.ReLU()
         
        self.conv6 = torch.nn.Conv1d(8+conv5_channels, conv6_channels, kernel_size=conv6_kernel, stride=conv6_stride, padding=0) # padding was 3
        self.relu6 = torch.nn.ReLU()
        
        # average pooling for groups
        self.avg_group_pool = torch.nn.AvgPool2d((self.group_size, 1), (self.height//self.groups, 1), padding=(0, 0))
        
        
        # compute output size to FC
        out_conv1 = self.compute_out_shape((H, W), (conv1_kernel, conv1_kernel), (conv1_stride, conv1_stride))
        out_pool1 = self.compute_out_shape(out_conv1, (pool1_kernel, pool1_kernel), (pool1_stride, pool1_stride))
        out_conv2 = self.compute_out_shape(out_pool1, (conv2_kernel, conv2_kernel), (conv2_stride, conv2_stride))
        out_pool2 = self.compute_out_shape(out_conv2, (pool2_kernel, pool2_kernel), (pool2_stride, pool2_stride))
        out_conv3 = self.compute_out_shape(out_pool2, (conv3_kernel, conv3_kernel), (conv3_stride, conv3_stride))
        out_pool3 = self.compute_out_shape(out_conv3, (pool3_kernel, pool3_kernel), (pool3_stride, pool3_stride))
        out_conv4 = self.compute_out_shape((out_pool3[0], out_pool3[1]), (conv4_kernel, conv4_kernel), (conv4_stride, conv4_stride))
        out_conv5 = self.compute_out_shape((out_conv4[0], out_conv4[1]), (conv5_kernel, conv5_kernel), (conv5_stride, conv5_stride))
        out_conv6 = self.compute_out_shape((out_conv5[0], out_conv5[1]), (conv5_kernel, conv5_kernel), (conv5_stride, conv5_stride))
        
        # init output layer
        self.fc = torch.nn.Linear(out_conv6[1]*conv6_channels, 2*self.outputs)
        
        # init group reduction layer
        self.group_mpool = torch.nn.MaxPool2d((self.groups, 1), (1, 1))
        self.group_apool = torch.nn.AvgPool2d((self.groups, 1), (1, 1))
        
        # batch normalization
        self.m1 = torch.nn.BatchNorm1d(self.conv1.out_channels)
        self.m2 = torch.nn.BatchNorm1d(self.conv2.out_channels)
        self.m3 = torch.nn.BatchNorm1d(self.conv3.out_channels)
        self.m4 = torch.nn.BatchNorm1d(self.conv4.out_channels)
        self.m5 = torch.nn.BatchNorm1d(self.conv5.out_channels)
        self.m6 = torch.nn.BatchNorm1d(self.conv6.out_channels)
        self.d1 = torch.nn.Dropout1d(p=0.3)
        
        
    def compute_out_shape(self, I, k, s):
        out_H = floor(((I[0] - (k[0] - 1) - 1) / s[0]) + 1)
        out_W = floor(((I[1] - (k[1] - 1) - 1) / s[1]) + 1)
        return (out_H, out_W)
    
    def cat_pool_channels(self, x):
        pool_channels = 4
        x_p = torch.reshape(x[:,:pool_channels,:], (x.shape[0]//self.groups, self.groups, pool_channels, x.shape[2]))
        x_p = torch.permute(x_p, (0, 2, 1, 3))
        x_m = self.group_mpool(x_p[:,:pool_channels,:,:]).repeat_interleave(self.groups, dim=2).permute(0,2,1,3).reshape((x.shape[0], pool_channels, x.shape[2]))
        x_a = self.group_apool(x_p[:,:pool_channels,:,:]).repeat_interleave(self.groups, dim=2).permute(0,2,1,3).reshape((x.shape[0], pool_channels, x.shape[2]))
        x_p = torch.cat((x[:, :, :], x_m, x_a), dim=1)
        return x_p
        
    def forward(self, x):
        
        if self.channels == 1:
            x = x[:,2,:,:].unsqueeze(1)
        elif self.channels == 2:
            x = x[:,1:3,:,:] 
        else:
            x = x[:,0:3,:,:] 
   
        x = self.avg_group_pool(x)
        x = torch.permute(x, (0, 2, 1, 3))
        x = torch.reshape(x, (x.shape[0]*self.groups, x.shape[2], x.shape[3]))       

        
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.relu1(x)
        x = self.m1(x)
        
        x = self.cat_pool_channels(x)

        x = self.conv2(x)
        x = self.pool2(x)
        x = self.relu2(x)
        x = self.m2(x)
        
        x = self.cat_pool_channels(x)

        x = self.conv3(x)
        x = self.pool3(x)
        x = self.relu3(x)
        x = self.m3(x)
        
        x = self.cat_pool_channels(x)
        
        x = self.conv4(x)
        x = self.relu4(x)
        x = self.m4(x)
        
        x = self.cat_pool_channels(x)
         
        x = self.conv5(x)
        x = self.relu5(x)
        x = self.m5(x)
        
        x = self.cat_pool_channels(x)
        
        x = self.conv6(x)
        x = self.relu6(x)
        x = self.m6(x)
        
        x = torch.reshape(x, (x.shape[0]//self.groups, self.groups, x.shape[1], x.shape[2]))
        x = torch.permute(x, (0, 2, 1, 3))
        x = self.group_apool(x).squeeze(2)

        x = x.flatten(1)
        x = self.fc(x)
        x = x.reshape(-1, self.outputs, 2)
        x = x.squeeze(1)

        return x
    
    
class SweepNetRecombination(torch.nn.Module):
    
    def __init__(self, H, W, outputs, channels):
        super(SweepNetRecombination, self).__init__()
        
        conv1_kernel = 3
        conv2_kernel = 3
        conv3_kernel = 3
        conv4_kernel = 3
        conv5_kernel = 3
        conv6_kernel = 3
        conv7_kernel = 3
        
        conv1_stride = 1
        conv2_stride = 1
        conv3_stride = 1
        conv4_stride = 1
        conv5_stride = 1
        conv6_stride = 1
        conv7_stride = 1
        
        conv1_channels = 32
        conv2_channels = 32
        conv3_channels = 32
        conv4_channels = 32
        conv5_channels = 32
        conv6_channels = 32
        conv7_channels = 32
        
        pool1_kernel = 1
        pool2_kernel = 1
        pool3_kernel = 1
        pool4_kernel = 1
        pool5_kernel = 1
        pool6_kernel = 1
        pool7_kernel = 1
        
        pool1_stride = 1
        pool2_stride = 1
        pool3_stride = 1
        pool4_stride = 1
        pool5_stride = 1
        pool6_stride = 1
        pool7_stride = 1
        
        self.outputs = outputs
        self.height = H
        self.width = W
        self.channels = channels
        
        self.conv1 = torch.nn.Conv1d(channels, conv1_channels, kernel_size=conv1_kernel, stride=conv1_stride, padding='same')
        self.pool1 = torch.nn.AvgPool1d(pool1_kernel, pool1_stride)
        self.relu1 = torch.nn.ReLU()
        
        self.conv2 = torch.nn.Conv1d(conv1_channels, conv2_channels, kernel_size=conv2_kernel, stride=conv2_stride, padding='same')
        self.pool2 = torch.nn.AvgPool1d(pool2_kernel, pool2_stride)
        self.relu2 = torch.nn.ReLU()
        
        self.conv3 = torch.nn.Conv1d(conv2_channels, conv3_channels, kernel_size=conv3_kernel, stride=conv3_stride, padding='same')
        self.pool3 = torch.nn.AvgPool1d(pool3_kernel, pool3_stride)
        self.relu3 = torch.nn.ReLU()
        
        self.conv4 = torch.nn.Conv1d(conv3_channels, conv4_channels, kernel_size=conv4_kernel, stride=conv4_stride, padding='same')
        self.pool4 = torch.nn.AvgPool1d(pool4_kernel, pool4_stride)
        self.relu4 = torch.nn.ReLU()
        
        self.conv5 = torch.nn.Conv1d(conv4_channels, conv5_channels, kernel_size=conv5_kernel, stride=conv5_stride, padding='same')
        self.pool5 = torch.nn.AvgPool1d(pool5_kernel, pool5_stride)
        self.relu5 = torch.nn.ReLU()
        
        self.conv6 = torch.nn.Conv1d(2*conv5_channels, conv6_channels, kernel_size=conv6_kernel, stride=conv6_stride, padding='same')
        self.pool6 = torch.nn.AvgPool1d(pool6_kernel, pool6_stride)
        self.relu6 = torch.nn.ReLU()
        
        self.conv7 = torch.nn.Conv1d(conv6_channels, conv7_channels, kernel_size=conv7_kernel, stride=conv7_stride, padding='same')
        self.pool7 = torch.nn.AvgPool1d(pool7_kernel, pool7_stride)
        self.relu7 = torch.nn.ReLU()
        
        # init output layers
        self.fc1 = torch.nn.Linear(conv5_channels, 32)
        self.out_relu = torch.nn.ReLU()
        self.fc2 = torch.nn.Linear(32, 32)
        self.out_relu2 = torch.nn.ReLU()
        self.out_pool = torch.nn.AvgPool1d(self.width)
        self.fc3 = torch.nn.Linear(32, 2*self.outputs)
        self.softmax = torch.nn.Softmax(dim=1)
        
        self.pool_hm = torch.nn.MaxPool2d((self.height, 1), return_indices=False)
        self.pool_ha = torch.nn.AvgPool2d((self.height, 1))

        self.m0 = torch.nn.BatchNorm1d(self.channels-1)
        self.m1 = torch.nn.BatchNorm1d(self.conv1.out_channels)
        self.m2 = torch.nn.BatchNorm1d(self.conv2.out_channels)
        self.m3 = torch.nn.BatchNorm1d(self.conv3.out_channels)
        self.m4 = torch.nn.BatchNorm1d(self.conv4.out_channels)
        self.m5 = torch.nn.BatchNorm1d(self.conv5.out_channels)
        self.m6 = torch.nn.BatchNorm1d(self.conv6.out_channels)
        self.m7 = torch.nn.BatchNorm1d(self.conv7.out_channels)
        self.m8 = torch.nn.BatchNorm1d(self.width)
        self.m9 = torch.nn.BatchNorm1d(self.width)
        
        self.d1 = torch.nn.Dropout1d(p=0.3)
        self.d2 = torch.nn.Dropout1d(p=0.3)
        self.d3 = torch.nn.Dropout1d(p=0.3)
        
    def forward(self, x):
        if self.channels == 1:
            x = x[:,2,:,:].unsqueeze(1) # get one b/w channel, keep channels dim
        elif self.channels == 2:
            x = x[:,1:3,:,:] # get one b/w channel and red depth channel
        else:
            x = x[:,0:3,:,:]
            
        batch = x.shape[0]
        x = torch.permute(x, (0, 2, 1, 3)).reshape(batch*self.height, self.channels, self.width)

        x = self.conv1(x)
        x = self.pool1(x)
        x = self.relu1(x)
        x = self.m1(x)
        
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.relu2(x)
        x = self.m2(x)
        
        x = self.conv3(x)
        x = self.pool3(x)
        x = self.relu3(x)
        x = self.m3(x)
        
        x = self.conv4(x)
        x = self.pool4(x)
        x = self.relu4(x)
        x = self.m4(x)
        
        x = self.conv5(x)
        x = self.pool5(x)
        x = self.relu5(x)
        x = self.m5(x)
        
        x = x.reshape(batch, self.height, self.conv3.out_channels, -1).permute(0,2,1,3)
        
        x_m = self.pool_hm(x).squeeze(2)
        x_a = self.pool_ha(x).squeeze(2)
        x = torch.cat((x_m, x_a), dim=1)
        
        x = self.conv6(x)
        x = self.pool6(x)
        x = self.relu6(x)
        x = self.m6(x)
        
        x = self.conv7(x)
        x = self.pool7(x)
        x = self.relu7(x)
        x = self.m7(x)
          
        x = torch.movedim(x, 1, -1)
        x = self.d1(x)
        x = self.fc1(x)
        x = self.out_relu(x)
        x = self.m8(x)
        x = self.d2(x)
        x = self.fc2(x)
        x = self.out_relu2(x)
        x = self.m9(x)
        x = torch.movedim(x, -1, 1)
        x = self.out_pool(x)
        x = x.flatten(1)
        x = self.d3(x)
        x = self.fc3(x)
        x = x.reshape(-1, self.outputs, 2)
        x = x.squeeze(1)

        return x
