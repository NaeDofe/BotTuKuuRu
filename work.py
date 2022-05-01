from platform import node
from tkinter import ttk, messagebox
from venv import create
from varset import AddVariableFrame, VariableDetailFrame
import tkinter as tk
import json
import nodede
import os
import threading
import subprocess
import yaml

class WorkFrame(ttk.Frame):
    
    def __init__(self, master = None, file = None, file_name = "", bt = None):
        super().__init__(master)
        
        self.file = file
        self.bt = bt
        
        self.file_name = file_name
        self.token = file["token"]
        self.prefix = file["prefix"]
        
        self.right_command_frame = RightCommandFrame(master=self, file=self.file)
        
        self.bottom_left_frame = BottomLeftFrame(master=self)
        self.top_left_frame = TopLeftFrame(master=self)
        
        self.bottom_left_frame.set_node_frame()
        
        self.right_command_frame.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)
        
        self.top_left_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.bottom_left_frame.grid(row=1, column=0,sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
class TopLeftFrame(ttk.Frame):
    def __init__(self, master: WorkFrame = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.con = master
        self.command = self.con.right_command_frame
        self.bottom = self.con.bottom_left_frame
        
        self.bot_is_run = False
        self.mode = 0
        self.selected_var_id = ""
        
        
        self.execution_btn = ttk.Button(self, text="実行", command=self.execution, style="MYStyle.TButton")
        self.save_btn = ttk.Button(self, text="保存", command=self.save, style="MYStyle.TButton")
        self.detail_btn = ttk.Button(self, text="詳細設定", command=lambda: self.bottom.show_frame("Detail"), style="MYStyle.TButton")
        self.node_add_btn = ttk.Button(self, text="ノード追加", command=lambda: self.bottom.show_frame("Node"), style="MYStyle.TButton")
        self.var_add_btn = ttk.Button(self, text="変数追加", command=lambda: self.bottom.show_frame("Variable"), style="MYStyle.TButton")
        self.command_add_btn = ttk.Button(self, text="コマンド追加", command=lambda: self.bottom.show_frame("Command"), style="MYStyle.TButton")
        self.mode_lbl_frame = ttk.Labelframe(self,text="モード", style="Dict.TLabelframe")
        self.mode_lbl = ttk.Label(self.mode_lbl_frame, text="選択", style="TopStyle.TLabel")
        self.selection_node_frame = ttk.Labelframe(self,text="ノード", style="Dict.TLabelframe")
        self.selection_node_lbl = ttk.Label(self.selection_node_frame, text="", style="TopStyle.TLabel")
        self.selection_btn = ttk.Button(self, text="選択", command=self.selection, style="MYStyle.TButton")
        self.move_btn = ttk.Button(self, text="移動", command=self.move, style="MYStyle.TButton")
        self.child_btn = ttk.Button(self, text="子供", command=self.child, style="MYStyle.TButton")
        
        self.execution_btn.grid(row=0, column=0)
        self.save_btn.grid(row=0, column=1)
        self.detail_btn.grid(row=0, column=2)
        self.node_add_btn.grid(row=1, column=0)
        self.var_add_btn.grid(row=1, column=2)
        self.command_add_btn.grid(row=1, column=1)
        self.mode_lbl_frame.grid(row=2, column=0 )
        self.selection_btn.grid(row=3, column=0)
        self.selection_node_frame.grid(row=3, column=1, columnspan=2)
        self.move_btn.grid(row=4, column=0)
        self.child_btn.grid(row=5, column=0)
        
        self.mode_lbl.pack()
        self.selection_node_lbl.pack()
        
        self.var_tree = ttk.Treeview(self)
        self.var_tree['columns'] = ('ID','Name','Score')
        self.var_tree.column('#0',width=0, stretch='no')
        self.var_tree.column('ID', anchor='center', width=60)
        self.var_tree.column('Name',anchor='w', width=100)
        self.var_tree.column('Score', anchor='center', width=80)
        
        self.var_tree.heading('#0',text='')
        self.var_tree.heading('ID', text='型',anchor='center')
        self.var_tree.heading('Name', text='名前', anchor='w')
        self.var_tree.heading('Score',text='初期値', anchor='center')
        
        self.variables = {}
        self._file_to_tree()
        self.var_tree.bind("<<TreeviewSelect>>", self.select_var_tree)
        self.var_tree.grid(row=0, column=4, rowspan=6)
        
        self.bottom.show_frame("Empty")
    
    def _file_to_tree(self):
        for name, vals in self.con.file["vars"].items():
            self.var_tree.insert(parent='', index='end', values=(vals[0], name, vals[1]))
            frame = VariableDetailFrame(master=self.bottom, top=self, var_name=name, var_type=vals[0], var_default=vals[1])
            frame.grid(row=0, column=0, sticky="nsew")
            self.variables[name] = {"type":vals[0], "val":vals[1], "frame": frame}
        
    def select_var_tree(self, event):
        self.selected_var_id = self.var_tree.focus()
        name = self.var_tree.item(self.selected_var_id, "values")[1]
        self.bottom.show_varpre_frame(name)
        
    def execution(self):
        if self.bot_is_run:
            messagebox.showerror("エラー", "すでにbotを実行しています")
            return
        if not messagebox.askyesno("確認", "botを実行しますか?"):
            return
        if not self.save(conf=False):
            return
        
        with open("config.yml", "r", encoding="utf-8") as yml:
            config = yaml.safe_load(yml)
            
        config["open_file_name"] = self.con.file_name
        
        with open("config.yml", "w", encoding="utf-8") as yml:
            yaml.safe_dump(config, yml)
        
        thread = threading.Thread(target=self._bot_run)
        thread.start()
    
    def _bot_run(self):
        self.bot_is_run = True
        subprocess.call("py bot.py")
        self.bot_is_run = False
    
    def save(self, conf = True):
        if conf:
            if not messagebox.askyesno("確認", "ファイルを保存しますか?"):
                return False
        
        command_trees = self.command.command_trees
        
        command_dic = {}
        for command_name, command_tree in command_trees.items():
            command_dic[command_name] = self._tree_to_dict(command_tree, "", command_name)
        
        self.con.file["commands"] = command_dic
        self.con.file["vars"] = self._variables_to_file_data()
        self.con.file["token"] = self.con.token
        self.con.file["prefix"] = self.con.prefix
        
        with open(f".\data\{self.con.file_name}.json", "w", encoding='utf-8') as f:
            json.dump(self.con.file, f, ensure_ascii=False, indent=4)
        
        return True
    
    def _tree_to_dict(self, tree, parent, command_name):
        dic = {}
        for item in tree.get_children(parent):
            name = tree.item(item, "text")
            data = self.command.node_settings[command_name][item]["data"]
            dic[item] = [name, self._tree_to_dict(tree, item, command_name), data ]
        return dic

    def _variables_to_file_data(self):
        dic = {}
        for name, data in self.variables.items():
            dic[name] = [data["type"], data["val"]]
        return dic
        
    
    def selection(self):
        self.mode = 0
        self.command.selected_id = ""
        self.selection_node_lbl["text"] = ""
        self.mode_lbl["text"] = "選択"
    
    def move(self):
        self.mode = 1
        self.command.selected_id = ""
        self.selection_node_lbl["text"] = ""
        self.mode_lbl["text"] = "移動"
    
    def child(self):
        self.mode = 2
        self.command.selected_id = ""
        self.selection_node_lbl["text"] = ""
        self.mode_lbl["text"] = "子供"


class RightCommandFrame(ttk.Frame):
    def __init__(self, master: WorkFrame = None, file = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.con = master
        self.file = file
        
        self.node_settings = {}
        self.command_trees = {}
        self.command_setting_frames = {}
        self.copy_nodes = None
        self.selected_id = ""
        self.now_command_name = ""
        
        self.command_note = ttk.Notebook(self)
        self.command_note.bind("<<NotebookTabChanged>>", self.tab_changed)
        self._file_to_commad()
        self.command_note.pack(fill="both", side="right")
    
    def _file_to_commad(self):
        for command_name, data_dic in self.file["commands"].items():
            command_tree = ttk.Treeview(self.command_note, height=30)
            command_tree.column("#0", width=500)
            command_tree.heading("#0", text=command_name)
            self._file_to_tree(command_tree, "", data_dic, command_name)
            command_tree.bind("<<TreeviewSelect>>", self.select_node)
            command_tree.bind("<Control-c>", self.copy)
            command_tree.bind("<Control-v>", self.paste)
            command_tree.bind("<Control-d>", self.deletion)
            command_tree.bind("<Control-s>", self.node_save)
            command_tree.tag_configure("not_save", foreground=self.con.bt.not_save_color)
            command_tree.pack(fill="x")
            self.command_trees[command_name] = command_tree
            self.command_note.add(command_tree, text=command_name)
        
    def _file_to_tree(self, tree, parent, data_dic, command_name):
        self.node_settings[command_name] = {}
        for val in data_dic.values():
            
            node_name = val[0]
            child_data = val[1]
            node_data = val[2]
            
            node_id = tree.insert(parent=parent, index="end", text=node_name)
            self.node_settings[command_name][node_id] = {"name": node_name, "data": node_data}
            
            if any(child_data):
                self._file_to_tree(tree, node_id, child_data, command_name)
    
    def show_node_frame(self, node_id):
        frame = self.node_settings[self.now_command_name][node_id]["frame"]
        frame.tkraise()
    
    def select_node(self, event):
        tree = self.command_trees[self.now_command_name]
        item_id = tree.focus()
        item_name = tree.item(item_id, "text")
        item_parent = tree.parent(item_id)
        
        mode = self.con.top_left_frame.mode
        node_lab = self.con.top_left_frame.selection_node_lbl
        
        if mode == 0:
            node_lab["text"] = item_name
            self.selected_id = item_id
            self.show_node_frame(item_id)
            return
            
        if not self.can_move(tree, item_id, item_parent):
            messagebox.showerror("Error", "その移動は不可能です")
            self.selected_id = ""
            node_lab["text"] = ""
            return
        
        if self.selected_id == "":
            self.selected_id = item_id
            node_lab["text"] = item_name
            return
        
        if mode == 1:
            index = tree.index(item_id)
            tree.move(self.selected_id, item_parent, index)
            self.selected_id = ""
            node_lab["text"] = ""
            
        if mode == 2:
            if self.selected_id != item_id:
                tree.move(self.selected_id, item_id, "end")
            self.selected_id = ""
            node_lab["text"] = ""
    
    def can_move(self, tree, item, parent) -> bool:
        while item != "":
            if parent == "":
                return True
            if parent == item:
                return False
            parent = tree.parent(parent)
        return True
        
    def tab_changed(self, event):
        select_id = self.command_note.select() 
        if select_id == "":
            return
        self.now_command_name = self.command_note.tab(select_id, "text")
    
    def copy(self, event):
        tree: ttk.Treeview = self.command_trees[self.now_command_name]
        node_ids = tree.selection()
        if not any(node_ids):
            return
        self.copy_nodes = [self.node_settings[self.now_command_name][node_id].copy() for node_id in node_ids]
    
    def paste(self, event):
        if self.copy_nodes is None:
            return
        tree: ttk.Treeview = self.command_trees[self.now_command_name]
        item_id = tree.selection()[-1]
         
        index = "end"
        parent = ""
        if any(item_id):
            index = tree.index(item_id)+1
            parent = tree.parent(item_id)
        
        for copy_node in reversed(self.copy_nodes):
            name = copy_node["name"]
            data = copy_node["data"]
            node_id = tree.insert(parent, index, text=name)
            frame = self.con.bottom_left_frame.create_node_frame(self.now_command_name, node_id, name, data)
            frame.Ngrid(row=0, column=0, sticky="nsew")
            self.node_settings[self.now_command_name][node_id] = {"name": name, "data":data, "frame": frame}
    
    def deletion(self, event):
        tree: ttk.Treeview = self.command_trees[self.now_command_name]
        node_ids = tree.selection()
        if not any(node_ids):
            return
        if not messagebox.askyesno("確認", "選択されているすべてのノードを削除しますか?"):
            return
        
        for node_id in  node_ids:
            frame = self.node_settings[self.now_command_name][node_id]["frame"]
            frame.delete_node()
    
    def node_save(self, event):
        tree: ttk.Treeview = self.command_trees[self.now_command_name]
        node_ids = tree.selection()
        if not any(node_ids):
            return
        if not messagebox.askyesno("確認", "選択されているノードの変更をすべて保存しますか?"):
            return
        
        for node_id in  node_ids:
            frame = self.node_settings[self.now_command_name][node_id]["frame"]
            frame.change_node()

class BottomLeftFrame(ttk.Frame):
    def __init__(self, master: WorkFrame = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.con = master
        self.command_frame = self.con.right_command_frame
        
        self.varpre_frames = {}
        
        self.frames = {}
        self.frames["Empty"] = ttk.Frame(master=self, style="MYStyle.TFrame")
        self.frames["Node"] = AddNodeFrame(master=self, command_frame=self.command_frame)
        self.frames["Command"] = AddCommandFrame(master=self, command_frame=self.command_frame)
        self.frames["Detail"] = DetailedPreference(master=self, con=self.con)
        self.frames["Variable"] = AddVariableFrame(master=self, con=self.con)
        
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("Empty")
        
    def set_node_frame(self):
        for command_name, node_settings in self.command_frame.node_settings.items():
            for node_id, datas in node_settings.items():
                name = datas["name"]
                data = datas["data"]
                frame = self.create_node_frame(command_name, node_id, name, data)
                frame.Ngrid(row=0, column=0, sticky="nsew")
                self.command_frame.node_settings[command_name][node_id] = {"name": name, "data": data, "frame": frame}
    
    def create_node_frame(self, command_name, node_id, node_name, data):
        if node_name == "ログ表示":
            return nodede.PrintFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name == "メッセージを送る":
            return nodede.SendMessageFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name == "変数の設定":
            return nodede.VarFrame(self, self.command_frame, command_name, node_id, data)
    
    def create_copre_frame(self):
        for command_name in self.command_frame.command_trees.keys():
            self.command_frame.command_setting_frames[command_name] = CommandDetailFrame(self, self.command_frame, command_name)
            
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
    
    def show_varpre_frame(self, name):
        variables = self.con.top_left_frame.variables
        frame = variables[name]["frame"]
        frame.tkraise()
    
    def show_copre_frame(self, name):
        frame = self.command_frame.command_trees[name]["frame"]
        frame.tkraise()
        
class AddNodeFrame(ttk.Frame):
    def __init__(self, master: BottomLeftFrame = None, command_frame: RightCommandFrame = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.bottom = master
        self.command_frame = command_frame
        
        with open("node.json", "r", encoding="utf-8") as j:
            self.nodes = json.load(j)
        
        self.node_tree = ttk.Treeview(self, height=15)
        self.node_tree.column("#0", width=200)
        self.node_tree.heading("#0", text="ノードの追加")
        
        for group_name, group in self.nodes.items():
            child = self.node_tree.insert(parent="",index='end',text=group_name)
            for node in group:
                self.node_tree.insert(parent=child,index='end',text=node)
        
        self.node_tree.bind("<<TreeviewSelect>>", self.select_node_tree)
        self.node_tree.pack(fill="both")
    
    def select_node_tree(self, event):
        item = self.node_tree.focus()
        item_name = self.node_tree.item(item, "text")
        item_parent = self.node_tree.parent(item)
        
        if not item_parent:
            return
        if not messagebox.askyesno(title="追加の確認", message=f"{item_name}を追加しますか?"):
            return
        
        command_name = self.command_frame.now_command_name
        tree = self.command_frame.command_trees[command_name]
        node_id = tree.insert(parent="", index="end", text=item_name)
        
        frame = self.bottom.create_node_frame(command_name, node_id, item_name, [])
        frame.Ngrid(row=0, column=0, sticky="nsew")
        self.command_frame.node_settings[command_name][node_id] = {"name": item_name, "data": frame.data, "frame": frame}
        

class CommandSettingFrame(ttk.Frame):
    def __init__(self, master = None, command_frame: RightCommandFrame = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.command_frame = command_frame
        
        
        self.name_lab = ttk.Label(self, text="名前", style="MYStyle.TLabel")
        self.name_ent = ttk.Entry(self)
        
        self.name_lab.grid(row=0, column=0)
        self.name_ent.grid(row=0, column=1)

class CommandDetailFrame(CommandSettingFrame):
    def __init__(self, master = None, command_frame = None, command_name = None):
        super().__init__(master, command_frame, command_name)
    
        self.command_name = command_name
        
        self.add_btn = ttk.Button(self, text="変更", command=self.change_command, style="Green.TButton")
        self.add_btn.grid(row=1, column=1)
    
    def delete_command(self):
        pass
    
    def change_command(self):
        name = self.name_ent.get()
        command_trees = self.command_frame.command_trees
        names = [command_name for command_name in command_trees]
        
        if not name:
            messagebox.showerror('エラー', '空欄を埋めてください')
            return
        if name in names and self.command_name != name:
            messagebox.showerror('エラー', 'すでに同じ名前のコマンドがあります')
            return
        
        
class AddCommandFrame(CommandSettingFrame):
    def __init__(self, master = None, command_frame: RightCommandFrame = None):
        super().__init__(master, command_frame)
        
        self.add_btn = ttk.Button(self, text="追加", command=self.add_command, style="Green.TButton")
        self.add_btn.grid(row=1, column=1)
        
        
    def add_command(self):
        name = self.name_ent.get()
        command_trees = self.command_frame.command_trees
        names = [command_name for command_name in command_trees]
        
        if not name:
            messagebox.showerror('エラー', '空欄を埋めてください')
            return
        if name in names:
            messagebox.showerror('エラー', 'すでに同じ名前のコマンドがあります')
            return
        
        frame = ttk.Frame(self.command_frame.command_note)
        tree = ttk.Treeview(frame, height=30)
        tree.column("#0", width=500)
        tree.heading("#0", text=name)
        tree.bind("<<TreeviewSelect>>", self.command_frame.select_node)
        tree.pack(fill="x")
        self.command_frame.command_trees[name]= tree
        self.command_frame.command_note.add(frame, text=name)
        self.command_frame.node_settings[name] = {}

class DetailedPreference(ttk.Frame):
    def __init__(self, master: WorkFrame = None, con: WorkFrame = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.con = con
        
        self.name_lab = ttk.Label(self, text="名前", style="MYStyle.TLabel")
        self.name_ent = ttk.Entry(self, width=80)
        self.token_lab = ttk.Label(self, text="TOKEN", style="MYStyle.TLabel")
        self.token_ent = ttk.Entry(self, width=80)
        self.prefix_lab = ttk.Label(self, text="PREFIX", style="MYStyle.TLabel")
        self.prefix_ent = ttk.Entry(self, width=80)
        self.change_btn = ttk.Button(self, text="変更", command=self.change_detail, style="Green.TButton")
        
        self.name_ent.insert(0, self.con.file_name)
        self.token_ent.insert(0, self.con.token)
        self.prefix_ent.insert(0, self.con.prefix)
        
        self.name_lab.grid(row=0, column=0)
        self.name_ent.grid(row=0, column=1)
        self.token_lab.grid(row=1, column=0)
        self.token_ent.grid(row=1, column=1)
        self.prefix_lab.grid(row=2, column=0)
        self.prefix_ent.grid(row=2, column=1)
        self.change_btn.grid(row=3, column=1)
        
    
    def change_detail(self):
        file_names = os.listdir(".\data")
        file_name = self.name_ent.get()
        token = self.token_ent.get()
        prefix = self.prefix_ent.get()
        
        if not all((file_name, token, prefix)):
            messagebox.showerror('エラー', '空欄があります')
            return
        if file_name+".json" in file_names and file_name != self.con.file_name:
            messagebox.showerror('エラー', '同じ名前のファイルがあります')
            return
        if not messagebox.askyesno(title="変更の確認", message=f"詳細を変更しますか?"):
            return
            
        self.con.file["token"] = token
        self.con.file["prefix"] = prefix
        
        with open(f".\data\{self.con.file_name}.json", "w", encoding='utf-8') as f:
            json.dump(self.con.file, f, ensure_ascii=False, indent=4)
        
        if file_name != self.con.file_name:   
            os.rename(f"./data/{self.con.file_name}.json", f"./data/{file_name}.json")
        
        self.con.file_name = file_name
        self.con.token = token
        self.con.prefix = prefix
        
        
        
        
    
        
        
        