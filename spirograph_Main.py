from spirograph_Display import Display
from spirograph_Draw import SpiroDraw
from tkinter import mainloop
import os
import win32gui
import win32con
import threading
from queue import Queue
import time
import time

class Parent:
    def __init__(self):
        self.queue = Queue()
        self.display  = Display(self)
        self.spirographer = SpiroDraw(self,self.display.canvas_dimension)
        self.resize_CLI_window()
        self.pause = False
        queue_thread = threading.Thread(target=lambda: self. queue_thread())
        queue_thread.daemon = True
        queue_thread.start()
        if os.path.isfile("data/stop"): os.remove("data/stop")
        if os.path.isfile("data/pause"):os.remove("data/pause")
        mainloop()
    def resize_CLI_window(self):
        def get_windows():
            def check(hwnd, param):
                title = win32gui.GetWindowText(hwnd)
                if 'spirograph_Main' in title and 'Notepad++' not in title:
                    param.append(hwnd)
            wind = []
            win32gui.EnumWindows(check, wind)
            return wind
        self.cli_handles = get_windows()
        for window in self.cli_handles:
            win32gui.MoveWindow(window,0,0,self.display.max_win_size[0],self.display.max_win_size[1],True)
    def queue_thread(self):
        while True: # handle objects in the queue until game_lost
            time.sleep(.25)
            try:
                next_action = self.queue.get(False)
                next_action()
            except Exception as e: 
                if str(e) not in (""): 
                    print(e)
        self.queue.queue.clear()
        self.close()
    def close(self):
        for handle in self.cli_handles:
            win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)

if __name__ == '__main__':
    main_object = Parent()
    