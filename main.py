import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import os
import work
import json


class BotTkuuuru():
    def __init__(self, root) -> None:
        self.root = root
        
        self.root.title("botツクール")
        self.root.geometry("1500x600")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.menubar = tk.Menu(root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        
        self.filemenu.add_command(label="新規作成", command=lambda: self.show_frame("Creation"))
        self.filemenu.add_command(label="開く", command=lambda: self.show_frame("Open"))
        self.filemenu.add_command(label="スタートメニュー", command=lambda: self.show_frame("Start"))
        self.filemenu.add_command(label="閉じる")
        self.menubar.add_cascade(label="ファイル", menu=self.filemenu)
        self.root.config(menu=self.menubar)
        
        self.frames = {}
        self.frames["Start"] = StartFrame(master=self.root, controller=self)
        self.frames["Creation"] = CreationFrame(master=self.root, controller=self)
        self.frames["Open"] = OpenFrame(master=self.root, controller=self)
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("Start")
    
    def create_work_frame(self, file_name):
        with open(f".\data\{file_name}.json", "r", encoding="utf-8") as j:
            file = json.load(j)
        self.frames["Work"] = work.WorkFrame(master=self.root, file=file, file_name=file_name)
        self.frames["Work"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("Work")
        
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        
class StartFrame(tk.Frame):
    
    def __init__(self, master = None, controller = None) -> None:
        super().__init__(master)
        
        self.creation_btn = ttk.Button(
            self, text="新規作成", 
            command=lambda: controller.show_frame("Creation"), 
            width = 20,
            padding=40)
        self.open_btn = ttk.Button(
            self, 
            text="開く",
            command=lambda: controller.show_frame("Open"),
            width = 20,
            padding=40)

        self.creation_btn.grid(row=0, column=0, padx=(230,0), pady=(200,0))
        self.open_btn.grid(row=0, column=1, padx=(100,0), pady=(200,0))
        
         

class CreationFrame(tk.Frame):
    def __init__(self, master = None, controller = None) -> None:
        super().__init__(master)
        
        self.controller = controller
        
        self.title_lbl = ttk.Label(self, text="新規作成")
        self.name_lbl = ttk.Label(self, text="名前")
        self.name_entry = ttk.Entry(self, width=40)
        self.token_lbl = ttk.Label(self, text="TOKEN")
        self.token_entry = ttk.Entry(self, width=40)
        self.prefix_lbl = ttk.Label(self, text="PREFIX")
        self.prefix_entry = ttk.Entry(self, width=40)
        self.prefix_entry.insert(0,"/")
        self.create_btn = ttk.Button(
            self, text="作成", 
            command=self.create)
        self.close_btn = ttk.Button(
            self, text="閉じる", 
            command=lambda: self.controller.show_frame("Start"))

        self.grid_columnconfigure(0, minsize=350)
        self.title_lbl.grid(row=0, column=2)
        self.name_lbl.grid(row=1, column=1)
        self.name_entry.grid(row=1, column=2)
        self.token_lbl.grid(row=2, column=1)
        self.token_entry.grid(row=2, column=2)
        self.prefix_lbl.grid(row=3, column=1)
        self.prefix_entry.grid(row=3, column=2)
        self.create_btn.grid(row=4, column=2)
        self.close_btn.grid(row = 5, column=2)
    
    def create(self):
        name = self.name_entry.get()
        token = self.name_entry.get()
        prefix = self.prefix_entry.get()
        
        if "" in (name, prefix):
            messagebox.showerror("Error", "名前またはPREFIXが空です")
            return
        
        j = {"commands":{},
             "vars": {}, 
             "token": token, 
             "prefix": prefix
            }
        
        with open(f".\data\{name}.json", "w") as file:
            json.dump(j, file, ensure_ascii=False, indent=4)
        
        self.controller.create_work_frame(name)

class OpenFrame(tk.Frame):
    def __init__(self, master = None, controller = None) -> None:
        super().__init__(master)

        self.controller = controller
        self.files = os.listdir(".\data")
        
        self.file_com = ttk.Combobox(self, values=self.files, width=50)
        self.open_btn = ttk.Button(
            self, text="開く", 
            command=self.open)
        self.close_btn = ttk.Button(
            self, text="閉じる", 
            command=lambda: controller.show_frame("Start"))
        
        self.grid_columnconfigure(0, minsize=330)
        self.file_com.grid(row=0, column=1)
        self.open_btn.grid(row=1, column=1)
        self.close_btn.grid(row=2, column=1)
        
    
    def open(self):
        files = os.listdir(".\data")
        name = self.file_com.get()
        if name not in files:
            messagebox.showerror('エラー', '選択されたファイルがありません')
            return
        name = name.replace(".json", "")
        self.controller.create_work_frame(name)


if __name__ == "__main__":
    root = tk.Tk()
    BotTkuuuru(root)
    root.mainloop()
        
        