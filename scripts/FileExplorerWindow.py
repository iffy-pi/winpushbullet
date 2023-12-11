# importing all files  from tkinter
from binascii import Incomplete
from typing import BinaryIO, TextIO
from tkinter import * 
from ctypes import windll
  
# import only asksaveasfile from filedialog
# which is used to save file in any extension
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askopenfilename
  
# root = Tk()
# root.withdraw()
# windll.shcore.SetProcessDpiAwareness(1)
  
# # function to call when user press
# # the save button, a filedialog will
# # open and ask to save file
# def save():
#     files = [('All Files', '*.*')]
#     initDir = r"C:\Users\omnic\Desktop"
#     file = asksaveasfile(filetypes = files, defaultextension = files, initialdir=initDir)
  
# # btn = ttk.Button(root, text = 'Save', command = lambda : save())
# # btn.pack(side = TOP, pady = 20)
  
# save()

class FileExplorerWindow():
    def __init__(self):
        self.root = Tk()
        self.root.withdraw()
        windll.shcore.SetProcessDpiAwareness(1)

    def save(self, path:tuple=(None, None), title:str=None) -> str:
        '''
        Opens file explorer dialog for saving a file and returns string of file name
        '''

        files = [('All Files', '*.*')]
        _dir, _file = path
        file = asksaveasfile(title=title, filetypes = files, defaultextension = files, initialdir=_dir, initialfile=_file)
        if file is None:
            return None
        return file.name
    
    def open(self, path: tuple=(None,None), title:str=None) -> str:
        '''
        Opens file explorer dialog for opening a file and returns the user set filename
        '''
        files = [('All Files', '*.*')]
        _dir, _file = path
        return askopenfilename( title=title, initialdir=_dir, initialfile=_file, filetypes=files )