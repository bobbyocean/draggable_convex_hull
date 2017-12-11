# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 00:47:14 2017

@author: Robert D. Bates, Ph.D. 

This module has two classes in it which are used to plot clickable objects
that can be dragged and repositioned within a matplotlib window. These objects 
must be saved to an accessible variable for matplotlib to use them correctly. 


DraggableObject. 
    This class is used to create individual objects that can all be plotted
    on a single axes and dragged and moved. Each object locks the class, 
    preventing other objects from moving. 

DraggableObjects. 
    This class takes in an axes and collection of objects to be manipulated
    in sync. Hence, the axes must be provided to be the prompt for capturing
    the mouse. Likewise, a custom function must be provided that specifies
    how to update the odjs_to_update list. 
"""

from matplotlib.patches import Circle,Rectangle,Polygon
from numpy.random       import choice

class DraggableObject:
    lock = None  # only one can be animated at a time
    def __init__(self, obj):
        self.obj        = obj
        self.press      = None
        self.background = None
        self.connect()
    def on_press(self, event):
        #if event.inaxes != self.obj.axes: return
        if DraggableObject.lock is not None: return
        contains, attrd = self.obj.contains(event)
        mouse_x, mouse_y = event.xdata, event.ydata
        if not contains: return
        if isinstance(self.obj,Circle):
            obj_data = self.obj.center
        elif isinstance(self.obj,Rectangle):
            obj_data = self.obj.xy
        elif isinstance(self.obj,Polygon):
            #Calculate who to change and their index in the list. 
            obj_data = self.obj.xy[:-1]
            obj_data = sorted(((mouse_x-x0)**2+(mouse_y-y0)**2,(n,x0,y0)) for n,(x0,y0) in enumerate(obj_data))[0][1]
        DraggableObject.lock = self
        # draw everything but the selected rectangle and store the pixel buffer
        self.press = obj_data, mouse_x, mouse_y
        self.obj.set_animated(True)
        self.obj.figure.canvas.draw()
        self.background = self.obj.figure.canvas.copy_from_bbox(self.obj.axes.bbox)
        self.obj.axes.draw_artist(self.obj)
        self.obj.figure.canvas.blit(self.obj.axes.bbox)
    def on_motion(self, event):
        if DraggableObject.lock is not self: return
        if event.inaxes != self.obj.axes: return
        obj_data, mouse_x, mouse_y = self.press
        dx = event.xdata - mouse_x
        dy = event.ydata - mouse_y
        if isinstance(self.obj,Circle):
            x0, y0 = obj_data
            self.obj.center = (x0+dx,y0+dy)
        elif isinstance(self.obj,Rectangle):
            x0, y0 = obj_data
            self.obj.xy     = (x0+dx,y0+dy)
        elif isinstance(self.obj,Polygon):
            n, x0, y0 = obj_data
            self.obj.xy[n]  = (x0+dx,y0+dy)
        # restore the background region
        self.obj.figure.canvas.restore_region(self.background)
        self.obj.axes.draw_artist(self.obj)
        self.obj.figure.canvas.blit(self.obj.axes.bbox)
    def on_release(self, event):
        if DraggableObject.lock is not self: return
        DraggableObject.lock = None
        self.press           = None
        self.background      = None
        self.obj.set_animated(False)
        #self.obj.figure.canvas.draw()
    def connect(self):
        self.cidpress   = self.obj.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.obj.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion  = self.obj.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
    def disconnect(self):
        self.obj.figure.canvas.mpl_disconnect(self.cidpress)
        self.obj.figure.canvas.mpl_disconnect(self.cidrelease)
        self.obj.figure.canvas.mpl_disconnect(self.cidmotion)
        
class DraggableObjects:
    def __init__(self, ax, clickable_objs, objs_to_update, updater):
        self.ax             = ax
        self.clickable_objs = clickable_objs
        self.updater        = updater
        self.objs_to_update = objs_to_update
        self.objs_to_update_data = dict()
        self.clicked_obj    = None
        self.old_mouse      = None
        self.new_mouse      = None
        self.background     = None
        self.connect()
    def get_data(self, obj):
        if isinstance(obj,Circle):
            return obj.center
        else:
            return obj.xy
    def on_press(self, event):
        self.old_mouse = event
        clicked_objs = [obj for obj in self.clickable_objs if obj.contains(self.old_mouse)[0]]
        if not clicked_objs:
            return
        self.clicked_obj = choice(clicked_objs)
        self.objs_to_update_data = {obj:self.get_data(obj) for obj in self.objs_to_update}
        for obj in self.objs_to_update:
            obj.set_animated(True)
        self.ax.figure.canvas.draw()
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.axes.bbox)
        for obj in self.objs_to_update:
            self.ax.axes.draw_artist(obj)
        self.ax.figure.canvas.blit(self.ax.axes.bbox)
    def on_motion(self, event):
        self.new_mouse = event
        if not self.old_mouse:
            return
        self.updater(self)
        self.ax.figure.canvas.restore_region(self.background)
        for obj in self.objs_to_update:
            self.ax.axes.draw_artist(obj)
        self.ax.figure.canvas.blit(self.ax.axes.bbox)
    def on_release(self, event):
        self.objs_to_update_data = dict()
        self.clicked_obj    = None
        self.old_mouse      = None
        self.new_mouse      = None
        self.background     = None
        for obj in self.objs_to_update:
            obj.set_animated(False)
        self.ax.figure.canvas.draw()
    def connect(self):
        self.cidpress   = self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion  = self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
    def disconnect(self):
        self.ax.figure.canvas.mpl_disconnect(self.cidpress)
        self.ax.figure.canvas.mpl_disconnect(self.cidrelease)
        self.ax.figure.canvas.mpl_disconnect(self.cidmotion)
    
