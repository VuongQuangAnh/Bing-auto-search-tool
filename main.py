import time
import pyautogui as pygui
import tkinter as tk
from tkinter import messagebox
from pynput import mouse

def trackingMousePosition () :
    def whenClick (x, y, _, pressed) :
        if pressed :
            print(f"x: {x}  y: {y}")
            listener.stop()
            
    listener = mouse.Listener(on_click = whenClick)
    listener.start()
    listener.join()
    
    messagebox.showinfo(title = "Successfull", 
                        message = "Getting mouse position completed",
                        parent=root)
        
root = tk.Tk()
root.title("Bing auto search tool")
root.geometry("300x300")
root.attributes("-topmost", True)

startButton = tk.Button(root, 
                        text = "Start tracking mouse position",
                        command = trackingMousePosition)
startButton.pack()

root.mainloop()