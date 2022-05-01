from tkinter import ttk, messagebox
import tkinter as tk
import os
import work
import json
import yaml

def fixed_map(option, style):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
        elm[:2] != ('!disabled', '!selected')]


class BotTkuuuru():
    def __init__(self, root) -> None:
        
        self.root:tk.Tk = root
        
        with open("config.yml", "r") as yml:
            self.config = yaml.safe_load(yml)
        
        #スタイルで変更できないwidgetに使う
        self.not_save_color = "yellow"
        self.defalt_bg = "white"
        
        style = ttk.Style()
        style.theme_use("clam")
        if self.config["style"] == "dark":
            style.configure("MainManu.TButton", font=("Yu Gothic UI Semibold", 12, "bold"), background="#333333", foreground="#e6e6e6")
            style.configure("Treeview.Heading", font=("Yu Gothic UI Semibold", 12, "bold"), background="#333333", foreground="#e6e6e6")
            style.configure("Treeview", font=("Yu Gothic UI Semibold", 12, "bold"),  background="#333333",fieldbackground="#333333", foreground="#e6e6e6")
            style.configure("MYStyle.TButton", font=("Yu Gothic UI Semibold", 8), background="#7daab3", foreground="#333333")
            style.configure("NodeStyle.TButton", font=("Yu Gothic UI Semibold", 8), background="#47b3a1", foreground="#e6e6e6")
            style.configure("Delete.TButton", font=("Yu Gothic UI Semibold", 10), background="#663333", foreground="#e6e6e6")
            style.configure("Green.TButton", font=("Yu Gothic UI Semibold", 10), background="#336633", foreground="#e6e6e6")
            style.configure("MYStyle.TFrame", font=("Yu Gothic UI Semibold", 8), background="#333333")
            style.configure("Dict.TLabelframe", font=("Yu Gothic UI Semibold", 8), background="#333333", foreground="green")
            style.configure("Dict.TLabelframe.Label", font=("Yu Gothic UI Semibold", 8), background="#333333", foreground="green")
            style.configure("TopStyle.TLabel", font=("Yu Gothic UI Semibold", 8), background="#333333", foreground="#e6e6e6")
            style.configure("MYStyle.TLabel", font=("Yu Gothic UI Semibold", 10), background="#333333", foreground="#e6e6e6")
            style.configure("Setting.TLabel", font=("Yu Gothic UI Semibold", 12), background="#333333", foreground="#e6e6e6")
            style.configure("NotSaveStyle.TLabel", font=("Yu Gothic UI Semibold", 7), background="#333333", foreground="#808080")
            style.configure("MYStyle.TCheckbutton", font=("Yu Gothic UI Semibold", 10), background="#333333", foreground="#e6e6e6")
            style.configure("Close.TButton", font=("Yu Gothic UI Semibold", 8, "bold"), background="#333333", foreground="#e6e6e6")
            style.configure("Option.TCheckbutton", font=("Yu Gothic UI Semibold", 15), background="#333333", foreground="#e6e6e6")
            
            
            style.map('Treeview', foreground=fixed_map('foreground', style), background=fixed_map('background', style))
            style.map("MainManu.TButton", foreground=[('active', "#333333")])
            style.map("Close.TButton", foreground=[('active', "#333333")])
            style.map("NodeStyle.TButton", background=[('active', "#5df0d7")])
            style.map("Delete.TButton", background=[('active', "#cc2929")])
            style.map("Green.TButton", background=[('active', "#12b32d")])
            style.map("MYStyle.TCheckbutton", background=[('active', "#e6e6e6")], foreground=[("active", "#333333")])
            style.map("Option.TCheckbutton", background=[('active', "#e6e6e6")], foreground=[("active", "#333333")])
            
            self.not_save_color = "#ffff99"
            self.defalt_bg = "#333333"
            
        if self.config["style"] == "light":
            style.configure("MainManu.TButton", font=("Yu Gothic UI Semibold", 12, "bold"), background="#e6e6e6", foreground="#333333")
            style.configure("Treeview.Heading", font=("Yu Gothic UI Semibold", 12, "bold"), background="#e6e6e6", foreground="#333333")
            style.configure("Treeview", font=("Yu Gothic UI Semibold", 12, "bold"),  background="#e6e6e6",fieldbackground="#e6e6e6", foreground="#333333")
            style.configure("MYStyle.TButton", font=("Yu Gothic UI Semibold", 8), background="#708ce0", foreground="#e6e6e6")
            style.configure("NodeStyle.TButton", font=("Yu Gothic UI Semibold", 8), background="#47b3a1", foreground="#e6e6e6")
            style.configure("Delete.TButton", font=("Yu Gothic UI Semibold", 10), background="#cc5252", foreground="#e6e6e6")
            style.configure("Green.TButton", font=("Yu Gothic UI Semibold", 10), background="#3dcc7d", foreground="#e6e6e6")
            style.configure("MYStyle.TFrame", font=("Yu Gothic UI Semibold", 8), background="#e6e6e6")
            style.configure("Dict.TLabelframe", font=("Yu Gothic UI Semibold", 8), background="#e6e6e6", foreground="green")
            style.configure("Dict.TLabelframe.Label", font=("Yu Gothic UI Semibold", 8), background="#e6e6e6", foreground="green")
            style.configure("TopStyle.TLabel", font=("Yu Gothic UI Semibold", 8), background="#e6e6e6", foreground="#333333")
            style.configure("MYStyle.TLabel", font=("Yu Gothic UI Semibold", 10), background="#e6e6e6", foreground="#333333")
            style.configure("Setting.TLabel", font=("Yu Gothic UI Semibold", 12), background="#e6e6e6", foreground="#333333")
            style.configure("NotSaveStyle.TLabel", font=("Yu Gothic UI Semibold", 7), background="#e6e6e6", foreground="#808080")
            style.configure("MYStyle.TCheckbutton", font=("Yu Gothic UI Semibold", 10), background="#e6e6e6", foreground="#333333")
            style.configure("Close.TButton", font=("Yu Gothic UI Semibold", 8, "bold"), background="#e6e6e6", foreground="#333333")
            style.configure("Option.TCheckbutton", font=("Yu Gothic UI Semibold", 15), background="#e6e6e6", foreground="#333333")
            
            style.map('Treeview', foreground=fixed_map('foreground', style), background=fixed_map('background', style))
            style.map("MainManu.TButton", background=[('active', "#cccccc")])
            style.map("Close.TButton", background=[('active', "#cccccc")])
            style.map("NodeStyle.TButton", background=[('active', "#5df0d7")])
            style.map("Delete.TButton", background=[('active', "#cc2929")])
            style.map("Green.TButton", background=[('active', "#12b32d")])
            style.map("MYStyle.TCheckbutton", background=[('active', "#e6e6e6")], foreground=[("active", "#333333")])
            style.map("Option.TCheckbutton", background=[('active', "#e6e6e6")], foreground=[("active", "#333333")])
        
            self.not_save_color = "#b4cc3d"
            self.defalt_bg ="#e6e6e6"
        
        
        self.root.tk.eval("""
                        ttk::style map Treeview \
                        -foreground {disabled SystemGrayText \
                                    selected SystemHighlightText} \
                        -background {disabled SystemButtonFace \
                                    selected SystemHighlight}
                    """)
        
        self.root.title("botツクール")
        self.root.geometry("1500x600")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.root.protocol("WM_DELETE_WINDOW", self.click_close_btn)
        
        self.menubar = tk.Menu(root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        
        self.filemenu.add_command(label="新規作成", command=lambda: self.might_show_win("Creation"))
        self.filemenu.add_command(label="開く", command=lambda: self.might_show_win("Open"))
        self.filemenu.add_command(label="スタートメニュー", command=lambda: self.might_show_win("Start"))
        self.filemenu.add_command(label="閉じる")
        self.menubar.add_cascade(label="設定", command=self.show_setting)
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
        self.frames["Work"] = work.WorkFrame(master=self.root, file=file, file_name=file_name, bt=self)
        self.frames["Work"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("Work")
    
    def click_close_btn(self):
        #WorkFrameを開いてる時だけ保存するか聞きたっかった
        if "Work" not in self.frames:
            self.root.destroy()
            return
        self.conf_win = SaveConfirmationWindow(self.defalt_bg, self.root.destroy, self.save)
    
    def might_show_win(self, name):
        #WorkFrameを開いてる時だけ保存するか聞きたっかった
        if "Work" not in self.frames:
            self.show_frame(name)
            return
        self.conf_win = SaveConfirmationWindow(self.defalt_bg, lambda:self._work_destroy_to_show_frame(name), self.save)
    
    def _work_destroy_to_show_frame(self, name):
        self.frames["Work"].destroy()
        self.frames.pop("Work")
        self.conf_win.destroy()
        self.show_frame(name)
    
    def save(self, func):
        self.frames["Work"].top_left_frame.save(conf=False)
        func()
        
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
    
    def show_setting(self):
        setting_win = Setting(self, self.defalt_bg)
        setting_win.geometry("450x600")
        setting_win.grab_set()

class SaveConfirmationWindow(tk.Toplevel):
    def __init__(self, bg = "", func = None, save_func = None) -> None:
        super().__init__(bg=bg)
        
        self.title("確認")
        self.geometry("300x100+810+490")
        self.grab_set()
        description_lab = ttk.Label(self, text="閉じる前に変更を保存しますか?", style="MYStyle.TLabel")
        
        save_btn = ttk.Button(
            self, text="保存する", 
            command=lambda: save_func(func),
            style="Close.TButton")
        
        not_save_btn = ttk.Button(
            self, text="保存しない", 
            command=func,
            style="Close.TButton")
        
        cancel_btn = ttk.Button(
            self, text="キャンセル", 
            command=lambda: self.destroy(), 
            style="Close.TButton")
        
        description_lab.grid(row=0, column=0, columnspan=3, pady=10)
        save_btn.grid(row=1, column=0, padx=10)
        not_save_btn.grid(row=1, column=1, padx=10)
        cancel_btn.grid(row=1, column=2, padx=10)
        
        
class StartFrame(ttk.Frame):
    
    def __init__(self, master = None, controller = None) -> None:
        super().__init__(master, style="MYStyle.TFrame")
        
        self.left_frame = ttk.Frame(self, style="MYStyle.TFrame")
        self.right_frame = ttk.Frame(self, style="MYStyle.TFrame")
        
        self.creation_btn = ttk.Button(
            self.left_frame, 
            text="＋新規作成", 
            command=lambda: controller.show_frame("Creation"), 
            width = 20,
            padding=40,
            style="MainManu.TButton")
        self.open_btn = ttk.Button(
            self.right_frame, 
            text="開く",
            command=lambda: controller.show_frame("Open"),
            width = 20,
            padding=40,
            style="MainManu.TButton")
        
        self.left_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.right_frame.grid(row=0, column=1, sticky=tk.NSEW)

        self.creation_btn.pack(anchor='center', expand=1)
        self.open_btn.pack(anchor='center', expand=1)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        

class CreationFrame(ttk.Frame):
    def __init__(self, master = None, controller = None) -> None:
        super().__init__(master, style="MYStyle.TFrame")
        
        self.controller = controller
        
        self.frame = ttk.Frame(self, style="MYStyle.TFrame")
        
        self.title_lbl = ttk.Label(self.frame, text="新規作成", style="MYStyle.TLabel")
        self.name_lbl = ttk.Label(self.frame, text="名前", style="MYStyle.TLabel")
        self.name_entry = ttk.Entry(self.frame, width=40)
        self.token_lbl = ttk.Label(self.frame, text="TOKEN", style="MYStyle.TLabel")
        self.token_entry = ttk.Entry(self.frame, width=40)
        self.prefix_lbl = ttk.Label(self.frame, text="PREFIX", style="MYStyle.TLabel")
        self.prefix_entry = ttk.Entry(self.frame, width=40)
        self.prefix_entry.insert(0,"/")
        self.create_btn = ttk.Button(
            self.frame, text="作成", 
            command=self.create,
            style="MainManu.TButton")
        self.close_btn = ttk.Button(
            self.frame, text="閉じる", 
            command=lambda: self.controller.show_frame("Start"),
            style="MainManu.TButton")
        
        self.frame.grid(row=0, column=0)

        self.title_lbl.grid(row=0, column=2)
        self.name_lbl.grid(row=1, column=1)
        self.name_entry.grid(row=1, column=2)
        self.token_lbl.grid(row=2, column=1)
        self.token_entry.grid(row=2, column=2)
        self.prefix_lbl.grid(row=3, column=1)
        self.prefix_entry.grid(row=3, column=2)
        self.create_btn.grid(row=4, column=2)
        self.close_btn.grid(row = 5, column=2)
        
        self.grid_columnconfigure(0, weight=1)
    
    def create(self):
        name = self.name_entry.get()
        token = self.token_entry.get()
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

class OpenFrame(ttk.Frame):
    def __init__(self, master = None, controller = None) -> None:
        super().__init__(master, style="MYStyle.TFrame")

        self.controller = controller
        self.files = os.listdir(".\data")
        
        self.title_lbl = ttk.Label(self, text="ファイル名", style="MYStyle.TLabel")
        self.file_com = ttk.Combobox(self, values=self.files, width=50)
        self.open_btn = ttk.Button(
            self, text="開く", 
            command=self.open,
            style="MainManu.TButton")
        self.close_btn = ttk.Button(
            self, text="閉じる", 
            command=lambda: controller.show_frame("Start"),
            style="MainManu.TButton")
        
        self.title_lbl.pack(anchor='center')
        self.file_com.pack(anchor='center')
        self.open_btn.pack(anchor='center')
        self.close_btn.pack(anchor='center')
        
    
    def open(self):
        files = os.listdir(".\data")
        name = self.file_com.get()
        if name not in files:
            messagebox.showerror('エラー', '選択されたファイルがありません')
            return
        name = name.replace(".json", "")
        self.controller.create_work_frame(name)

class Setting(tk.Toplevel):
    
    styles = ["dark", "light"]
    
    def __init__(self, controller = None, bg=None) -> None:
        super().__init__(bg=bg)
        
        self.con = controller
        
        self.frame = ttk.Frame(self, style="MYStyle.TFrame")
        self.save_frame = ttk.Frame(self, style="MYStyle.TFrame")
        
        self.title_lbl = ttk.Label(self.frame, text="設定", style="Setting.TLabel")
        self.need_save_lab = ttk.Label(self.frame, text="", style="NotSaveStyle.TLabel")
        
        self.style_lab = ttk.Label(self.frame, text="スタイル", style="MYStyle.TLabel")
        self.style_com = ttk.Combobox(self.frame, values=self.styles)
        self.attention_lab = ttk.Label(self.frame, text="※スタイルを変更するには再起動してください", style="NotSaveStyle.TLabel")
        self.change_btn = ttk.Button(self.save_frame, text="変更を保存", command=self.save, style="Green.TButton")
        
        self.style_com.insert(0, self.con.config["style"])
        
        self.style_com.bind("<<ComboboxSelected>>", self.on_change)
        
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.save_frame.grid(row=1, column=0, sticky="se")
        
        self.title_lbl.grid(row=0, column=0, columnspan=10, pady=10)
        self.need_save_lab.grid(row=1, column=1)
        self.style_lab.grid(row=2, column=0)
        self.style_com.grid(row=2, column=1)
        self.attention_lab.grid(row=2, column=2)
        self.change_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def on_change(self, event):
        self.need_save_lab["text"] = "変更を保存されたていません"
        
    def save(self):
        style = self.style_com.get()
        
        if style not in self.styles:
            messagebox.showerror("エラー", "スタイルが間違っています")
            return
        
        if not messagebox.askquestion("確認", "変更を保存しますか?"):
            return
        
        self.con.config["style"] = style
        self.need_save_lab["text"] = ""
        
        with open("config.yml", "w") as yml:
            yaml.safe_dump(self.con.config, yml, encoding="utf-8")

if __name__ == "__main__":
    root = tk.Tk()
    BotTkuuuru(root)
    root.mainloop()
        
        