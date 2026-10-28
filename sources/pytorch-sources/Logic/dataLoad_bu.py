import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets.folder import has_file_allowed_extension
import os
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Union
from torch.utils.data import random_split
import numpy as np

def snp_file_loader_prev(path):
        data = np.memmap(path, mode='r+').tobytes()
        ints_per_col = np.frombuffer(data, dtype=np.uint16, offset=0, count=1)[0]
        num_cols = np.frombuffer(data, dtype=np.int32, offset=2, count=1)[0]
        target_pos = np.frombuffer(data, dtype=np.float64, offset=6, count=1)[0]
        
        snp_data = np.unpackbits(np.frombuffer(data, dtype=np.uint8, offset=14, count=ints_per_col*num_cols))
        snp_matrix = snp_data.reshape((ints_per_col*8, num_cols), order='F')
        snp_tensor = torch.from_numpy(snp_matrix).float()
        
        bp_array = np.frombuffer(data, dtype=np.float64, offset=14+ints_per_col*num_cols, count=num_cols)
        bp_tensor = torch.from_numpy(bp_array.copy())
        bp_tensor = torch.broadcast_to(bp_tensor, snp_tensor.shape)
        
        sample = torch.stack([bp_tensor, bp_tensor, snp_tensor], dim=0).float()
        sample = sample[:, 0:20, :]
        return sample, target_pos
        
def snp_file_loader(path):
        data = np.memmap(path, mode='r+').tobytes()
        num_samples = np.frombuffer(data, dtype=np.int32, offset=0, count=1)[0]
        ints_per_col = int(np.ceil(num_samples / 8))
        num_cols = np.frombuffer(data, dtype=np.int32, offset=4, count=1)[0]
        target_pos = np.frombuffer(data, dtype=np.float64, offset=8, count=1)[0]
       # print(num_samples)
       # print(ints_per_col)
       # print(num_cols)

        snp_data = np.unpackbits(np.frombuffer(data, dtype=np.uint8, offset=16, count=ints_per_col*num_cols))
        snp_matrix = snp_data.reshape((ints_per_col*8, num_cols), order='F')

        snp_matrix = snp_matrix[:num_samples, :]
        # print(snp_matrix.shape)
        snp_tensor = torch.from_numpy(snp_matrix).float()

        bp_array = np.frombuffer(data, dtype=np.float64, offset=16+ints_per_col*num_cols, count=num_cols)
        bp_tensor = torch.from_numpy(bp_array.copy())
        bp_tensor = torch.broadcast_to(bp_tensor, snp_tensor.shape)

        sample = torch.stack([bp_tensor, bp_tensor, snp_tensor], dim=0).float()
       # print(sample.shape)
        return sample, target_pos
        
        
def snp_file_loader_1d(path):
    data = np.memmap(path, mode='r+').tobytes()
    num_cols = np.frombuffer(data, dtype=np.int32, offset=0, count=1)[0]
    target_pos = np.frombuffer(data, dtype=np.float64, offset=4, count=1)[0]
   
    snp_data = np.frombuffer(data, dtype=np.float32, offset=12, count=num_cols).astype(np.float32)
    snp_tensor = torch.from_numpy(snp_data.copy()).float()   

    bp_array = np.frombuffer(data, dtype=np.float64, offset=12+(num_cols*4), count=num_cols)
    bp_tensor = torch.from_numpy(bp_array.copy())
    bp_tensor = torch.broadcast_to(bp_tensor, snp_tensor.shape)   

    sample = torch.stack([bp_tensor, bp_tensor, snp_tensor], dim=0).float()
    sample = sample.unsqueeze(1)
    return sample, target_pos

def snp_file_loader_1d_bu(path):
    data = np.memmap(path, mode='r+').tobytes()
    num_cols = np.frombuffer(data, dtype=np.int32, offset=0, count=1)[0]
    target_pos = np.frombuffer(data, dtype=np.float64, offset=4, count=1)[0]   

    snp_data = np.frombuffer(data, dtype=np.uint64, offset=12, count=num_cols).astype(np.int64)
    snp_tensor = torch.from_numpy(snp_data.copy()).float()   

    bp_array = np.frombuffer(data, dtype=np.float64, offset=12+(num_cols*8), count=num_cols)
    bp_tensor = torch.from_numpy(bp_array.copy())
    bp_tensor = torch.broadcast_to(bp_tensor, snp_tensor.shape)   

    sample = torch.stack([bp_tensor, bp_tensor, snp_tensor], dim=0).float()
    sample = sample.unsqueeze(1)
    sample[2,:,:] = sample[2,:,:]/128 # todo fix this
    return sample, target_pos
    
class shuffleDim(torch.nn.Module):

    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, img):
        rand_indices = torch.randperm(img.shape[self.dim])
        img = torch.index_select(img, self.dim, rand_indices)
        return img

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(dim={self.dim})"
    
    
class CustomImageFolder(torchvision.datasets.DatasetFolder):
    
    def __init__(self, root, load_binary, transform, mix_images, train_detect, reduction):
        #print("using ", root,"\n")
        if load_binary:
            extensions = (".snp",)
            if reduction:
                loader = snp_file_loader_1d
            else:
                loader = snp_file_loader
        else:
            extensions = (".png",)
            loader = torchvision.datasets.folder.default_loader
            
        super().__init__(root, transform=transform, extensions=extensions, loader=loader)
        self.mix_images = mix_images
        self.load_binary = load_binary
        self.train_detect = train_detect
    
    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        
        path, target = self.samples[index]
        if self.load_binary:
            sample, target_pos = self.loader(path)
            sample[0:2, :, :] = sample[0:2, :, :] / 200.0
        else:
            sample = self.loader(path)
        
        if self.transform is not None:
            sample = self.transform(sample)
        if self.target_transform is not None:
            target = self.target_transform(target)
            
        # if self.mix_images:
        #     new_path, new_target = self.samples[np.random.randint(0, len(self.samples))]
        #     if new_target != target:
        #         sel_class = self.class_to_idx['sel']
        #         combine_ratio = np.random.randint(1, sample.shape[2])
        #         new_sample = self.transform(self.loader(new_path))
                
        #         # temporary implementation of loading full bp distances    
        #         bp_dist_path = new_path[:-3] + "txt"
        #         bp_dist_file = open(bp_dist_path, "r")
        #         bp_dist_list = np.asarray(bp_dist_file.readlines())
        #         bp_dist_list = bp_dist_list.astype(float)
        #         bp_dist_list = np.broadcast_to(bp_dist_list, new_sample[0].shape)
        #         bp_dist_tensor = torch.tensor(bp_dist_list)
        #         new_sample[0] = bp_dist_tensor
        #         new_sample[1] = bp_dist_tensor

        #         sample[:, :, :combine_ratio] = new_sample[:, :, :combine_ratio]
                    
        #         target = torch.nn.functional.one_hot(torch.tensor(target), num_classes=2)
        #         new_target = torch.nn.functional.one_hot(torch.tensor(new_target), num_classes=2)
                
        #         target = target * (1 - (combine_ratio/new_sample.shape[2]))
        #         new_target = new_target * (combine_ratio/new_sample.shape[2])
                    
        #         target = target + new_target
        #     else:
        #         target = torch.nn.functional.one_hot(torch.tensor(target), num_classes=2)    
        if self.train_detect:
            target_oh = torch.nn.functional.one_hot(torch.tensor(target), num_classes=2).float()
            if target == self.class_to_idx['sel']:
                target_oh[target] = max(1-abs(33.33*(0.5-(target_pos/100000))), 0) # decays linearly from center
                target_oh[self.class_to_idx['neu']] = 1 - target_oh[target]
            target = target_oh

        return path, sample, target
    
class DoubleLabelImageFolder(CustomImageFolder):   

    def __init__(self, root, load_binary, transform, mix_images, train_detect, reduction, label_names):
        self.label_names = label_names
        super().__init__(root, load_binary, transform, mix_images, train_detect, reduction)
   

    def find_classes(self, directory):
        class_to_idx = {}   
        for i, sub_labels in enumerate(self.label_names):
            for j, label_name in enumerate(sub_labels):
                class_to_idx.update({label_name : (i, j)}) 

        return list(class_to_idx.keys()), class_to_idx
        
            
class NoClassImageFolder(CustomImageFolder):

    def __init__(self, root, load_binary, transform, mix_images, train_detect, reduction, hotspot):
        self.hotspot = hotspot
        super().__init__(root, load_binary, transform, mix_images, train_detect, reduction)

    def find_classes(self, directory: str) -> Tuple[List[str], Dict[str, int]]:
        if self.hotspot:
            class_to_idx = {'generic': (0,0)}
            return ((0,0),), class_to_idx
        else:
            class_to_idx = {'generic': 0}
            return (0,), class_to_idx

    def make_dataset(
        self,
        directory: str,
        class_to_idx: Optional[Dict[str, int]] = None,
        extensions: Optional[Union[str, Tuple[str, ...]]] = None,
        is_valid_file: Optional[Callable[[str], bool]] = None,
    ) -> List[Tuple[str, int]]:
        """Generates a list of samples of a form (path_to_sample, class).

        See :class:`DatasetFolder` for details.

        Note: The class_to_idx parameter is here optional and will use the logic of the ``find_classes`` function
        by default.
        """
        directory = os.path.expanduser(directory)

        if class_to_idx is None:
            _, class_to_idx = self.find_classes(directory)
        elif not class_to_idx:
            raise ValueError("'class_to_index' must have at least one entry to collect any samples.")

        both_none = extensions is None and is_valid_file is None
        both_something = extensions is not None and is_valid_file is not None
        if both_none or both_something:
            raise ValueError("Both extensions and is_valid_file cannot be None or not None at the same time")

        if extensions is not None:

            def is_valid_file(x: str) -> bool:
                return has_file_allowed_extension(x, extensions)  # type: ignore[arg-type]

        is_valid_file = cast(Callable[[str], bool], is_valid_file)

        instances = []
        available_classes = set()
        for target_class in sorted(class_to_idx.keys()):
            class_index = class_to_idx[target_class]
            target_dir = directory
            if not os.path.isdir(target_dir):
                continue
            for root, _, fnames in sorted(os.walk(target_dir, followlinks=True)):
                for fname in sorted(fnames):
                    path = os.path.join(root, fname)
                    if is_valid_file(path):
                        item = path, class_index
                        instances.append(item)

                        if target_class not in available_classes:
                            available_classes.add(target_class)

        empty_classes = set(class_to_idx.keys()) - available_classes
        if empty_classes:
            msg = f"Found no valid file for the classes {', '.join(sorted(empty_classes))}. "
            if extensions is not None:
                msg += f"Supported extensions are: {extensions if isinstance(extensions, str) else ', '.join(extensions)}"
            raise FileNotFoundError(msg)

        return instances
    


def get_loader(data_path, batch_size, class_folders, shuffle, load_binary, shuffle_row, mix_images, validation, train_detect, reduction, hotspot, label_names):
    
    transform_list = []
    if not load_binary:
        transform_list.append(transforms.ToTensor())
    
    if shuffle_row:
        transform_list.append(shuffleDim(1))
    
    transform = transforms.Compose(transform_list)
    
    if not class_folders:
        dataset = NoClassImageFolder(root=data_path, load_binary=load_binary, transform=transform, mix_images=mix_images, train_detect=train_detect, reduction=reduction, hotspot=hotspot)
    else:
        if not hotspot:
            dataset = CustomImageFolder(root=data_path, load_binary=load_binary, transform=transform, mix_images=mix_images, train_detect=train_detect, reduction=reduction)
        else:
            dataset = DoubleLabelImageFolder(root=data_path, load_binary=load_binary, transform=transform, mix_images=mix_images, train_detect=train_detect, reduction=reduction, label_names=label_names)
        
    # added to filter training samples for detection training
    # if train_detect:
    #     idx = [i for i in range(len(dataset)) if 45 < int(os.path.split(dataset.samples[i][0])[1].split('_')[1]) < 55]
    #     dataset = torch.utils.data.Subset(dataset, idx)
        
    if validation:
        (dataset, val_set) = random_split(dataset, [0.85, 0.15]) # , torch.Generator().manual_seed(90)
        val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size,
                                            shuffle=shuffle, num_workers=0)
        
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size,
                                            shuffle=shuffle, num_workers=0)
    
    if validation:
        return dataloader, val_loader
    else:
        return dataloader, None
