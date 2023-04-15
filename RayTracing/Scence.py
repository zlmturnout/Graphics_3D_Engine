import os,sys,time
from collections import namedtuple
from PIL import Image
import numpy as np
from PutPixel import put_pixel,createIMGarray,BackgroundColor,Color

Point3D=namedtuple("Point3D",field_names=["x","y","z"])
PixelPos=namedtuple("PixelPos",field_names=["x","y"])
Sphere=namedtuple("sphere",field_names=["center","radius","color","ID"])


def piontToArray(point:Point3D):
    """transform a 3D point to np.array for vector calculation

    Args:
        point (Point3D): _description_
    """
    return np.array(point)

class Scence(object):
    
    def __init__(self) -> None:
        super(Scence,self).__init__()
        self.all_objects={} # {ID:namedtuple}
        self.object_num=0
    
    def add_object(self,object:namedtuple):
        ID=object.ID
        if ID not in self.all_objects:
            self.all_objects[ID]=object
            self.object_num+=1
            
    def remove_object(self,object_ID:str=None):
        if object_ID in self.add_objects:
            self.all_objects.pop(object_ID)
            self.object_num-=1

def CanvasToViewport(x:int,y:int,Cw:int=1280,Ch:int=720,Vw:int=1,Vh:int=1,d:int=1):
    """

    Args:
        x (_type_): _description_
        y (_type_): _description_
    """
    return Point3D(x*Vw/Cw,y*Vh/Ch,d)

"""
calculate the intersect between ray and sphere object
"""   

def Ray_intersect_Sphere(O:Point3D,D:Point3D,sphere:Sphere):
    """计算射线与球体的交点

    Args:
        O (Point3D): observation point(camera pos)
        D (Point3D): direction of ray D=(V-O)
        sphere (Sphere): sphereobject

    """
    O_vec=np.array(O)
    D_vec=np.array(D)
    r=sphere.radius
    center=sphere.center
    CO_vec=O_vec-np.array(center)
    # calculate intersection
    a=np.dot(D_vec,D_vec)
    b=2*np.dot(CO_vec,D)
    c=np.dot(CO_vec,CO_vec)-r**2

    dis=b*b-4*a*c
    if dis<0:
        return -1,-1
    else:
        t1=(-b+np.sqrt(dis))/2/a
        t2=(-b-np.sqrt(dis))/2/a
        return t1,t2

# ray tracing

def TraceRay(O:Point3D,D:Point3D,scence:Scence,t_min:int=1,t_max:int=100):
    """tray ray from O with direction D
    return the color of the pixel X and Y

    Args:
        O (Point3D): _description_
        D (Point3D): _description_
        t_min (int, optional): _description_. Defaults to 1.
        t_max (int, optional): _description_. Defaults to 100.
    """
    closest_t=1e10
    closest_shere=None
    for id,sphere in scence.all_objects.items():
        t1,t2=Ray_intersect_Sphere(O,D,sphere)
        if t1>t_min and t1<t_max and t1<closest_t:
            closest_t=t1
            closest_shere=sphere
        if t2>t_min and t2<t_max and t2<closest_t:
            closest_t=t2
            closest_shere=sphere
    if closest_shere==None:
        return BackgroundColor
    else:
        return Color(*closest_shere.color)

def CanvasPainting(O:Point3D,scence:Scence,Cw:int=1280,Ch:int=720):
    """paint the canvas of Cw*Ch,according to the rayTracing results 

    Args:
        O (Point3D): center of of the camera viewport
        Cw (int, optional): _description_. Defaults to 1280.
        Ch (int, optional): _description_. Defaults to 720.
    """
    Img_Render=createIMGarray(w=Cw,h=Ch)

    for x in np.arange(int(-Cw/2),int(Cw/2)):
        for y in np.arange(int(-Ch/2),int(Ch/2)):
            D=CanvasToViewport(x,y)
            pixel_color=TraceRay(O,D,scence)
            put_pixel(Img_Render,x,y,pixel_color)
    return Img_Render



if __name__=="__main__":
    s1=Sphere(center=Point3D(0,-1,3),radius=1,color=(255,0,0,0),ID="OS_01")
    s2=Sphere(center=Point3D(2,0,4),radius=1,color=(0,255,0,0),ID="OS_02")
    s3=Sphere(center=Point3D(-2,0,4),radius=1,color=(0,0,255,0),ID="OS_03")
    P1=Point3D(1,2,3)
    P0=Point3D(0,-1,0)
    Scence01=Scence()
    Scence01.add_object(s1)
    Scence01.add_object(s2)
    Scence01.add_object(s3)
    #t1,t2=Ray_intersect_Sphere(P0,P1,s2)
    #TraceRay(P0,P1,Scence01)
    #print(t1,t2)
    img_array=CanvasPainting(P0,Scence01,Cw=1000,Ch=1000)
    print(img_array)
    img=Image.fromarray(img_array.astype('uint8')).convert('RGB')
    img.save('RayTracing/render3DTest01.png')
    img.show()

    