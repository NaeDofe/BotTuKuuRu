import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class WorkFrame(tk.Frame):
    
    def __init__(self, master = None, file = None, file_name = "") -> None:
        super().__init__(master)
        
        self.file = file
        
        self.file_name = file_name
        self.token = file["token"]
        self.prefix = file["prefix"]
        
        #作る
        self.right_command_frame = RightCommandFrame(master=self, file=self.file)
        
        self.bottom_left_frame = BottomLeftFrame(master=self)
        self.top_left_frame = TopLeftFrame(master=self)
        
        #配置する
        self.top_left_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.bottom_left_frame.grid(row=1, column=0,sticky=tk.NSEW)
        
        self.right_command_frame.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
class TopLeftFrame(tk.Frame):
    def __init__(self, master: WorkFrame = None):
        super().__init__(master)
        
        self.con = master
        self.bottom = self.con.bottom_left_frame
        
        self.execution_btn = ttk.Button(self, text="実行", command=self.execution)
        self.save_btn = ttk.Button(self, text="保存", command=self.save)
        self.detail_btn = ttk.Button(self, text="詳細設定", command=lambda: self.bottom.show_frame("Detail"))
        self.node_add_btn = ttk.Button(self, text="ノード追加", command=lambda: self.bottom.show_frame("Node"))
        self.var_add_btn = ttk.Button(self, text="変数追加", command=self.var_add)
        self.command_add_btn = ttk.Button(self, text="コマンド追加", command=lambda: self.bottom.show_frame("Command"))
        self.mode_lbl = ttk.Label(self, text="モード  :")
        self.change_mode_lbl = ttk.Label(self, text="選択")
        self.selection_btn = ttk.Button(self, text="選択", command=self.selection)
        self.selection_node = ttk.Label(self, text="ノード:")
        self.selection_node_lbl = ttk.Label(self, text="")
        self.move_btn = ttk.Button(self, text="移動", command=self.move)
        self.child_btn = ttk.Button(self, text="子供", command=self.child)
        
        self.execution_btn.grid(row=0, column=0)
        self.save_btn.grid(row=0, column=1)
        self.detail_btn.grid(row=0, column=2)
        self.node_add_btn.grid(row=1, column=0)
        self.var_add_btn.grid(row=1, column=2)
        self.command_add_btn.grid(row=1, column=1)
        self.mode_lbl.grid(row=2, column=0)
        self.change_mode_lbl.grid(row=2, column=1)
        self.selection_btn.grid(row=3, column=0)
        self.selection_node.grid(row=3, column=1)
        self.selection_node_lbl.grid(row=3, column=2)
        self.move_btn.grid(row=4, column=0)
        self.child_btn.grid(row=5, column=0)
        
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
        
        self.var_dic = {}
        for name, vals in self.con.file["vars"].items():
            var_lis = [vals[0], name, vals[1]]
            self.var_tree.insert(parent='', index='end', values=var_lis)
            self.var_dic[var_lis[1]] = [var_lis[0],var_lis[2]]
        self.var_tree.bind("<<TreeviewSelect>>", self.select_var_tree)
        self.var_tree.grid(row=0, column=4, rowspan=6)
        
    def select_var_tree(self, evvent):
        pass
    
    def execution(self):
        pass
    
    def save(self):
        pass

    def var_add(self):
        pass
    
    def selection(self):
        pass
    
    def move(self):
        pass
    
    def child(self):
        pass


class RightCommandFrame(tk.Frame):
    def __init__(self, master = None, file = None):
        super().__init__(master)
        
        self.file = file
        self.node_settings = {}
        self.command_trees = []
        self.tab_index = 0
        
        self.command_note = ttk.Notebook(self)
        self.command_note.bind("<<NotebookTabChanged>>", self.tab_changed)
        self.command_note.bind("<ButtonRelease-1>", self.tab_click)
        
        for command_name, data_dic in file["commands"].items():
            command_tree = ttk.Treeview(self.command_note, height=30)
            command_tree.column("#0", width=500)
            command_tree.heading("#0", text=command_name)
            self.file_to_tree(command_tree, "", data_dic)
            command_tree.bind("<<TreeviewSelect>>", self.select_node)
            command_tree.pack(fill="x")
            self.command_trees.append(command_tree)
            self.command_note.add(command_tree, text=command_name)
        
        self.command_note.pack(fill="both", side="right")
        
    def file_to_tree(self, tree, parent, data_dic):
        for val in data_dic.values():
            
            child = tree.insert(parent=parent, index="end", text=val[0])
            
            self.node_settings[child] = val[2]
            
            if not any(val[1]):
                self.file_to_tree(tree, child, val[1])
    
    def select_node(self, event):
        pass
        
    def tab_changed(self, event):
        select_id = self.command_note.select() 
        if select_id == "":
            return
        self.tab_index = self.command_note.index(select_id)
    
    def tab_click(self, event):
        pass    
    

class BottomLeftFrame(tk.Frame):
    def __init__(self, master: WorkFrame = None):
        super().__init__(master)
        
        self.con = master
        self.command_frame = self.con.right_command_frame
        
        self.frames = {}
        self.frames["Empty"] = tk.Frame(master=self)
        self.frames["Node"] = AddNodeFrame(master=self, command_frame=self.command_frame)
        self.frames["Command"] = AddCommandFrame(master=self, command_frame=self.command_frame)
        self.frames["Detail"] = DetailedPreference(master=self, con=self.con)
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("Empty")
        
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        pass
        

class AddNodeFrame(tk.Frame):
    def __init__(self, master = None, command_frame: RightCommandFrame = None):
        super().__init__(master)
        
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
        
        if item_parent == "":
            return
        if not messagebox.askyesno(title="追加の確認", message=f"{item_name}を追加しますか?"):
            return
        
        #コマンドツリーにアイテムを追加する
        tab_index = self.command_frame.tab_index
        tree = self.command_frame.command_trees[tab_index]
        tree.insert(parent="", index="end", text=item_name)

class AddCommandFrame(tk.Frame):
    def __init__(self, master = None, command_frame: RightCommandFrame = None):
        super().__init__(master)
        
        self.command_frame = command_frame
        
        self.name_lab = ttk.Label(self, text="名前")
        self.name_ent = ttk.Entry(self)
        self.add_btn = ttk.Button(self, text="追加", command=self.add_command)
        
        self.name_lab.grid(row=0, column=0)
        self.name_ent.grid(row=0, column=1)
        self.add_btn.grid(row=1, column=1)
        
        
    def add_command(self):
        name = self.name_ent.get()
        command_trees = self.command_frame.command_trees
        names = [tree.heading("#0", "text") for tree in command_trees]
        if name == "":
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
        self.command_frame.command_trees.append(tree)
        self.command_frame.command_note.add(frame, text=name)

class DetailedPreference(tk.Frame):
    def __init__(self, master: WorkFrame = None, con: WorkFrame = None):
        super().__init__(master)
        
        self.con = con
        
        self.name_lab = ttk.Label(self, text="名前")
        self.name_ent = ttk.Entry(self, width=80)
        self.token_lab = ttk.Label(self, text="TOKEN")
        self.token_ent = ttk.Entry(self, width=80)
        self.prefix_lab = ttk.Label(self, text="PREFIX")
        self.prefix_ent = ttk.Entry(self, width=80)
        self.change_btn = ttk.Button(self, text="変更", command=self.change_detail)
        
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
        
        if file_name == "" or token == "" or prefix == "":
            messagebox.showerror('エラー', '空欄があります')
            return
        if file_name+".json" in file_names:
            messagebox.showerror('エラー', '同じ名前のファイルがあります')
            return
        if not messagebox.askyesno(title="変更の確認", message=f"詳細を変更しますか?"):
            return
        
        with open(f"./data/{self.con.file_name}.json", "r", encoding='utf-8') as j:
            file = json.load(j)
            
        file["token"] = token
        file["prefix"] = prefix
        
        with open(f".\data\{self.con.file_name}.json", "w", encoding='utf-8') as f:
            json.dump(file, f, ensure_ascii=False, indent=4)
                
        os.rename(f"./data/{self.con.file_name}.json", f"./data/{file_name}.json")
        
        self.con.file_name = file_name
        self.con.token = token
        self.con.prefix = prefix
        
        
        
        
    
        
        
        