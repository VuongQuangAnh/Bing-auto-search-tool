import random
import threading
import pyautogui as pygui
import tkinter as tk
from tkinter import messagebox
from pynput import mouse

xPos, yPos = None, None
root = tk.Tk()
words = []

def getData () :
  global words, xPos, yPos
  
  with open("Common words.txt", "r") as file :
    words = file.read().splitlines()
  
  try :
    with open("Mouse position.txt", "r") as file :
      data = file.read()
      if len(data.split()) == 2:
        xPos, yPos = map(int, data.split())
  except :
    pass

def trackingMousePosition () :
  def whenClick (x, y, _, pressed) :
    global xPos, yPos
    
    if pressed :
      xPos, yPos = x, y
      print(f"x: {x}  y: {y}")
      listener.stop()
      
      with open("Mouse position.txt", "w") as file :
        file.write(f"{x} {y}")
          
  listener = mouse.Listener(on_click = whenClick)
  listener.start()
  listener.join()
    
  messagebox.showinfo(title = "Successfull", 
                      message = "Finished retrieving mouse position",
                      parent = root)

def searchingProcess () :
  print(f"x: {xPos}  y: {yPos}")
  cancelSearchingProcess = threading.Event()
  
  if xPos == None or yPos == None :
    messagebox.showerror(title = 'Error',
                         message = f"Invalid mouse position \n (x: {xPos} y: {yPos})",
                         parent = root)
    return
  
  def searchingLoop () :
    searchesCount = 0
    
    while searchesCount < 35 and not cancelSearchingProcess.is_set():
      pygui.click(xPos, yPos)
      pygui.write(random.choice(words) + " ", random.uniform(0.05, 0.1))
      pygui.press("enter")
      sleeptime = random.randint(10000, 17000) / 1000
      print(sleeptime)
      
      if cancelSearchingProcess.wait(sleeptime) :
        return
      
      searchesCount += 1
      
  threading.Thread(target = searchingLoop, daemon = True).start()
  
  def whenClick (_, __, button, pressed) :
    if pressed and button == mouse.Button.right :
      cancelSearchingProcess.set()
      listener.stop()
  
  listener = mouse.Listener(on_click = whenClick)
  listener.start()
  listener.join()
  
  if cancelSearchingProcess.is_set() :
    messagebox.showinfo(title = "Cancel",
                          message = "Task cancelled by user",
                          parent = root)
    return
    
  messagebox.showinfo(title = "Succesfull",
                      message = "Searching Completed",
                      parent = root)
  
    
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

getData()
initUI()