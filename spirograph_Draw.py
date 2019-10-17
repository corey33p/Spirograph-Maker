import math
import numpy as np
import random

class SpiroDraw:
    def __init__(self, parent, outer_circle_dimension):
        self.outer_circle_pixel_dimension = outer_circle_dimension
        self.parent = parent
        
        self.color_table = {}
        self.color_table[0] = ('BLACK',np.array([0,0,0]))
        self.color_table[1] = ('WHITE',np.array([255,255,255]))
        self.color_table[2] = ('RED',np.array([255,0,0]))
        self.color_table[3] = ('LIME',np.array([0,255,0]))
        self.color_table[4] = ('BLUE',np.array([0,0,255]))
        self.color_table[5] = ('YELLOW',np.array([255,255,0]))
        self.color_table[6] = ('AQUA',np.array([0,255,255]))
        self.color_table[7] = ('FUCHSIA',np.array([255,0,255]))
        self.color_table[8] = ('SILVER',np.array([192,192,192]))
        self.color_table[9] = ('GRAY',np.array([128,128,128]))
        # self.color_table[13] = ('MAROON',np.array([128,0,0]))   #A
        self.color_table[10] = ('OLIVE',np.array([128,128,0]))  #B
        # self.color_table[14] = ('GREEN',np.array([0,128,0]))    #C
        self.color_table[11] = ('PURPLE',np.array([128,0,128])) #D
        self.color_table[12] = ('TEAL',np.array([0,128,128]))   #E
        # self.color_table[15] = ('NAVY',np.array([0,0,128]))     #F
    def init_spirograph(self):
        self.theta_step = 1 * math.pi / 180 # one degree
        self.outer_degree = 0
        self.step_number = 0
        
        self.inner_radius = 1 # relative to the outer_radius of 1
        self.outer_circumference = 2*math.pi
        self.inner_circumference = 2*self.inner_radius*math.pi
        
        self.draw_point_radius = 1
        self.draw_point_theta = 0
        self.line_weight = 25
        
        self.update_spirograph()
        self.get_random_color_scheme()
        self.get_color()
    def update_spirograph(self):
        def proportion_radii():
            self.proportion = 1 / ((1 - self.inner_radius) + self.inner_radius * self.draw_point_radius)
        proportion_radii()
        
        # both of the following are in polar coordinates (r,theta)
        self.inner_circle_center = (1 - self.inner_radius, self.outer_degree)
        self.inner_circle_draw_point = (self.draw_point_radius*self.inner_radius, self.draw_point_theta)
        
        self.translate()
        self.line_coordinates = None
        self.start_point = self.pixel_y,self.pixel_x
        self.update_line_coordinates()
        self.get_random_color_scheme()
        self.get_color()
    def step(self):
        self.step_number += 1
        
        # move inner circle
        distance_along_circles = self.inner_radius * self.theta_step
        delta_angle_on_outer_circle = distance_along_circles
        self.outer_degree += delta_angle_on_outer_circle
        self.inner_circle_center = (1 - self.inner_radius, self.outer_degree)
        
        # move draw point
        self.draw_point_theta -= self.theta_step
        self.inner_circle_draw_point = (self.draw_point_radius*self.inner_radius, self.draw_point_theta)
        
        self.translate()
        self.update_line_coordinates()
        self.get_color()
    def translate(self):
        self.translate_draw_point_to_cartesian()
        self.translate_to_pixel_plane()
    def translate_draw_point_to_cartesian(self):
        def pol_to_cart(polar_coords):
            r,t=polar_coords
            return r*math.cos(t),r*math.sin(t)
        self.cartesian_inner_circle_center = pol_to_cart(self.inner_circle_center)
        self.cartesian_draw_point = pol_to_cart(self.inner_circle_draw_point)
        x = self.cartesian_inner_circle_center[0]+self.cartesian_draw_point[0]
        y = self.cartesian_inner_circle_center[1]+self.cartesian_draw_point[1]
        self.coord_plane_draw_point = x,y
    def translate_to_pixel_plane(self):
        x,y=self.coord_plane_draw_point
        x=x*self.proportion
        y=y*self.proportion
        pic_size = self.parent.display.image_size
        x_radius = pic_size[0]/2
        y_radius = pic_size[1]/2
        radius = min(x_radius,y_radius)
        self.pixel_x = x * radius + y_radius
        self.pixel_y = y * radius + x_radius
        # self.inner_circle_center_on_pixel_plane = tuple([2*self.pixel_radius-(self.pixel_radius-i*self.pixel_radius) for i in self.cartesian_inner_circle_center][::-1])
    def update_line_coordinates(self):
        if self.line_coordinates is None: 
            self.line_coordinates = [(self.pixel_y,self.pixel_x),(self.pixel_y,self.pixel_x)]
        else:
            self.line_coordinates[0] = self.line_coordinates[1]
            self.line_coordinates[1] = self.pixel_y,self.pixel_x
            
            # extend the line a bit to avoid gaps between the lines
            extension_factor = .2*self.line_weight
            rise= self.line_coordinates[1][1]-self.line_coordinates[0][1]
            run = self.line_coordinates[1][0]-self.line_coordinates[0][0]
            new_start_point_x = self.line_coordinates[0][0] - extension_factor * run
            new_start_point_y = self.line_coordinates[0][1] - extension_factor * rise
            new_end_point_x = self.line_coordinates[1][0] + extension_factor * run
            new_end_point_y = self.line_coordinates[1][1] + extension_factor * rise
            self.pseudo_coordinates=[(new_start_point_x,new_start_point_y),
                                     (new_end_point_x,new_end_point_y)]
    def end_reached(self):
        if self.step_number < 360: return False
        delta_x = self.line_coordinates[1][1] - self.start_point[1]
        delta_y = self.line_coordinates[1][0] - self.start_point[0]
        if abs(delta_x) < .01 and abs(delta_y) < .01: return True
        else: return False
    def get_random_color_scheme(self):
        self.number_of_colors = int(random.gauss(8,2.5))
        self.number_of_colors = max(self.number_of_colors,1)
        self.colors=[]
        for color in range(self.number_of_colors):
            self.colors.append(random.choice(self.color_table)[1])
    def get_color(self):
        theta = self.draw_point_theta % math.pi
        length_of_each_color = math.pi / self.number_of_colors
        which_color = int(theta // length_of_each_color)
        how_far_in_the_color = (theta % length_of_each_color) / length_of_each_color
        first_color = self.colors[which_color]
        if which_color == self.number_of_colors - 1:
            next_color = 0
        else:
            next_color = which_color + 1
        delta_color = self.colors[next_color] - self.colors[which_color]
        self.color = self.colors[which_color] + delta_color * how_far_in_the_color
        
        self.color = tuple(self.color)
        self.color = tuple([int(a) for a in self.color])
        self.color = "#%02x%02x%02x" % self.color
