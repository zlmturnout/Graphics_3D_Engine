import os,sys,time
from collections import namedtuple

Point3D=namedtuple("Point3D",field_names=["x","y","z"])
PixelPos=namedtuple("PixelPos",field_names=["x","y"])
Sphere=namedtuple("sphere",field_names=["center","radius","color","ID"])
Light=namedtuple("light",field_names=["type","intensity","position","ID"])

class Scence(object):
    
    def __init__(self) -> None:
        super(Scence,self).__init__()
        self.all_spheres={} # {ID:namedtuple}
        self.spheres_num=0
        self.lights={}
        self.lights_num=0
    
    def add_sphere(self,sphere:Sphere):
        ID=sphere.ID
        if ID not in self.all_spheres:
            self.all_spheres[ID]=sphere
            self.spheres_num+=1
            
    def remove_sphere(self,sphere_ID:str=None):
        if sphere_ID in self.all_spheres:
            self.all_spheres.pop(sphere_ID)
            self.spheres_num-=1
    
    def add_light(self,light:Light):
        ID=light.ID
        if ID not in self.lights:
            self.lights[ID]=light
            self.lights_num+=1
    
    def remove_light(self,light_ID:str=None):
        if light_ID in self.lights:
            self.lights.pop(light_ID)
            self.lights_num-=1
    

    