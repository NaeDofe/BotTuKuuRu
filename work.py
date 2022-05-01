import tkinter as tk
from tkinter import ttk, messagebox
import json

class WorkFrame(tk.Frame):
    
    def __init__(self, master = None, file = None) -> None:
        super().__init__(master)
        
        self.file = file 
        
        self.left_empty_frame = ttk.Frame(self)
        self.right_empty_frame = ttk.Frame(self)
        
        self.bottom_left_frame = BottomLeftFrame(master=self.left_empty_frame)
        self.top_left_frame = TopLeftFrame(master=self.left_empty_frame, con=self, bottom=self.bottom_left_frame)
       
        self.right_command_frame = RightCommandFrame(master=self.right_empty_frame, file=self.file)
        
        self.left_empty_frame.pack(side = tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_empty_frame.pack(side = tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.top_left_frame.pack(fill=tk.BOTH, expand=True)
        self.bottom_left_frame.pack(fill=tk.BOTH, expand=True)
        
        self.right_command_frame.pack(fill=tk.BOTH, side=tk.RIGHT)
        
        
class TopLeftFrame(tk.Frame):
    def __init__(self, master = None, con = None, bottom = None):
        super().__init__(master)
        
        self.con = con
        self.bottom = bottom
        
        self.execution_btn = ttk.Button(self, text="実行", command=self.execution)
        self.save_btn = ttk.Button(self, text="保存", command=self.save)
        self.detail_btn = ttk.Button(self, text="詳細設定", command=self.detail)
        self.node_add_btn = ttk.Button(self, text="ノード追加", command=lambda: self.bottom.show_frame("Node"))
        self.var_add_btn = ttk.Button(self, text="変数追加", command=self.var_add)
        self.command_add_btn = ttk.Button(self, text="コマンド追加", command=self.command_add)
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
    
    def detail(self):
        pass

    def var_add(self):
        pass
    
    def command_add(self):
        pass
    
    def selection(self):
        pass
    
    def move(self):
        pass
    
    def child(self):
        pass
    
    

#左下
class BottomLeftFrame(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        
        self.frames = {}
        self.frames["Empty"] = ttk.Frame(master=self)
        self.frames["Node"] = NodeFrame(master=self)
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("Empty")
        
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        pass
        
        

class RightCommandFrame(tk.Frame):
    def __init__(self, master = None, file = None):
        super().__init__(master)
        
        self.file = file
        self.node_settings = {}
        self.command_trees = []
        
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
        pass
    
    def tab_click(self, event):
        pass
        
        
        
        
class NodeFrame(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        
        with open("node.json", "r", encoding="utf-8") as j:
            self.nodes = json.load(j)
        
        self.node_tree = ttk.Treeview(self, height=15)
        
        for i in self.nodes:
            child = self.node_tree.insert(parent="",index='end',text=i)
            for j in self.nodes[i]:
                self.node_tree.insert(parent=child,index='end',text=j)
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
    
        
        
        