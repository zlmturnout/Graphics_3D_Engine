import os,sys,time
from PIL import Image
import numpy as np

from collections import namedtuple
...
Color = namedtuple("Color", ["r", "g", "b", "alpha"])
Color.__doc__ = """A namedtuple that represents a color.
    It has 4 fields:
    r - red
    g - green
    b - blue
    alpha - the alpha channel
    """
...

def createIMGarray(w:int,h:int,channel:int=3):
    """Create a image 3D array for image data

    Args:
        w (int): width
        h (int): height
        channel (int, optional): channels,default RGB Defaults to 3. RGBa=4
    """
    return np.zeros(shape=(h,w,channel))

def put_pixel(img:np.array([]),x:int,y:int,color:Color):
    """put color into the image array at pos=(x,y) pixel

    Args:
        img (np.array): _description_
        x (int): pixel num of width
        y (int): pixel num of height
        color (Color): _description_
    """
    w,h,channel=img.shape
    Sx=int(w/2+x)
    Sy=int(h/2-y)
    r,g,b,a=tuple(color)
    if channel==3:
        img[Sx][Sy]=(r,g,b)
    elif channel==4:
        img[Sx][Sy]=(r,g,b,a)
...
"""canvas pos to viewport pos
    Field of view(FOV)
    Vx=Cx*Vw/Cw
    Vy=Cy*Vh/Ch
    Vz=d
    
"""
Vw=Vh=d=1
#canvas with=1280,height=720
Cw=1280
Ch=720

...
def CanvasToViewport(x:int,y:int):
    """

    Args:
        x (_type_): _description_
        y (_type_): _description_
    """
    return x*Vw/Cw,y*Vh/Ch,d

if __name__=="__main__":
    a=Color(r=255, g=0, b=0, alpha=255)
    im=Image.open("RayTracing/001.png")
    img_array=np.asarray(im).copy()
    
    put_pixel(img_array,0,0,a)
    im_cut=Image.fromarray(img_array[5:,0:],mode='RGB')
    
    im_cut.show()
    