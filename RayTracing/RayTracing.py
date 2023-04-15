import os,sys,time
from collections import namedtuple
from PIL import Image
import numpy as np
from PutPixel import put_pixel,createIMGarray,Color
from Scence import Scence,Point3D,Sphere,Light

BackgroundColor=Color(10,10,20,0.7)
def piontToArray(point:Point3D):
    """transform a 3D point to np.array for vector calculation

    Args:
        point (Point3D): _description_
    """
    return np.array(point)


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
    if dis<0 or dis==0:
        return -1,-1
    else:
        t1=(-b+np.sqrt(dis))/2/a
        t2=(-b-np.sqrt(dis))/2/a
        return t1,t2

# calculate intersection for shades
def Closestintersection(O:Point3D,D:Point3D,scence:Scence,t_min:int=1,t_max:int=100):
    closest_t=1e10
    closest_shere=None
    for id,sphere in scence.all_spheres.items():
        t1,t2=Ray_intersect_Sphere(O,D,sphere)
        if t1>t_min and t1<t_max and t1<closest_t:
            closest_t=t1
            closest_shere=sphere
        if t2>t_min and t2<t_max and t2<closest_t:
            closest_t=t2
            closest_shere=sphere
    return closest_shere,closest_t

# reflect rat=y
def ReflectRay(R:np.array([]),N:np.array([])):
    return 2*N*np.dot(N,R)-R

# ray tracing
def TraceRay(O:Point3D,D:Point3D,scence:Scence,t_min:int=1,t_max:int=100,rec_depth:int=3):
    """tray ray from O with direction D
    return the color of the pixel X and Y

    Args:
        O (Point3D): _description_
        D (Point3D): _description_
        t_min (int, optional): _description_. Defaults to 1.
        t_max (int, optional): _description_. Defaults to 100.
    """
    closest_shere,closest_t=Closestintersection(O,D,scence,t_min,t_max)
    if closest_shere==None:
        return BackgroundColor
    else:
        #return Color(*closest_shere.color)
        # calculate intersect point
        P=np.array(O)+closest_t*np.array(D)
        N=P-np.array(closest_shere.center)
        N=N/np.sqrt(np.dot(N,N))
        cal_color=np.array(closest_shere.color)*ComputeLighting(P,N,-np.array(D),scence,s=closest_shere.specular)
        #print(*pixel_color)
        local_color=RGBcolor(cal_color)

        r=closest_shere.reflective
        if rec_depth<=0 or r<=0:
            return local_color
        # calculate reflected color
        R=ReflectRay(-np.array(D),N)
        reflected_color=TraceRay(Point3D(*P),Point3D(*R),scence,0.001,1e10,rec_depth-1)
        #final composed color
        final_color=local_color*(1-r)+np.array(reflected_color)*r

        return Color(*final_color)


def RGBcolor(color:np.array([])):
    for i,value in enumerate(color[:-1]):
        if value<0:
            color[i]=0
        elif value>255:
            color[i]=255
    return color

# add lighting diffuse mirror reflection and shadows
def ComputeLighting(P:np.array([]),N:np.array([]),V:np.array([]),scence:Scence,s:float=-1):
    """compute the light intensity from Normal-line N at point P

    Args:
        P (np.array): P point
        N (np.array): Normal line direction vector N
        V (np.array): View direction V
        scence (Scence): SCENCE
        s (float, optional): Gloss index Defaults to -1.

    Returns:
        _type_: _description_
    """
    i=0
    t_max=1
    L=np.zeros(3) #3D xyz vector (x,y,z)
    # vector length
    N_length=np.sqrt(np.dot(N,N))
    V_length=np.sqrt(np.dot(V,V))
    for ID,light in scence.lights.items():
        if isinstance(light,Light):
            if light.type=="ambient":
                i+=light.intensity
            elif light.type=="point":
                L=np.array(light.position)-P
                t_max=1
            else:
                L=np.array(light.position)
                t_max=1e10
            # shadows
            P_3D=Point3D(*P)
            L_3D=Point3D(*L)
            shadow_sphere,shadow_t=Closestintersection(P_3D,L_3D,scence,0.001,t_max)
            if not shadow_sphere:
                continue

            # diffuse light
            n_dot_l=np.dot(N,L)
            L_length=np.sqrt(np.dot(L,L))
            if n_dot_l>0:
                i+=light.intensity*n_dot_l/N_length/L_length
            # mirror reflection s Gloss index
            if s!=-1:
                R=2*N*np.dot(N,L)-L
                R_length=np.sqrt(np.dot(R,R))
                r_dot_v=np.dot(R,V)
                if r_dot_v>0:
                    # no negative reflection
                    i+=light.intensity*np.power(r_dot_v/R_length/V_length,s)
    return i


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
    t_start=time.time()
    
    Scence_3D=Scence()
    s1=Sphere(center=Point3D(0,-1,3),radius=1,color=(255,0,0,255),specular=500,reflective=0.2,ID="OS_01")
    s2=Sphere(center=Point3D(2,0,4),radius=1,color=(0,255,0,255),specular=500,reflective=0.3,ID="OS_02")
    s3=Sphere(center=Point3D(-2,0,4),radius=1,color=(0,0,255,255),specular=10,reflective=0.5,ID="OS_03")
    Yellow_big=Sphere(center=Point3D(0,-5001,0),radius=5000,color=(155,125,0,255),specular=1000,reflective=0.5,ID="OY_00")
    P1=Point3D(1,2,3)
    P0=Point3D(0,0,0)
    #  add spheres
    Scence_3D.add_sphere(s1)
    Scence_3D.add_sphere(s2)
    Scence_3D.add_sphere(s3)
    Scence_3D.add_sphere(Yellow_big)
    # light setup
    l_01=Light("ambient",0.2,(0,0,0),"am_01") # ambient position=(0,0,0)
    l_02=Light("point",0.6,(2,1,0),"p_01")  # point light at pos
    l_03=Light("direction",0.2,(1,4,4),"p_01") # direction light direct/pos=(1,4,4)
    # add lights
    Scence_3D.add_light(l_01)
    Scence_3D.add_light(l_02)
    Scence_3D.add_light(l_03)

    #t1,t2=Ray_intersect_Sphere(P0,P1,s2)
    #TraceRay(P0,P1, Scence_3D)
    #print(t1,t2)
    width=1280
    height=720
    print(f'estimate time cost:{0.3*width*height/1000:.2f}s')
    img_array=CanvasPainting(P0,Scence_3D,Cw=width,Ch=height)
    #print(img_array)
    img=Image.fromarray(img_array.astype('uint8')).convert('RGB')
    img.save(f'RayTracing/render_img/render_3Dreflection_shadows_grey_{width}x{height}px.png')
    print(f'time cost:{time.time()-t_start:.4f}s with total {width}x{height} pixel\n\
          average timecost for each pixel: {(time.time()-t_start)/width/height*1000:.2f}ms ')
    img.show()
