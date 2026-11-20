import random
import subprocess
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

def runShutdown (*args) :
  # Windows-only: "shutdown /s /t 60" to schedule, "shutdown /a" to abort
  subprocess.run(["shutdown", *args],
                 creationflags = subprocess.CREATE_NO_WINDOW,
                 check = False)

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

def loadShutdown () :
  try :
    with open("Shutdown.txt", "r") as file :
      return file.read().strip() == "1"
  except OSError :
    return False

def saveShutdown () :
  with open("Shutdown.txt", "w") as file :
    file.write("1" if shutdownVar.get() else "0")

def saveTabs (_ = None) :
  with open("Tabs.txt", "w") as file :
    file.write(entry.get())

def trackingMousePosition () :
  startTrackingButton.configure(command = None)
  
  def finishTracking () :
    startTrackingButton.configure(command = trackingMousePosition)
    messagebox.showinfo(title = "Successful", 
                        message = "Finished retrieving mouse position",
                        parent = root)
  
  def whenClick (x, y, _, pressed) :
    global xPos, yPos
    
    if pressed :
      xPos, yPos = x, y
      
      with open("Mouse position.txt", "w") as file :
        file.write(f"{x} {y}")
      
      root.after(0, finishTracking)
      return False  # stops the listener
  
  # Non-blocking: the UI stays responsive while waiting for the click
  mouse.Listener(on_click = whenClick).start()

def searchingProcess () :
  global loopTimes
  
  if xPos is None or yPos is None :
    messagebox.showerror(title = "Error",
                         message = f"Invalid mouse position \n (x: {xPos} y: {yPos})",
                         parent = root)
    return
  
  if not words :
    messagebox.showerror(title = "Error",
                         message = "Common words.txt is empty",
                         parent = root)
    return
  
  # Read the entry here (main thread). Tkinter widgets must not be touched from other threads.
  tabsText = entry.get()
  if not tabsText :
    messagebox.showerror(parent = root,
                         message = "Tab fill cannot be empty",
                         title = "Error")
    return
  
  tabs = int(tabsText)
  if tabs == 0 :
    messagebox.showerror(parent = root,
                         message = "Tab fill cannot be zero",
                         title = "Error")
    return
  
  loopTimes = tabs
  saveTabs()
  
  startSearchingButton.configure(text = "Right-click to cancel",
                                 command = None)
  startTrackingButton.configure(command = None)
  cancelSearchingProcess = threading.Event()
  
  def whenClick (_, __, button, pressed) :
    if pressed and button == mouse.Button.right :
      cancelSearchingProcess.set()
      return False  # stops the listener
  
  # Created before the worker thread starts, so the thread can never see it undefined
  listener = mouse.Listener(on_click = whenClick)
  
  def showMessage (result, error) :
    listener.stop()
    startSearchingButton.configure(text = "Start Searching",
                                   command = searchingProcess)
    startTrackingButton.configure(command = trackingMousePosition)
    
    if result == "cancel" :
      messagebox.showinfo(title = "Cancel",
                          message = "Task cancelled by user",
                          parent = root)
    elif result == "error" :
      messagebox.showerror(title = "Error",
                           message = f"Something went wrong:\n{error}",
                           parent = root)
    elif shutdownVar.get() :
      # Shut down after 60 seconds, giving the user time to cancel
      runShutdown("/s", "/t", "60")
      answer = messagebox.askyesno(
          title = "Shutdown",
          message = "Your PC will shut down in 60 seconds.\nDo you want to cancel the shutdown?",
          parent = root)
      if answer :
        runShutdown("/a")
    else :
      messagebox.showinfo(title = "Successful",
                          message = "Searching Completed",
                          parent = root)
  
  def switchWindow () :
    pygui.keyDown("alt")
    try :
      for _ in range(tabs) :
        pygui.press("tab")
    finally :
      pygui.keyUp("alt")  # never leave alt stuck down
  
  def runSearches () :
    """Returns True if finished, False if cancelled."""
    for _ in range(tabs) :
      for __ in range(MAXSEARCHES) :
        pygui.click(xPos, yPos)
        pygui.write(random.choice(words) + " ", random.uniform(0.05, 0.1))
        pygui.press("enter")
        
        if cancelSearchingProcess.wait(random.uniform(10, 17)) :
          return False
      
      if tabs != 1 :
        switchWindow()
        if cancelSearchingProcess.is_set() :
          return False
    return True
  
  def searchingLoop () :
    result, error = "done", ""
    try :
      if not runSearches() :
        result = "cancel"
    except Exception as e :  # e.g. pyautogui fail-safe (mouse moved to a corner)
      result, error = "error", str(e)
    root.after(0, lambda: showMessage(result, error))
  
  listener.start()
  threading.Thread(target = searchingLoop, daemon = True).start()
  
def initUI():
    root.title("Bing Auto Search")
    root.geometry("250x280")
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
    startTrackingButton.pack(fill = "x", padx = 15, pady = 6)

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
    startSearchingButton.pack(fill = "x", padx = 15, pady = 6)
    
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
      
    text.pack(side = "left")
    
    global entry
    entry = ctk.CTkEntry(
        tabsFrame,
        textvariable = ctk.StringVar(value = str(1 if loopTimes is None else loopTimes)),
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
        validatecommand = (root.register(lambda input: input.isdecimal() or not input), "%P")
    )
    entry.pack(padx = 15)
    entry.bind("<FocusOut>", saveTabs)
    
    global shutdownVar
    shutdownVar = ctk.BooleanVar(value = loadShutdown())
    shutdownCheck = ctk.CTkCheckBox(
        root,
        text = "Shutdown when done",
        variable = shutdownVar,
        command = saveShutdown,
        font = ("Segoe UI", 10),
        text_color = "#ffffff",
        checkbox_width = 16,
        checkbox_height = 16,
        border_width = 1,
        corner_radius = 4
    )
    shutdownCheck.pack(pady = 6)

if __name__ == "__main__" :
  getData()
  initUI()
  root.mainloop()