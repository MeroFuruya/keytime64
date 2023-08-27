from tkinter import Tk, Label, Button, ttk, Entry, Toplevel, Checkbutton, IntVar, OptionMenu, StringVar
from typing import Callable, TypedDict
from win32gui import GetWindowText, EnumWindows, IsWindowVisible, SetActiveWindow
from win32api import GetKeyState, GetAsyncKeyState

class Key(TypedDict):
  name: str
  keys: str
  time: int
  window: str
  active: bool
SaveCallback = Callable[[str, Key], None]
DeleteCallback = Callable[[str], None]


class MainWindow:
  def __init__(self, master: Tk):
    self.master = master
    self.master.title("keytime64")

    # setup tables
    self.keyTable = ttk.Treeview(master)
    self.keyTable["columns"] = ("name", "keys", "time", "window", "active")
    self.keyTable.column("#0", width=0, stretch=False)
    self.keyTable.column("name", width=100, stretch=False)
    self.keyTable.column("keys", width=100, stretch=False)
    self.keyTable.column("time", width=100, stretch=False)
    self.keyTable.column("window", width=100, stretch=False)
    self.keyTable.column("active", width=100, stretch=False)
    self.keyTable.grid(row=0, column=0, sticky="nsew")
    self.keyTable.bind("<Button-1>", self._on_table_click)
    
    self.keyTable.heading("#0", text="", anchor="w")
    self.keyTable.heading("name", text="Name", anchor="w")
    self.keyTable.heading("keys", text="Keys", anchor="w")
    self.keyTable.heading("time", text="Time", anchor="w")
    self.keyTable.heading("window", text="Window", anchor="w")
    self.keyTable.heading("active", text="Active", anchor="w")
    
    self.keyTable.pack(fill="both", expand=True)
    
    # add key button
    
    self.addKeyButton = Button(master, text="Add Key", command=self._add_key_unknown)
    self.addKeyButton.pack()
    
  def _on_table_click(self, event):
    clicked: str = self.keyTable.identify("item", event.x, event.y)
    if clicked == "": return
    self.edit_key(clicked)
    
  def add_new_empty_key(self) -> str:
    return self.keyTable.insert("", "end", values=("<no name>", "", "", "", ""))

  def _add_key_unknown(self):
    id = self.add_new_empty_key()
    self.edit_key(id)
  
  def edit_key(self, id: str):
    key = self.keyTable.item(id)
    values = {
      "name": key["values"][0],
      "keys": key["values"][1],
      "time": key["values"][2],
      "window": key["values"][3],
      "active": key["values"][4]
    }
    KeyGui(Toplevel(self.master), id, values, self.update_key, self.delete_key)
  
  def update_key(self, id: str, key: Key):
    self.keyTable.item(id, values=(
      key["name"],
      key["keys"],
      key["time"],
      key["window"],
      key["active"]
    ))
  
  def delete_key(self, id: str):
    self.keyTable.delete(id)

class KeyGui:
  def __init__(self, master: Tk, id: str, values: Key, save_callback: SaveCallback or None = None, delete_callback: DeleteCallback or None = None):
    self.master = master
    self.id = id
    self.save_callback = save_callback
    self.delete_callback = delete_callback

    self.master.title(f"keytime64")
    
    self.nameLabel = Label(master, text="Name")
    self.nameLabel.pack()
    
    self.nameEntry = Entry(master)
    self.nameEntry.insert(0, values["name"])
    self.nameEntry.pack()
    
    self.keysLabel = Label(master, text="Keys")
    self.keysLabel.pack()
    
    self.keysEntry = Button(master, text=values["keys"], command=lambda: self.keysEntry.configure(text=self.capture_hotkey()))
    self.keysEntry.pack()
    
    self.timeLabel = Label(master, text="Time")
    self.timeLabel.pack()

    self.timeEntry = Entry(master, validate="all", validatecommand=(self.master.register(lambda P: P.isdigit() or P == ""), '%P'))
    self.timeEntry.insert(0, str(values["time"]))
    self.timeEntry.pack()
    
    self.windowLabel = Label(master, text="Window")
    self.windowLabel.pack()
    
    self.windowVar = StringVar(value=values["window"])
    self.windowEntry = OptionMenu(master, self.windowVar, *self.get_windows())
    self.windowEntry.pack()
    
    self.ActiveVar = IntVar(value=1 if str(values["active"]).lower() == "true" else 0)
    self.activeEntry = Checkbutton(master, text="Active", variable=self.ActiveVar)
    self.activeEntry.pack()
    
    self.saveButton = Button(master, text="Save", command=self.save)
    self.saveButton.pack()
    
    self.deleteButton = Button(master, text="Delete", command=self.delete)
    self.deleteButton.pack()
    
    self.cancelButton = Button(master, text="Cancel", command=self.cancel)
    self.cancelButton.pack()
  
  def save(self):
    if self.save_callback is not None:
      self.save_callback(self.id, {
        "name": self.nameEntry.get(),
        "keys": "",
        "time": int(self.timeEntry.get()) if self.timeEntry.get() != "" else 0,
        "window": self.windowVar.get(),
        "active": self.ActiveVar.get() == 1
      })
    self.master.destroy()
  
  def cancel(self):
    self.master.destroy()
  
  def delete(self):
    if self.delete_callback is not None:
      self.delete_callback(self.id)
    self.master.destroy()
  
  def get_windows(self) -> list[str]:
    windows = []
    def callback(hwnd, extra):
      if IsWindowVisible(hwnd):
        text = GetWindowText(hwnd)
        if text not in ["", "keytime64", "Microsoft Text Input Application", "Program Manager", "Settings"]:
          windows.append(text)
    EnumWindows(callback, None)
    return windows
  
  def capture_hotkey(self) -> str:
    keys = []
    while True:
      for i in range(256):
        if GetAsyncKeyState(i) != 0:
          keys.append(i)
          break
      if len(keys) > 0 and GetKeyState(0x1B) != 0:
        break
    return "+".join(keys)

root = Tk()
my_gui = MainWindow(root)
root.mainloop()


