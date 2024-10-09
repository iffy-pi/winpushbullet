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

    def getSavePath(self, path:tuple=(None, None), windowTitle:str=None, fileTypes:list[tuple[str, str]]=None) -> str:
        '''
        Opens file explorer dialog for saving a file and returns string of file name to save
        :param path: A tuple of (folder, filename) that the explorer window will open to
        :param windowTitle: The title of the explorer window
        :param fileTypes: The list of file type extensions e.g. [('All Files', '*.*'), ('Plain Text', '*.txt')]
        :return: str : The address of the file path to save to, None if the user cancelled
        '''

        if fileTypes is None:
            fileTypes = [('All Files', '*.*')]

        _dir, _file = path
        file = asksaveasfile(title=windowTitle, filetypes = fileTypes, defaultextension = fileTypes, initialdir=_dir, initialfile=_file)
        if file is None:
            return None
        return file.name

    def save(self, binaryContent:bytes, path:tuple=(None, None), windowTitle:str=None, fileTypes:list[tuple[str, str]]=None) -> tuple[bool, str|None]:
        """
        Saves the binaryContent using a save file explorer window
        :param binaryContent: The bytes of the file to be saved
        :param path: A tuple of (folder, filename) that the explorer window will open to
        :param windowTitle: The title of the explorer window
        :param fileTypes: The list of file type extensions e.g. [('All Files', '*.*'), ('Plain Text', '*.txt')]
        :return: tuple: Boolean which is true if the user saved, str of the file address
        """
        fileAddress = self.getSavePath(path=path, windowTitle=windowTitle, fileTypes=fileTypes)
        if fileAddress is None:
            return False, fileAddress

        with open(fileAddress, 'wb') as file:
            file.write(binaryContent)

        return True, fileAddress

    
    def open(self, path: tuple=(None,None), title:str=None) -> str:
        '''
        Opens file explorer dialog for opening a file and returns the user set filename
        '''
        files = [('All Files', '*.*')]
        _dir, _file = path
        return askopenfilename( title=title, initialdir=_dir, initialfile=_file, filetypes=files )