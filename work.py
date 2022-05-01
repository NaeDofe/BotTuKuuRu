from tkinter import ttk, messagebox
import tkinter as tk
import json
import os
import tc

class WorkFrame(tk.Frame):
    
    def __init__(self, master = None, file = None, file_name = "") -> None:
        super().__init__(master)
        
        self.file = file
        
        self.file_name = file_name
        self.token = file["token"]
        self.prefix = file["prefix"]
        
        self.right_command_frame = RightCommandFrame(master=self, file=self.file)
        
        self.bottom_left_frame = BottomLeftFrame(master=self)
        self.top_left_frame = TopLeftFrame(master=self)
        
        self.right_command_frame.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)
        
        self.top_left_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.bottom_left_frame.grid(row=1, column=0,sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
class TopLeftFrame(tk.Frame):
    def __init__(self, master: WorkFrame = None):
        super().__init__(master)
        
        self.con = master
        self.command = self.con.right_command_frame
        self.bottom = self.con.bottom_left_frame
        
        self.mode = 0
        self.selected_var_id = ""
        
        self.execution_btn = ttk.Button(self, text="実行", command=self.execution)
        self.save_btn = ttk.Button(self, text="保存", command=self.save)
        self.detail_btn = ttk.Button(self, text="詳細設定", command=lambda: self.bottom.show_frame("Detail"))
        self.node_add_btn = ttk.Button(self, text="ノード追加", command=lambda: self.bottom.show_frame("Node"))
        self.var_add_btn = ttk.Button(self, text="変数追加", command=lambda: self.bottom.show_frame("Variable"))
        self.command_add_btn = ttk.Button(self, text="コマンド追加", command=lambda: self.bottom.show_frame("Command"))
        self.mode_lbl = ttk.Label(self, text="モード： 選択")
        self.selection_btn = ttk.Button(self, text="選択", command=self.selection)
        self.selection_node_lbl = ttk.Label(self, text="ノード： ")
        self.move_btn = ttk.Button(self, text="移動", command=self.move)
        self.child_btn = ttk.Button(self, text="子供", command=self.child)
        
        self.execution_btn.grid(row=0, column=0)
        self.save_btn.grid(row=0, column=1)
        self.detail_btn.grid(row=0, column=2)
        self.node_add_btn.grid(row=1, column=0)
        self.var_add_btn.grid(row=1, column=2)
        self.command_add_btn.grid(row=1, column=1)
        self.mode_lbl.grid(row=2, column=0, columnspan=2)
        self.selection_btn.grid(row=3, column=0)
        self.selection_node_lbl.grid(row=3, column=1, columnspan=2)
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
        pass
    
    def save(self):
        pass
    
    def selection(self):
        self.mode = 0
        self.command.selected_id = ""
        self.selection_node_lbl["text"] = "ノード： "
        self.mode_lbl["text"] = "モード： 選択"
    
    def move(self):
        self.mode = 1
        self.command.selected_id = ""
        self.selection_node_lbl["text"] = "ノード： "
        self.mode_lbl["text"] = "モード： 移動"
    
    def child(self):
        self.mode = 2
        self.command.selected_id = ""
        self.selection_node_lbl["text"] = "ノード： "
        self.mode_lbl["text"] = "モード： 子供"


class RightCommandFrame(tk.Frame):
    def __init__(self, master: WorkFrame = None, file = None):
        super().__init__(master)
        
        self.con = master
        self.file = file
        
        self.node_settings = {}
        self.command_trees = []
        self.tab_index = 0
        self.selected_id = ""
        
        self.command_note = ttk.Notebook(self)
        self.command_note.bind("<<NotebookTabChanged>>", self.tab_changed)
        self.command_note.bind("<ButtonRelease-1>", self.tab_click)
        self._file_to_commad()
        self.command_note.pack(fill="both", side="right")
    
    def _file_to_commad(self):
        for command_name, data_dic in self.file["commands"].items():
            command_tree = ttk.Treeview(self.command_note, height=30)
            command_tree.column("#0", width=500)
            command_tree.heading("#0", text=command_name)
            self._file_to_tree(command_tree, "", data_dic)
            command_tree.bind("<<TreeviewSelect>>", self.select_node)
            command_tree.pack(fill="x")
            self.command_trees.append(command_tree)
            self.command_note.add(command_tree, text=command_name)
        
    def _file_to_tree(self, tree, parent, data_dic):
        for val in data_dic.values():
            
            child = tree.insert(parent=parent, index="end", text=val[0])
            self.node_settings[child] = val[2]
            
            if not any(val[1]):
                self._file_to_tree(tree, child, val[1])
    
    def select_node(self, event):
        tree = self.command_trees[self.tab_index]
        item_id = tree.focus()
        item_name = tree.item(item_id, "text")
        item_parent = tree.parent(item_id)
        
        mode = self.con.top_left_frame.mode
        node_lab = self.con.top_left_frame.selection_node_lbl
        
        if mode == 0:
            node_lab["text"] = "ノード: "+item_name
            if self.selected_id == item_id:
                return
            self.selected_id = item_id
            #ノードの詳細を表示する処理を描く↓
            return
            
        if not self.can_move(tree, item_id, item_parent):
            messagebox.showerror("Error", "その移動は不可能です")
            self.selected_id = ""
            node_lab["text"] = "ノード： "
            return
        
        if self.selected_id == "":
            self.selected_id = item_id
            node_lab["text"] = "ノード： "+item_name
            return
        
        if mode == 1:
            index = tree.index(item_id)
            tree.move(self.selected_id, item_parent, index)
            self.selected_id = ""
            node_lab["text"] = "ノード： "
            
        if mode == 2:
            if self.selected_id != item_id:
                tree.move(self.selected_id, item_id, "end")
            self.selected_id = ""
            node_lab["text"] = "ノード： "
    
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
        self.tab_index = self.command_note.index(select_id)
    
    def tab_click(self, event):
        pass    
    

class BottomLeftFrame(tk.Frame):
    def __init__(self, master: WorkFrame = None):
        super().__init__(master)
        
        self.con = master
        self.command_frame = self.con.right_command_frame
        
        self.varpre_frames = {}
        
        self.frames = {}
        self.frames["Empty"] = tk.Frame(master=self)
        self.frames["Node"] = AddNodeFrame(master=self, command_frame=self.command_frame)
        self.frames["Command"] = AddCommandFrame(master=self, command_frame=self.command_frame)
        self.frames["Detail"] = DetailedPreference(master=self, con=self.con)
        self.frames["Variable"] = AddVariableFrame(master=self, con=self.con)
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("Empty")
        
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
    
    def show_varpre_frame(self, name):
        variables = self.con.top_left_frame.variables
        frame = variables[name]["frame"]
        frame.tkraise()
    
    
class VariableDetailFrame(tk.Frame):
    def __init__(self, master = None, top: TopLeftFrame = None, var_name = "", var_type = "", var_default = ""):
        super().__init__(master)
        
        self.top = top
        
        self.frame_name = ttk.Label(self, text="変数の詳細設定")
        self.name_lab = ttk.Label(self, text="名前")
        self.name_ent = ttk.Entry(self, width=40)
        self.type_lab = ttk.Label(self, text="型")
        self.type_com = ttk.Combobox(self, width=40, values=["str","int","float","bool","list","dict","None"])
        self.default_lab = ttk.Label(self, text="初期値")
        self.default_ent = ttk.Entry(self, width=40)
        self.change_btn = ttk.Button(self, text="変更", command=self.change_var)
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_var)
        
        self.name_ent.insert(0, var_name)
        self.type_com.insert(0, var_type)
        self.default_ent.insert(0, var_default)
        
        self.frame_name.grid(row=0, column=1)
        self.name_lab.grid(row=1, column=0)
        self.name_ent.grid(row=1, column=1)
        self.type_lab.grid(row=2, column=0)
        self.type_com.grid(row=2, column=1)
        self.default_lab.grid(row=3, column=0)
        self.default_ent.grid(row=3, column=1)
        self.change_btn.grid(row=4, column=1)
        self.delete_btn.grid(row=5, column=1)
    
    def change_var(self):
        var_name = self.name_ent.get()
        var_type = self.type_com.get()
        var_default = self.default_ent.get()
        
        var_tree = self.top.var_tree
        variables = self.top.variables
        select_id = self.top.selected_var_id
        original_name = var_tree.item(select_id, "values")[1]
        
        
        if not all([var_name, var_type, var_default]):
            messagebox.showerror('エラー', '空欄を埋めてください')
            return
        if var_name in variables and var_name != original_name:
            messagebox.showerror('エラー', 'すでに同じ名前の変数があります')
            return
        if not tc.type_check(var_type, var_default):
            messagebox.showerror('エラー', '型と値が合いません')
            return
        if not messagebox.askquestion("確認", "変数を変更しますか？"):
            return
        
        index = var_tree.index(select_id)
        
        variables.pop(original_name)
        var_tree.delete(self.top.selected_var_id)
        
        variables[var_name] = {"type": var_type, "val": var_default, "frame": self}
        var_tree.insert(parent="", index=index, values=(var_type, var_name, var_default,))
        
        self.top.variables = variables
    
    def delete_var(self):
        if not messagebox.askquestion("確認", "変数を削除しますか？"):
            return
        
        var_tree = self.top.var_tree
        select_id = self.top.selected_var_id
        delete_name = var_tree.item(select_id, "values")[1]
        
        var_tree.delete(select_id)
        self.top.variables.pop(delete_name)
        self.top.selected_var_id = ""
        
        self.destroy()

class AddVariableFrame(tk.Frame):
    def __init__(self, master = None, con: WorkFrame = None):
        super().__init__(master)
        
        self.con = con
        
        self.frame_name = ttk.Label(self, text="変数の追加")
        self.name_lab = ttk.Label(self, text="名前")
        self.name_ent = ttk.Entry(self, width=40)
        self.type_lab = ttk.Label(self, text="型")
        self.type_com = ttk.Combobox(self, width=40, values=["str","int","float","bool","list","dict","None"])
        self.default_lab = ttk.Label(self, text="初期値")
        self.default_ent = ttk.Entry(self, width=40)
        self.add_btn = ttk.Button(self, text="追加", command=self.append_var_tree)
        
        self.frame_name.grid(row=0, column=1)
        self.name_lab.grid(row=1, column=0)
        self.name_ent.grid(row=1, column=1)
        self.type_lab.grid(row=2, column=0)
        self.type_com.grid(row=2, column=1)
        self.default_lab.grid(row=3, column=0)
        self.default_ent.grid(row=3, column=1)
        self.add_btn.grid(row=4, column=1)

    
    def append_var_tree(self):
        var_tree = self.con.top_left_frame.var_tree
        variables = self.con.top_left_frame.variables
        
        var_name = self.name_ent.get()
        var_type = self.type_com.get()
        var_default = self.default_ent.get()
        
        if not all([var_name, var_type, var_default]):
            messagebox.showerror('エラー', '空欄を埋めてください')
            return
        if var_name in variables:
            messagebox.showerror('エラー', 'すでに同じ名前の変数があります')
            return
        if not tc.type_check(var_type, var_default):
            messagebox.showerror('エラー', '型と値が合いません')
            return
        if not messagebox.askquestion("確認", "変数を追加しますか？"):
            return
        
        frame = VariableDetailFrame(
            master=self.con.bottom_left_frame, 
            top=self.con.top_left_frame, 
            var_name=var_name, 
            var_type=var_type, 
            var_default=var_default)
        frame.grid(row=0, column=0, sticky="nsew")
        
        variables[var_name] = {"type": var_type, "val": var_default, "frame": frame}
        self.con.top_left_frame.variables = variables
        
        var_tree.insert(parent="", index="end", values=(var_type, var_name, var_default,))
        
        
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
        
        if not item_parent:
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
        
        
        
        
    
        
        
        