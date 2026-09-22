import random
import threading
import pyautogui as pygui
import customtkinter as ctk
from tkinter import messagebox
from pynput import mouse

MAXSEARCHES = 33
loopTimes = None
xPos, yPos = None, None
root = ctk.CTk()
words = []

def getData () :
  global words, xPos, yPos, loopTimes
  
  with open("Common words.txt", "r") as file :
    words = file.read().splitlines()
  
  try :
    with open("Mouse position.txt", "r") as file :
      data = file.read()
      if len(data.split()) == 2:
        xPos, yPos = map(int, data.split())
  except :
    pass
  
  try :
    with open("Tabs.txt", "r") as file :
      data = file.read()
      if data :
        loopTimes = int(data)
  except :
    pass

def trackingMousePosition () :
  def whenClick (x, y, _, pressed) :
    global xPos, yPos
    
    if pressed :
      xPos, yPos = x, y
      # print(f"x: {x}  y: {y}")
      listener.stop()
      
      with open("Mouse position.txt", "w") as file :
        file.write(f"{x} {y}")
          
  listener = mouse.Listener(on_click = whenClick)
  listener.start()
  listener.join()
    
  messagebox.showinfo(title = "Successful", 
                      message = "Finished retrieving mouse position",
                      parent = root)

def searchingProcess () :
  # print(f"x: {xPos}  y: {yPos}")
  
  if xPos == None or yPos == None :
    messagebox.showerror(title = 'Error',
                         message = f"Invalid mouse position \n (x: {xPos} y: {yPos})",
                         parent = root)
    return
  
  print(f"Loops: {entry.get()}")
  if not entry.get() :
    messagebox.showerror(parent = root,
                         message = "Tab fill cannot be empty",
                         title = "Error")
  elif entry.get() == "0" :
    messagebox.showerror(parent = root,
                         message = "Tab fill cannot be zero",
                         title = "Error")
    return
    
  startSearchingButton.configure(text = "Right-click to cancel",
                                 command = None)
  startTrackingButton.configure(command = None)
  cancelSearchingProcess = threading.Event()
  
  def showMessage(success) :
    if not success :
      messagebox.showinfo(title = "Cancel",
                            message = "Task cancelled by user",
                            parent = root)
    else :
      messagebox.showinfo(title = "Successful",
                          message = "Searching Completed",
                          parent = root)
    
    startSearchingButton.configure(text = "Start searching",
                                   command = searchingProcess)
    startTrackingButton.configure(command = trackingMousePosition)
    
  
  def searchingLoop () :
    global loopTimes
    loopTimes = int(entry.get())
    
    for _ in range(loopTimes) :
      searchesCount = 0
      
      while searchesCount < MAXSEARCHES and not cancelSearchingProcess.is_set():
        print(f"Searched: {searchesCount}")
        pygui.click(xPos, yPos)
        pygui.write(random.choice(words) + " ", random.uniform(0.05, 0.1))
        pygui.press("enter")
        sleeptime = random.randint(10000, 17000) / 1000
        # print(sleeptime)
        
        if cancelSearchingProcess.wait(sleeptime) :
          root.after(0, lambda: showMessage(False))
          return
        
        searchesCount += 1
      
      if loopTimes != 1:
        pygui.keyDown("alt")
        for __ in range(loopTimes) :
          pygui.press("tab")
          print("pressed")
          
        pygui.keyUp("alt")
      
    root.after(0, lambda: showMessage(True))
    listener.stop()
      
  threading.Thread(target = searchingLoop, daemon = True).start()
  
  def whenClick (_, __, button, pressed) :
    if pressed and button == mouse.Button.right :
      cancelSearchingProcess.set()
      listener.stop()
  
  listener = mouse.Listener(on_click = whenClick)
  listener.start()
  
def initUI():
    root.title("Bing Auto Search")
    root.geometry("250x240")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    root.configure(fg_color = "#1e1e2e")

    title = ctk.CTkLabel(
        root,
        text = "Bing Auto Search Tool",
        font = ("Segoe UI", 20, "bold"),
        text_color = "#ffffff"
    )
    title.pack(pady = 25)

    global startTrackingButton
    startTrackingButton = ctk.CTkButton(
        root,
        text = "Start Tracking",
        command = trackingMousePosition,
        font = ("Segoe UI", 11, "bold"),
        height = 45,
        corner_radius = 15,
        fg_color = "#313244",
        hover_color = "#404356",
        text_color = "#ffffff"
    )
    startTrackingButton.pack(fill = "x", padx = 15, pady=6)

    global startSearchingButton
    startSearchingButton = ctk.CTkButton(
        root,
        text = "Start Searching",
        command = searchingProcess,
        font = ("Segoe UI", 11, "bold"),
        height = 45,
        corner_radius = 15,
        fg_color = "#89b4fa",
        hover_color = "#619ffd",
        text_color = "#ffffff"
    )
    startSearchingButton.pack(fill = "x", padx = 15, pady=6)
    
    tabsFrame = ctk.CTkFrame(
          root,
          fg_color = "#1e1e2e")
    
    tabsFrame.pack(pady = 5)
        
    text = ctk.CTkLabel(
      tabsFrame,
      text = "Tabs",
      font = ("Segoe UI", 13, "bold"),
      text_color = "#ffffff"
    )
      
    text.pack(side="left")
    
    global entry
    entry = ctk.CTkEntry(
        tabsFrame,
        textvariable = ctk.IntVar(value = 1 if loopTimes is None else loopTimes),
        width = 60,
        height = 38,
        justify = "center",
        font = ("Segoe UI", 13, "bold"),
        fg_color = "#303044",
        border_color = "#82B0F4",
        border_width = 1,
        text_color = "white",
        corner_radius = 8,
        validate = "key",
        validatecommand = (root.register(lambda input: input.isdigit() or not input), "%P")
    )
  
  
    entry.pack(padx = 15)
    
    def savePosition (_) :
      with open("Tabs.txt", "w") as file :
        file.write(entry.get())
    entry.bind("<FocusOut>", savePosition)
    
    root.mainloop()

getData()
initUI()