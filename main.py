import time
import random
import pyautogui as pygui
import tkinter as tk
from tkinter import messagebox
from pynput import mouse
from PopularWords import words

xPos, yPos = None, None
root = tk.Tk()

def trackingMousePosition () :
  def whenClick (x, y, _, pressed) :
    global xPos, yPos
    
    if pressed :
      xPos, yPos = x, y
      print(f"x: {x}  y: {y}")
      listener.stop()
          
  listener = mouse.Listener(on_click = whenClick)
  listener.start()
  listener.join()
    
  messagebox.showinfo(title = "Successfull", 
                      message = "Finished retrieving mouse position",
                      parent = root)

def searchingProcess () :
  print(f"x: {xPos}  y: {yPos}")
  
  if xPos == None or yPos == None :
    messagebox.showerror(title = 'Error',
                         message = f"Invalid mouse position \n (x: {xPos} y: {yPos})",
                         parent = root)
    return

  while True :
    pygui.click(xPos, yPos)
    pygui.write(random.choice(words) + " ", random.uniform(0.05, 0.1))
    pygui.press("enter")
    sleeptime = random.randint(10000, 17000) / 1000
    print(sleeptime)
    time.sleep(sleeptime)
    
def initUI () :     
  root.title("Bing auto search tool")
  root.geometry("300x300")
  root.attributes("-topmost", True)

  startTrackingButton = tk.Button(root, 
                        text = "Start tracking",
                        command = trackingMousePosition)
  startTrackingButton.pack()

  startButton2 = tk.Button(root, 
                        text = "Start tracking",
                        command = searchingProcess)
  startButton2.pack()

  root.mainloop()
  
initUI()