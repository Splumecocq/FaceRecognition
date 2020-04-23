# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:58:20 2020

@author: Simon.plumecocq

Next step: Zoom and dezomm, cf def doZoom
Afficher taille et scaling

"""
import os
import sys
print("Python version: "+sys.version) 
print(sys.path) 

import time

import tkinter as tk 
import tkinter.messagebox as msg
import tkinter.filedialog as dlg

print("TKinter version: "+str(tk.TkVersion))

import PIL 
print("PIL version: "+str(PIL.__version__))

from PIL import Image, ImageTk

import sklearn as sk
print("sklearn version: "+str(sk.__version__))

import cv2 as cv
print("OpenCv version: "+str(cv.__version__))

main_path = "C:\\Users\\Plumecocq\\Documents\\Python Scripts\\Video"
sys.path.append(main_path)
os.chdir(main_path)

import analyze.mtcnn_face_recognition as mtcnn_f_r

class MyVideoCapture:
    ''' Open the webcam and return frames '''
    def __init__(self, video_source=0):
        ''' Open the video source '''
        self.vid = cv.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv.CAP_PROP_FRAME_HEIGHT)

    def __del__(self): 
        ''' Release the video source when the object is destroyed '''
        print('Delete MyVideoCapture')
        if self.vid.isOpened():
            self.vid.release()
            cv.destroyAllWindows()
        #self.window.mainloop()

    def get_frame(self):
        ''' Return the next frame of the Video '''
        ret1  = None
        ret2 = None
        if self.vid.isOpened():
            ret1, frame = self.vid.read()
            if ret1:
                ret2 = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return (ret1, ret2)

class ImagesInterface(tk.Tk):
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.menuBar = tk.Menu(self)
        self.createMenuBar()
        self.geometry("300x200")
        self.init_title = "Operation on Image"
        self.title(self.init_title)

        #For images
        self.canvas = []
        self.images = []
        self.labels = []
        
        #For scaling
        self.x_max = 300
        self.scale = []
        
        #For selection
        self.x = []
        self.y = []
        self.selection = []
        
        #For video
        self.video_source = 0
        self.delay = 2
        # open video source
        self.video_actif = False
        self.vid = None
        self.photo = None
        self.imgs_time = []
        
        self.video_analyse = None
        
        self.mainloop()
        
    def createMenuBar(self):
               
        menuInput = tk.Menu(self.menuBar, tearoff=0)
        menuInput.add_command(label="Open Image", command=self.openFile)
        menuInput.add_separator()
        menuInput.add_command(label="Open Cam", command=self.openCam)
        self.menuBar.add_cascade( label="Input", menu=menuInput)
        
        self.createMenuImage()
        self.createMenuVideo()
        
        menuHelp = tk.Menu(self.menuBar, tearoff=0)
        menuHelp.add_command(label="About", command=self.doAbout)
        self.menuBar.add_cascade( label="Help", menu=menuHelp)

        menuQuit = tk.Menu(self.menuBar, tearoff=0)
        '''menuQuit.add_command(label="Quit", command=self.destroy)'''
        menuQuit.add_command(label="Quit", command=self._quit)
        self.menuBar.add_cascade( label="Quit", menu=menuQuit)
        
        self.config(menu = self.menuBar)
          

    def createMenuImage(self, state_mi=tk.DISABLED):
        menuImage = tk.Menu(self.menuBar, tearoff=0)
        menuImage.add_command(label="Remove the last image", command=self.doRemoveLast)
        menuImage.add_command(label="Save the last image", command=self.saveFile)       
        menuImage.add_separator()
        menuImage.add_command(label="Selection", command=self.doSelect)
        menuImage.add_command(label="Create from Selection", command=self.doSelectCreate)
        menuImage.add_separator()
        menuImage.add_command(label="Zoom", command=self.doZoom)
        menuImage.add_command(label="Translate", command=self.doSomething)
        menuImage.add_separator()
        menuImage.add_command(label="Grey", command=self.doGrey)
        menuImage.add_command(label="Canny Border", command=self.doSomething)
        self.menuBar.add_cascade( label="Image Action", menu=menuImage, state=state_mi)
    
    def createMenuVideo(self, state_mv=tk.DISABLED):
        menuVideo = tk.Menu(self.menuBar, tearoff=0)
        menuVideo.add_command(label="Break/Read", command=self.doVideoPause)
        menuVideo.add_command(label="SSD", command=self.doSomething)
        menuVideo.add_command(label="YOLO", command=self.doSomething)
        menuVideo.add_command(label="MTCNN", command=self.doAnalyseMTCNN)
        self.menuBar.add_cascade( label="Video Action", menu=menuVideo, state=state_mv)
    
    def ableMenuImage(self):
        self.menuBar.entryconfigure(2,state=tk.NORMAL)
    
    def disableMenuImage(self):
        self.menuBar.entryconfigure(2,state=tk.DISABLED)
        
    def ableMenuVideo(self):
        self.menuBar.entryconfigure(3,state=tk.NORMAL)
    
    def disableMenuVideo(self):
        self.menuBar.entryconfigure(3,state=tk.DISABLED)
              
    def openFile(self):
        file = dlg.askopenfilename(title="Choose the file to open", 
                filetypes=[("JPG image", ".jpg"),("PNG image", ".png"), ("GIF image", ".gif"), ("All files", ".*")])
        if len(file) > 0:
            print(file)
            self.clean()
            monImage = Image.open(file)
            self.images.append(monImage)
            width, height = monImage.size
            print('Size: '+str(width)+'-'+str(height))
            if width > self.x_max:
                x_size = self.x_max
                self.scale.append(self.x_max/width)
                y_size = int(height*self.x_max/width)
                monImage = monImage.resize((x_size,y_size))     
            else:
                x_size = width
                y_size = height
                self.scale.append(1)           
            label_init = "Init size : "+str(width)+","+str(height) 
            label_show = "Show size : "+str(x_size)+","+str(y_size)
            label_tot = label_init+"   "+label_show
            print(label_tot)
            self.showImage(monImage, label_tot)
            self.ableMenuImage()
            self.disableMenuVideo()
    
    def clean(self):
        self.video_actif = False
        self.images = []
        self.scale = []
        for canvas in self.canvas:
            canvas.grid_forget()
            canvas.delete()
        self.canvas = []
        self.title(self.init_title)
    
    def showImage(self, monImage, monLabel):
        photo = ImageTk.PhotoImage(monImage, master=self)
        canvas = tk.Canvas(self)
        self.canvas.append(canvas)
        x_size, y_size = monImage.size
        canvas.create_image(x_size/2, y_size/2, anchor=tk.CENTER,image=photo)
        canvas.image = photo
        label_canvas = tk.Label(self,text=monLabel)
        self.labels.append(label_canvas)
        label_canvas.grid(row=0, column=len(self.canvas)-1,sticky="w")
        canvas.grid(row=1, column=len(self.canvas)-1)
        self.resize()
    
    def openCam(self):
        self.clean()
        self.video_actif = True
        if self.vid is None:
            self.vid = MyVideoCapture(self.video_source)
        canvas = tk.Canvas(self, width=self.vid.width, height=self.vid.height)
        print("openCam: "+str(self.vid.width)+" "+str(self.vid.height))
        self.geometry(str(int(self.vid.width+20))+"x"+str(int(self.vid.height+20)))
        self.canvas.append(canvas)
        canvas.grid(row=0, column=0)
        self.images.append("One image")
        self.disableMenuImage()
        self.ableMenuVideo()
        self.update()

    def update(self):
        ''' Get a frame from the video source '''
        if self.video_actif:
            #print("update ok 0")
            ret, frame = self.vid.get_frame()
            self.imgs_time.append([time.time()])
            if len(self.imgs_time)%10 == 0 and len(self.imgs_time) > 10:
                fps = 0
                last_time = self.imgs_time[-1][0]
                prev_time = self.imgs_time[-11][0]
                if prev_time != last_time:
                    fps = round(10.0/(last_time - prev_time), 2)
                self.title(self.init_title+"  FPS:"+str(fps))
                if not (self.video_analyse is None):
                    self.video_analyse.show_fps(str(fps))
            if ret:
                #print("update ok 1")
                self.images[0] = Image.fromarray(frame)
                if not (self.video_analyse is None):
                    self.images[0] = self.video_analyse.analyse(self.images[0])        
                self.photo = ImageTk.PhotoImage(image=self.images[0], master=self)
                self.canvas[0].create_image(1, 0, image=self.photo, anchor=tk.NW)
            self.after(self.delay, self.update)
        else:
            print("No Video Capture")

    def doVideoPause(self):
        self.video_actif = not(self.video_actif)
        if self.video_actif:
            self.update()

    def doAnalyseMTCNN(self):
        self.video_analyse = mtcnn_f_r.MtcnnFaceRecognition(self)
    
    def closeVideoAnalyse(self):
        self.video_analyse = None
        
    def resize(self):
        if len(self.canvas)>0:
            self.geometry(str(len(self.canvas)*(self.x_max+50))+"x200" )
        else:
            self.geometry("300x200")
            
    def saveFile(self):
        file = dlg.asksaveasfile(mode='w',
                filetypes=[("JPG image", ".jpg"),("PNG image", ".png"), ("GIF image", ".gif"), ("All files", ".*")])
        if file:
            self.images[-1].save(file)
            print("Save "+file)
            
    def doGrey(self):
        print('Grey')
        monImage = self.images[-1]
        monImage = monImage.convert(mode="L")
        self.images.append(monImage)
        width, height = monImage.size
        if width > self.x_max:
            x_size = self.x_max
            self.scale.append(self.x_max/width)
            y_size = int(height*self.x_max/width)
            monImage = monImage.resize((x_size,y_size))     
        else:
            x_size = width
            y_size = height
            self.scale.append(1)
        label_init = "Init size : "+str(width)+","+str(height) 
        label_show = "Show size : "+str(x_size)+","+str(y_size)
        label_tot = label_init+"   "+label_show
        self.showImage(monImage, label_tot)
            
    def doRemoveLast(self):
        print("Remove last image")
        if len(self.images) > 0:
            self.images.pop()
            self.canvas[-1].grid_forget()
            self.canvas[-1].delete()
            self.canvas.pop()
            self.labels[-1].grid_forget()
            #self.labels[-1].delete()
            self.labels.pop()
            self.scale.pop()
            if len(self.images) == 0:
                self.disableMenuImage()
            self.resize()
        else:
            print("No image")
        
    def selectClick(self, event):
        print("Clicked at "+str(event.x)+" "+str(event.y))
        self.x.append(event.x)
        self.y.append(event.y)
        
    def selectEnd(self, event):
        print("Released at "+str(event.x)+" "+str(event.y))
        self.x.append(event.x)
        self.y.append(event.y)
        
    def selectMotion(self, event):
        #print("Motion at "+str(event.x)+" "+str(event.y))
        monCanvas = self.canvas[-1]
        if len(self.selection)> 0 :
            monCanvas.delete(self.selection[-1])
        selection = monCanvas.create_rectangle(self.x[-1],self.y[-1],event.x, event.y, outline='white')
        self.selection.append(selection)
        
    def doSelect(self):
        print('Select')
        monCanvas = self.canvas[-1]
        monCanvas.bind("<Button-1>", self.selectClick)
        monCanvas.bind("<ButtonRelease-1>", self.selectEnd)
        monCanvas.bind("<B1-Motion>", self.selectMotion)
        
    def stopSelect(self):
        monCanvas = self.canvas[-1]
        monCanvas.unbind("<Button-1>")
        monCanvas.unbind("<ButtonRelease-1>")
        monCanvas.unbind("<B1-Motion>")
        
    def doSelectCreate(self):
        print('Create from Selection')
        self.stopSelect()
        if len(self.x) >=2:
            area = [self.x[-2],self.y[-2],self.x[-1],self.y[-1]]
            print(area)
            monImage = self.images[-1]
            monScale = self.scale[-1]   
            print(monScale)
            if monScale != 1:
                for index_coord, coord in enumerate(area):
                    area[index_coord] = int(coord / monScale)
            print(area)
            monImage = monImage.crop(area)
            self.images.append(monImage)
            
            width, height = monImage.size
            if width > self.x_max:
                x_size = self.x_max
                self.scale.append(self.x_max/width)
                y_size = int(height*self.x_max/width)
                monImage = monImage.resize((x_size,y_size))     
            else:
                x_size = width
                y_size = height
                self.scale.append(1)
            label_init = "Init size : "+str(width)+","+str(height) 
            label_show = "Show size : "+str(x_size)+","+str(y_size)
            label_tot = label_init+"   "+label_show
            self.showImage(monImage, label_tot)
        else:
            print('Do a selection')
    
    def doZoom(self):
        print("Do a zoom")
        #window = ZoomWindow(self)
        self.zoom(200)
        
    def doSomething(self):
        print("Available in next version")

    def doAbout(self):
        msg.showinfo("About", "Produced by S.Plumecocq Jan 2020")

    def _quit(self):
        self.video_actif = False
        del self.vid
        self.quit()
        self.detroy()

    def zoom(self, zomm_scale=100):
        print("Zoom at scale: "+str(zomm_scale))


def test_interface():
    ImagesInterface()


