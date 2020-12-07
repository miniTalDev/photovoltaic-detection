import torch.utils.data as data
from torchvision.transforms import transforms
import glob
import numpy as np
import os
from PIL import Image
import torch
import random
from process_data.data_loader import flip, normalization2
import matplotlib.pyplot  as plt
import cv2


class DataLoaderNoARA(data.Dataset):
    """
    load noPV data, only pictures and  mask are all 0(black)
    """
    def __init__(self, folder_path_img):
        """
        Args:
            image_path (str): the path where the image is located
            option (str): decide which dataset to import
        """
        self.img_files = glob.glob(os.path.join(folder_path_img,'*.png'))

        
    def __getitem__(self, index):
        """Get specific data corresponding to the index applying randomly dat augmentation
        Args:
            index (int): index of the data
        Returns:
            Tensor: specific data on index which is converted to Tensor
        """
        
        """
        # GET IMAGE
        """
        image = Image.open(self.img_files[index])
        img_as_np = np.asarray(image)
        np.random.seed(0)

        # AUGMENTATION
        
        # flip {0: vertical, 1: horizontal, 2: both, 3: none}
        flip_num = random.randint(0, 3)         
        img_as_np = flip(img_as_np, flip_num)
        # rotate of rot_num*90 degrees in counterclockwise
        # since we are altready flipping, rotating of 180 or 270 is redundant
        rot_num = random.randint(0, 1)
        img_as_np = np.rot90(img_as_np, rot_num)
        # add noise {0: Gaussian_noise, 1: uniform_noise, 2: no_noise}
        #noise_num = random.randint(0, 2)
        #noise_param = 20
        #img_as_np = add_noise(img_as_np, noise_num, noise_param)
        # Brightness and Saturation
        sat = random.randint(0,75)
        bright = random.randint(0,40)
        img_as_np = change_hsv(img_as_np, sat, bright)
       
        # Convert numpy array to tensor
        img_as_np = np.transpose(img_as_np,(2,0,1))
        img_as_tensor = torch.from_numpy(img_as_np).float()  
        


        """
        # GET noPv MASK All balck
        """

        #Cut channel for binary pictures
        mask_shape = (img_as_np.shape[1],img_as_np.shape[2]) 
        mask = np.zeros(mask_shape)
        
        # Convert numpy array to tensor
        msk_as_tensor =  torch.tensor(mask, dtype = torch.float)
        
        return img_as_tensor, msk_as_tensor

    def __len__(self):
        return len(self.img_files)






def change_hsv(image, sat, bright):
    """
    Args:
        image : numpy array of image
        sat: saturation
        bright : brightness
    Return :
        image : numpy array of image with saturation and brightness added
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    for i in range(s.shape[0]):
        for j in range(s.shape[1]):
            s[i,j]=min(s[i,j]+sat,255)
            v[i,j]=min(v[i,j]+bright,255)
    final_hsv = cv2.merge((h, s, v))
    image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return image
    
    
    
    
    
    
def flip(image, option_value):
    """
    Args:
        image : numpy array of image
        option_value = random integer between 0 to 3
    Return :
        image : numpy array of flipped image
    """
    

    if option_value == 0:
        # vertical
        image = np.flip(image, option_value)
    elif option_value == 1:
        # horizontal
        image = np.flip(image, option_value)
    elif option_value == 2:
        # horizontally and vertically flip
        image = np.flip(image, 0)
        image = np.flip(image, 1)
    else:
        # no effect
        image = image     
    return image


def normalization2(image, max, min):
    """Normalization to range of [min, max]
    Args :
        image : numpy array of image
        mean :
    Return :
        image : numpy array of image with values turned into standard scores
    """
    image_new = (image - np.min(image))*(max - min)/(np.max(image)-np.min(image)) + min
    return image_new

def add_noise(image, option_value, param):
    if option_value==0:
        # Gaussian_noise
        gaus_sd, gaus_mean = random.randint(0, param), 0
        image = add_gaussian_noise(image, gaus_mean, gaus_sd)
    elif option_value==1:
        # uniform_noise
        l_bound, u_bound = random.randint(-param, 0), random.randint(0, param)
        image = add_uniform_noise(image, l_bound, u_bound)
    else:
        # no noise
        image = image
    return image       

def add_uniform_noise(image, low=-10, high=10):
    """
    Args:
        image : numpy array of image
        low : lower boundary of output interval
        high : upper boundary of output interval
    Return :
        image : numpy array of image with uniform noise added
    """
    uni_noise = np.random.uniform(low, high, image.shape)
    image = image.astype("int16")
    noise_img = image + uni_noise
    image = ceil_floor_image(image) 
    return noise_img

def add_gaussian_noise(image, mean=0, std=1):
    """
    Args:
        image : numpy array of image
        mean : pixel mean of image
        standard deviation : pixel standard deviation of image
    Return :
        image : numpy array of image with gaussian noise added
    """
    gaus_noise = np.random.normal(mean, std, image.shape)
    image = image.astype("int16")
    noise_img = image + gaus_noise
    image = ceil_floor_image(image)
    return noise_img

def ceil_floor_image(image):
    """
    Args:
        image : numpy array of image in datatype int16
    Return :
        image : numpy array of image in datatype uint8 with ceilling(maximum 255) and flooring(minimum 0)
    """
    image[image > 255] = 255
    image[image < 0] = 0
    image = image.astype("uint8")
    return image
