from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import Canvas,Tk,ttk,Label,Entry,Button,mainloop,Text,Frame,IntVar,Checkbutton,Radiobutton
import os
import numpy as np
from tkinter import filedialog
import math
import random
import time
from fractions import Fraction
from decimal import Decimal

class Display:
    def __init__(self, parent):
        self.parent = parent
        self.main_font = ("Courier", 22, "bold")
        self.max_win_size = (1200,700)
        self.canvas_dimension = 500
        self.canvas_size = (int(1199/520*self.canvas_dimension),self.canvas_dimension)
        self.image_size = (3840,2160)
        self.canvas_image_counter = 0
        self.im = {}
        self.setup_window()
        self.boring_state_detected_at = 0
        self.circles_drawn = False
        self.series_frame = 0
        self.spirographs_drawn = 0
    def pause_toggle(self): 
        if self.pause.get() == 2: # pause
            open("data/pause",'w+').close()
            self.pause.set(1)
        elif self.pause.get() == 1: # unpause
            if os.path.isfile('data/pause'):
                os.remove("data/pause")
            self.pause.set(2)
    def stop(self,end=True):
        if not os.path.isfile('data/stop'):
            open("data/stop",'w+').close()
        if self.status_entry.get() != "Drawing...":
            # self.the_canvas.delete("all")
            if os.path.isfile('data/stop'):
                os.remove('data/stop')
    def open_images(self):
        pil_img = Image.open('source/play.gif').resize((80,80), Image.ANTIALIAS)
        self.play_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/pause.gif').resize((80,80), Image.ANTIALIAS)
        self.pause_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/close.gif').resize((80,80), Image.ANTIALIAS)
        self.close_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/accept.gif').resize((80,80), Image.ANTIALIAS)
        self.accept_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/refresh.gif').resize((80,80), Image.ANTIALIAS)
        self.update_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/random.gif').resize((80,80), Image.ANTIALIAS)
        self.random_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/trash.gif').resize((80,80), Image.ANTIALIAS)
        self.trash_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/pause_play.gif').resize((80,80), Image.ANTIALIAS)
        self.pause_play_photo=ImageTk.PhotoImage(pil_img)
    def setup_window(self):
        # initial setup
        self.primary_window = Tk()
        self.open_images()
        self.primary_window.wm_title("spirograph")
        self.primary_window.geometry('1274x960-1+0')
        self.primary_window.minsize(width=100, height=30)
        self.primary_window.maxsize(width=self.max_win_size[0], height=self.max_win_size[1])
        
        # image & canvas
        
        self.im_frame = ttk.Frame(self.primary_window)
        self.im_frame.grid(row=0,column=0,columnspan=2,sticky="nsew")
        self.im_frame.columnconfigure(0, weight=1)
        self.im_frame.rowconfigure(0, weight=1)
        self.primary_window.columnconfigure(0, weight=1)
        self.primary_window.rowconfigure(0, weight=1)
        
        self.canvas_frame = ttk.Frame(self.primary_window)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.columnconfigure(0, weight=1)
        
        self.the_canvas = Canvas(self.canvas_frame,
                                width=self.canvas_size[0],
                                height=self.canvas_size[1],
                                background='black')
        self.the_canvas.grid(row=0, column=0,columnspan=2)
        canv_im = Image.new('RGB',self.canvas_size)
        self.tk_im = ImageTk.PhotoImage(canv_im)
        self.canv_im = self.the_canvas.create_image((0,0), anchor='nw', image=self.tk_im)
        
        # bottom buttons
        self.bottom_buttons_frame = ttk.Frame(self.primary_window)
        self.bottom_buttons_frame.grid(row=3,column=0,columnspan=2)
        #
        self.random_button = Button(self.bottom_buttons_frame,
                                    command=self.random,
                                    image=self.random_photo,
                                    width="80",height="80")
        self.random_button.grid(row=0,column=3)
        #
        self.update_button = Button(self.bottom_buttons_frame,
                                   command=self.update,#lambda: self.parent.queue.put(self.update),
                                   image=self.update_photo,
                                   width="80",height="80")
        self.update_button.grid(row=0,column=2)
        #
        self.stop_button = Button(self.bottom_buttons_frame,
                                   command=self.stop,
                                   image=self.trash_photo,
                                   width="80",height="80")
        self.stop_button.grid(row=0,column=4)
        #
        self.pause = IntVar()
        self.pause.set(2)
        self.pause_button = Button(self.bottom_buttons_frame,
                                   command=self.pause_toggle,
                                   image=self.pause_play_photo,
                                   width="80",height="80")
        self.pause_button.grid(row=0,column=5)
        #
        self.close_button = Button(self.bottom_buttons_frame,
                                   command=self.parent.close,
                                   image=self.close_photo,
                                   width="80",height="80")
        self.close_button.grid(row=0,column=6)
        #
        Label(self.bottom_buttons_frame, text="Status: ",font=self.main_font).grid(row=0,column=7)
        self.status_entry = Entry(self.bottom_buttons_frame)
        self.status_entry.config(font=self.main_font)
        self.update_status_entry("waiting")
        self.status_entry.grid(row=0,column=8)
        # bottom entries 
        self.bottom_entries_frame = ttk.Frame(self.primary_window)
        self.bottom_entries_frame.grid(row=4,column=0,columnspan=2)
        #
        Label(self.bottom_entries_frame, text=" Inner Radius:",font=self.main_font).grid(row=1, column=1)
        self.inner_radius = Entry(self.bottom_entries_frame,justify='right')
        self.inner_radius.insert("end", '4/5')
        self.inner_radius.config(font=self.main_font,width=9)
        self.inner_radius.grid(row=1,column=2)
        #
        Label(self.bottom_entries_frame, text=" Draw Point Radius:",font=self.main_font).grid(row=1, column=3)
        self.draw_point_radius = Entry(self.bottom_entries_frame,justify='right')
        self.draw_point_radius.insert("end", '1/2')
        self.draw_point_radius.config(font=self.main_font,width=9)
        self.draw_point_radius.grid(row=1,column=4)
        # #
        # Label(self.bottom_entries_frame, text=" Step Time (ms):",font=self.main_font).grid(row=2, column=3)
        # self.step_time = Entry(self.bottom_entries_frame,justify='right')
        # self.step_time.insert("end", '0')
        # self.step_time.config(font=self.main_font,width=9)
        # self.step_time.grid(row=2,column=4)
        #
        Label(self.bottom_entries_frame, text=" Line Weight:",font=self.main_font).grid(row=2, column=3)
        self.line_weight = Entry(self.bottom_entries_frame,justify='right')
        self.line_weight.insert("end", '25')
        self.line_weight.config(font=self.main_font,width=9)
        self.line_weight.grid(row=2,column=4)
        #
        Label(self.bottom_entries_frame, text=" Draw Angle:",font=self.main_font).grid(row=2, column=5)
        self.draw_theta = Entry(self.bottom_entries_frame,justify='left')
        self.draw_theta.insert("end", '0')
        self.draw_theta.config(font=self.main_font,width=9)
        self.draw_theta.grid(row=2,column=6)
        # #
        # self.show_circles_check = IntVar()
        # self.show_circles_check.set(0)
        # self.show_path_button = Checkbutton(self.bottom_entries_frame, text="Show Circles", variable=self.show_circles_check,font=self.main_font)
        # self.show_path_button.grid(row=2,column=1,columnspan=2)
        #
        self.continuous_random_check = IntVar()
        self.continuous_random_check.set(0)
        self.continuous_random_button = Checkbutton(self.bottom_entries_frame, text="Continuous Random", variable=self.continuous_random_check,font=self.main_font)
        self.continuous_random_button.grid(row=2,column=1,columnspan=2)
        #
        #
        self.save_series_check = IntVar()
        self.save_series_check.set(0)
        self.save_series_button = Checkbutton(self.bottom_entries_frame, text="Save Series", variable=self.save_series_check,font=self.main_font)
        self.save_series_button.grid(row=1,column=5,columnspan=2)
        # self.pause_button = Radiobutton(self.bottom_entries_frame, text="Pause", variable=self.pause, command=pause_toggle,value=1,font=self.main_font)
        # self.pause_button.grid(row=1, column=5)
        # self.unpause_button = Radiobutton(self.bottom_entries_frame, text="Go", variable=self.pause, command=pause_toggle,value=2,font=self.main_font)
        # self.unpause_button.grid(row=2,column=5)
    def update_status_entry(self,state):
        def change_status(message):
            self.status_entry.config(state="normal",width=len(message))
            self.status_entry.delete(0,"end")
            self.status_entry.insert("end",message)
            self.status_entry.config(state="disabled")
        if state == 'waiting':
            change_status("Waiting...")
        elif state == 'complete':
            change_status("Complete!")
        elif state == 'drawing':
            change_status("Drawing...")
    # def update(self):
        # while os.path.isfile('data/stop'): time.sleep(.1)
        # self.update_status_entry('drawing')
        # self.parent.queue.queue.clear()
        # self.the_canvas.delete("all")
        # self.spiro = self.parent.spirographer
        # self.spiro.init_spirograph()
        # # if '/' in radius_entry: entry_as_fraction = Fraction(radius_entry)
        # # else: entry_as_fraction = Fraction(Decimal(radius_entry))
        # self.spiro.inner_radius = abs(eval(self.inner_radius.get()))
        # self.spiro.draw_point_radius = eval(self.draw_point_radius.get())
        # self.spiro.draw_point_theta = float(self.draw_theta.get())
        # self.spiro.update_spirograph()
        # self.the_canvas.delete("all")
        
        # self.steps = 0
        # def step():
            # self.steps += 1
            # while os.path.isfile("data/pause") and not os.path.isfile("data/stop"): time.sleep(.2)
            # delay = self.step_time.get()
            # try:
                # delay = float(delay)
                # time.sleep(delay/1000)
            # except: pass
            # self.spiro.step()
            # x1,y1 = self.spiro.line_coordinates[0]
            # x2,y2 = self.spiro.line_coordinates[1]
            # self.the_canvas.create_line(x1,y1,x2,y2, fill=self.spiro.color, width=2)
            # if self.show_circles_check.get():
                # self.draw_circles()
            # elif not self.show_circles_check.get() and self.circles_drawn:
                # self.the_canvas.delete("circle")
        
        # while not self.spiro.end_reached() and not os.path.isfile('data/stop'):
            # step()
        # if os.path.isfile("data/stop"): 
            # os.remove("data/stop")
            # if os.path.isfile("data/pause"):
                # os.remove("data/pause")
            # self.the_canvas.delete("all")
            # self.update_status_entry('waiting')
        # else: self.update_status_entry('complete')
        # print("Finished in " + str(self.steps) + " steps.")
    def update(self):
        while os.path.isfile('data/stop'): time.sleep(.1)
        self.update_status_entry('drawing')
        self.parent.queue.queue.clear()
        self.spiro = self.parent.spirographer
        self.spiro.init_spirograph()
        # if '/' in radius_entry: entry_as_fraction = Fraction(radius_entry)
        # else: entry_as_fraction = Fraction(Decimal(radius_entry))
        self.spiro.inner_radius = abs(eval(self.inner_radius.get()))
        self.spiro.draw_point_radius = eval(self.draw_point_radius.get())
        self.spiro.draw_point_theta = float(self.draw_theta.get())
        self.spiro.line_weight = int(self.line_weight.get())
        self.spiro.update_spirograph()
        # self.the_canvas.delete("all")
        
        self.image = Image.new('RGB',self.image_size)
        self.draw = ImageDraw.Draw(self.image)
        
        self.steps = 0
        self.spirographs_drawn += 1
        def step():
            self.steps += 1
            while os.path.isfile("data/pause") and not os.path.isfile("data/stop"): time.sleep(.2)
            # delay = self.step_time.get()
            delay = 0
            try:
                delay = float(delay)
                time.sleep(delay/1000)
            except: pass
            self.spiro.step()
            x1,y1 = self.spiro.pseudo_coordinates[0]
            x2,y2 = self.spiro.pseudo_coordinates[1]
            # print("self.spiro.color: " + str(self.spiro.color))
            self.draw.line([x1,y1,x2,y2], fill=self.spiro.color, width=int(self.line_weight.get()))
            # if self.show_circles_check.get():
                # self.draw_circles()
            # elif not self.show_circles_check.get() and self.circles_drawn:
                # self.the_canvas.delete("circle")
            if self.save_series_check.get() and self.steps % 12 == 0:
                self.series_frame += 1
                name = "series/spiro_" + str(self.spirographs_drawn) + "_" + str(self.series_frame) + ".png"
                self.image.save(name)
        
        while not self.spiro.end_reached() and not os.path.isfile('data/stop'):
            step()
        if self.save_series_check.get() and self.steps % 12 != 0:
            self.series_frame += 1
            name = "series/spiro_" + str(self.series_frame) + ".png"
            self.image.save(name)
        self.image.save("spiro.png")
        self.update_image(self.image)
        if os.path.isfile("data/stop"): 
            os.remove("data/stop")
            if os.path.isfile("data/pause"):
                os.remove("data/pause")
            # self.the_canvas.delete("all")
            self.update_status_entry('waiting')
        else: self.update_status_entry('complete')
        print("Finished in " + str(self.steps) + " steps.")
        if self.continuous_random_check.get():
            return self.primary_window.after(333,lambda: self.random_button.invoke())
    def draw_circles(self):
        def create_circle(x, y, r, canvasName,inner=False): #center coordinates, radius
            x0 = x - r
            y0 = y - r
            x1 = x + r
            y1 = y + r
            if inner: return canvasName.create_oval(x0, y0, x1, y1, tags=("circle","inner"), outline="white")
            else: return canvasName.create_oval(x0, y0, x1, y1, tags=("circle"), outline="white")
        if not self.circles_drawn:
            self.inner_circle_location = self.spiro.inner_circle_center_on_pixel_plane
            x,y = self.inner_circle_location
            create_circle(self.canvas_dimension/2,
                          self.canvas_dimension/2,
                          self.canvas_dimension/2,
                          self.the_canvas)
            self.inner_circle = create_circle(x,y,self.spiro.inner_radius*self.spiro.pixel_radius,self.the_canvas)
            self.circles_drawn = True
        else:
            new_location = self.spiro.inner_circle_center_on_pixel_plane
            delta_x = new_location[0]-self.inner_circle_location[0]
            delta_y = new_location[1]-self.inner_circle_location[1]
            self.inner_circle_location = self.spiro.inner_circle_center_on_pixel_plane
            self.the_canvas.move(self.inner_circle,delta_x,delta_y)
    def random(self):
        if self.status_entry.get() in ("Drawing...","Complete!") and not os.path.isfile('data/pause'):
            was_drawing = True
        else:
            was_drawing = False
        self.stop()
        # inner_radius_numerator = int(random.gauss(60,40))
        # inner_radius_denominator=int(random.gauss(100,10))
        draw_point_denominator=int(random.gauss(100,20))
        draw_point_numerator = int(random.gauss(draw_point_denominator/2,draw_point_denominator/10))
        inner_radius_denominator = int(random.gauss(1,.1)//.01)
        inner_radius_numerator = int(random.gauss(inner_radius_denominator/2,inner_radius_denominator/10))
        draw_point_theta = random.uniform(0,math.pi)
        line_weight = abs(int(random.gauss(0,8)))+5
        
        self.spiro = self.parent.spirographer
        self.spiro.inner_radius = inner_radius_numerator / inner_radius_denominator
        self.spiro.draw_point_radius = draw_point_numerator / draw_point_denominator
        self.spiro.draw_point_theta = draw_point_theta
        
        self.inner_radius.delete(0,'end')
        self.inner_radius.insert('end',str(inner_radius_numerator)+"/"+str(inner_radius_denominator))
        self.draw_point_radius.delete(0,'end')
        self.draw_point_radius.insert('end',str(draw_point_numerator)+"/"+str(draw_point_denominator))
        self.draw_theta.delete(0,'end')
        self.draw_theta.insert('end',str(draw_point_theta))
        self.line_weight.delete(0,'end')
        self.line_weight.insert('end',str(line_weight))
        if was_drawing:
            return self.update_button.invoke()
    def update_image(self,im):
        new_size = self.get_size(self.canvas_size,im.size)
        im=im.resize(new_size,Image.ANTIALIAS)
        self.tk_im = ImageTk.PhotoImage(im)
        self.the_canvas.itemconfig(self.canv_im, image=self.tk_im)
        self.the_canvas.config(width=new_size[0], height=new_size[1])
    def get_size(self, max_size, input_size):
        # fits dimensions to a target size while maintaining aspect ratio
        if (input_size[0] != max_size[0]) or (input_size[1] != max_size[1]):
            if (input_size[0] > max_size[0]) or (input_size[1] > max_size[1]):
                if input_size[0]/input_size[1] > max_size[0]/max_size[1]:
                    resized_size=(int(max_size[0]),int(max_size[0]*input_size[1]/input_size[0]))
                else:
                    resized_size=(int(max_size[1]*input_size[0]/input_size[1]),int(max_size[1]))
            else:
                if input_size[0]/input_size[1] < max_size[0]/max_size[1]:
                    resized_size=(int(max_size[1]*input_size[0]/input_size[1]),int(max_size[1]))
                else:
                    resized_size=(int(max_size[0]),int(max_size[0]*input_size[1]/input_size[0]))
        else: resized_size = input_size
        return resized_size