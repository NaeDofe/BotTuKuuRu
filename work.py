from tkinter import ttk, messagebox
from varset import AddVariableFrame, VariableDetailFrame
from nodes import branch, variable
import tkinter as tk
import json
import nodede
import os
import threading
import subprocess
import yaml
import copy

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
        
        #VarFrameでtop_left_frameを使うから
        self.bottom_left_frame.initial_setting_node_frame()
        
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
        
        self.var_note = ttk.Notebook(self)
        
        self.var_tree = self._create_var_tree(self.var_note, "global")
        
        self.global_var = {}
        self._var_file_to_tree()
        self.var_tree.bind("<<TreeviewSelect>>", self.select_var_tree_item)
        self.var_tree.pack()
        self.var_note.add(self.var_tree, text="global")
        
        self._vars_to_tree_local()
        
        self.var_note.grid(row=0, column=4, rowspan=6)
        
        
        self.bottom.show_frame("Empty")
    
    def _create_var_tree(self, master, name):
        tree = ttk.Treeview(master)
        tree['columns'] = ('ID','Name','Score')
        tree.column('#0',width=0, stretch='no')
        tree.column('ID', anchor='center', width=60)
        tree.column('Name',anchor='w', width=100)
        tree.column('Score', anchor='center', width=80)
            
        tree.heading('#0',text=name)
        tree.heading('ID', text='型',anchor='center')
        tree.heading('Name', text='名前', anchor='w')
        tree.heading('Score',text='初期値', anchor='center')
        return tree
    
    def _var_file_to_tree(self):
        for name, vals in self.con.file["vars"].items():
            self.var_tree.insert(parent='', index='end', values=(vals[0], name, vals[1]))
            frame = VariableDetailFrame(master=self.bottom, top=self, var_name=name, var_type=vals[0], var_default=vals[1])
            frame.grid(row=0, column=0, sticky="nsew")
            self.global_var[name] = {"type":vals[0], "val":vals[1], "frame": frame}
    
    def _vars_to_tree_local(self):
        for command_name, data_dic in self.con.file["commands"].items():
            vars = data_dic["vars"]
            self.set_local_vars(vars, command_name)
            
    def set_local_vars(self, vars, command_name):
        tree = self._create_var_tree(self.var_note, command_name)
        self.command.commands[command_name]["var_tree"] = tree
        for name, vals in vars.items():
            tree.insert(parent='', index='end', values=(vals[0], name, vals[1]))
            frame = VariableDetailFrame(master=self.bottom, top=self, var_name=name, var_type=vals[0], var_default=vals[1], par_name=command_name)
            frame.grid(row=0, column=0, sticky="nsew")
            self.command.commands[command_name]["vars"][name] = {"type":vals[0], "val":vals[1], "frame": frame}
        tree.bind("<<TreeviewSelect>>",self.select_var_tree_item)
        tree.pack()
        self.var_note.add(tree, text="local: "+ command_name)
    
    
    def select_var_tree_item(self, event):
        tree = event.widget
        self.selected_var_id = tree.focus()
        name = tree.item(self.selected_var_id, "values")[1]
        command_name = tree.heading("#0", "text")
        self.bottom.show_varpre_frame(name, command_name)
        
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
        subprocess.call('start /wait py bot.py', shell=True)
        self.bot_is_run = False
    
    def save(self, conf = True):
        #確認がいらない場合があるから
        if conf:
            if not messagebox.askyesno("確認", "ファイルを保存しますか?"):
                return False
        
        commands = self.command.commands
        
        command_dic = {}
        for command_name, command_data in commands.items():
            command_tree = command_data["tree"]
            command_dic[command_name] = {"nodes": self._tree_to_dict(command_tree, "", command_name)}
            command_dic[command_name]["vars"] = self._variables_to_file_data(commands[command_name]["vars"])

        
        self.con.file["commands"] = command_dic
        self.con.file["vars"] = self._variables_to_file_data(self.global_var)
        self.con.file["token"] = self.con.token
        self.con.file["prefix"] = self.con.prefix
        
        with open(f".\data\{self.con.file_name}.json", "w", encoding='utf-8') as f:
            json.dump(self.con.file, f, ensure_ascii=False, indent=4)
        
        return True
    
    def _tree_to_dict(self, tree, parent, command_name):
        dic = {}
        for item in tree.get_children(parent):
            name = tree.item(item, "text")
            data = self.command.commands[command_name]["nodes"][item]["data"]
            dic[item] = [name, self._tree_to_dict(tree, item, command_name), data ]
        return dic

    def _variables_to_file_data(self, vars):
        dic = {}
        for name, data in vars.items():
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
        
        self.commands = {}
        self.undo_nodes = {}
        self.undo_index = 1
        self.redo_index = 1
        self.copy_nodes = None
        self.selected_id = ""
        self.now_command_name = ""
        
        self.command_note = ttk.Notebook(self)
        self.command_note.bind("<<NotebookTabChanged>>", self.tab_changed)
        self.command_note.bind("<ButtonRelease-1>", self.tab_click)
        
        #ctrl-zを使うとTreeviewが変わって毎回クリックしないといけなくなるからallにしてる
        self.command_note.bind_all("<Control-z>", self.undo)
        self.command_note.bind_all("<Control-Shift-Key-Z>", self.redo)
        
        self._file_to_commad_tree()
        self.command_note.pack(fill="both", side="right")
    
    def _file_to_commad_tree(self):
        for command_name, data_dic in self.file["commands"].items():
            node_deta = data_dic["nodes"]
            
            self.commands[command_name] = {}
            self.undo_nodes[command_name] = []
            tree_frame = ttk.Frame(self.command_note, style="MYStyle.TFrame")
            command_tree = ttk.Treeview(tree_frame, height=100)
            scrollbar = ttk.Scrollbar(tree_frame, orient = tk.VERTICAL, command=command_tree.yview)
            command_tree.configure(yscrollcommand=lambda f, l: scrollbar.set(f, l))
            
            command_tree.column("#0", width=600)
            command_tree.heading("#0", text=command_name)
            command_tree.bind("<<TreeviewSelect>>", self.select_node)
            command_tree.bind("<Control-c>", self.copy)
            command_tree.bind("<Control-v>", self.paste)
            command_tree.bind("<Control-d>", self.deletion)
            command_tree.bind("<Control-s>", self.node_save)
            command_tree.tag_configure("not_save", foreground=self.con.bt.not_save_color)
            self.commands[command_name]["nodes"] = {}
            self._command_file_to_tree(command_tree, "", node_deta, command_name)
            command_tree.pack(fill="both", side="left")
            scrollbar.pack(fill="y", side="left")
            self.commands[command_name]["tree"] = command_tree
            self.commands[command_name]["tree_frame"] = tree_frame
            self.commands[command_name]["scrollbar"] = scrollbar
            self.commands[command_name]["vars"] = {}
            self.commands[command_name]["var_tree"] = {}
            self.command_note.add(tree_frame, text=command_name)
        
    def _command_file_to_tree(self, tree, parent, data_dic, command_name):
        for val in data_dic.values():
            
            node_name = val[0]
            child_data = val[1]
            node_data = val[2]
            
            node_id = tree.insert(parent=parent, index="end", text=node_name)
            tree.item(node_id, open=True)
            self.commands[command_name]["nodes"][node_id] = {"name": node_name, "data": node_data}
            
            if any(child_data):
                self._command_file_to_tree(tree, node_id, child_data, command_name)
    
    
    def show_node_frame(self, node_id):
        frame = self.commands[self.now_command_name]["nodes"][node_id]["frame"]
        frame.tkraise()
    
    def select_node(self, event):
        tree = self.commands[self.now_command_name]["tree"]
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
            
        if not self.can_move(tree, self.selected_id, item_parent):
            messagebox.showerror("Error", "その移動は不可能です")
            self.selected_id = ""
            node_lab["text"] = ""
            return
        
        if self.selected_id == "":
            self.selected_id = item_id
            node_lab["text"] = item_name
            return
        
        if mode == 1:
            self.con.bottom_left_frame.save_command_nodes()
            index = tree.index(item_id)
            tree.move(self.selected_id, item_parent, index)
            self.selected_id = ""
            node_lab["text"] = ""
            
        if mode == 2:
            if self.selected_id != item_id:
                self.con.bottom_left_frame.save_command_nodes()
                tree.move(self.selected_id, item_id, "end")
                tree.item(item_id, open=True)
            self.selected_id = ""
            node_lab["text"] = ""
    
    def can_move(self, tree, item, parent) -> bool:
        while True:
            if parent == "":
                return True
            if parent == item:
                return False
            parent = tree.parent(parent)
        
    def tab_changed(self, event):
        select_id = self.command_note.select() 
        if select_id == "":
            return
        self.now_command_name = self.command_note.tab(select_id, "text")
        
    def tab_click(self, event):
        select_id = self.command_note.select()
        if select_id == "":
            return
        self.now_command_name = self.command_note.tab(select_id, "text")
        self.con.bottom_left_frame.show_command_detail_frame(self.now_command_name)
    
    def copy(self, event):
        tree: ttk.Treeview = self.commands[self.now_command_name]["tree"]
        node_ids = tree.selection()
        if not any(node_ids):
            return
        
        self.copy_nodes = {}
        for node_id in node_ids:
            if node_id in self.copy_nodes.keys():
                continue
            isOpen = True if tree.item(node_id, "open") == 1 else False
            parent = tree.parent(node_id)
            node_setting = self.commands[self.now_command_name]["nodes"][node_id].copy()
            self.copy_nodes[node_id] = {"setting": node_setting, "parent": parent}
            if isOpen:
                continue
            self._copy_node_set_child(tree, node_id)
        
    def _copy_node_set_child(self, tree: ttk.Treeview, parent):
        for node_id in tree.get_children(parent):
            if node_id in self.copy_nodes.keys():
                return
            parent = tree.parent(node_id)
            node_setting = self.commands[self.now_command_name]["nodes"][node_id].copy()
            self.copy_nodes[node_id] = {"setting": node_setting, "parent": parent}
            self._copy_node_set_child(tree, node_id)
        
    
    def paste(self, event):
        if self.copy_nodes is None:
            return
        tree: ttk.Treeview = self.commands[self.now_command_name]["tree"]
        item_ids = tree.selection()
         
        index = "end"
        defa_par = ""
        if any(item_ids):
            defa_par = tree.parent(item_ids[-1])
        new_pars = {}
        
        self.con.bottom_left_frame.save_command_nodes()
        for node_id, data in self.copy_nodes.items():
            node_setting = data["setting"]
            parent = data["parent"]
            if parent not in self.copy_nodes:
                parent = defa_par
            elif parent in new_pars:
                parent = new_pars[parent]
            else:
                parent = defa_par
            
            name = node_setting["name"]
            data = node_setting["data"]
            new_node_id = tree.insert(parent, index, text=name)
            frame = self.con.bottom_left_frame.create_node_frame(self.now_command_name, new_node_id, name, data)
            frame.Ngrid(row=0, column=0, sticky="nsew")
            self.commands[self.now_command_name]["nodes"][new_node_id] = {"name": name, "data":data, "frame": frame}

            new_pars[node_id] = new_node_id
    
    def deletion(self, event):
        tree: ttk.Treeview = self.commands[self.now_command_name]["tree"]
        node_ids = tree.selection()
        if not any(node_ids):
            return
        if not messagebox.askyesno("確認", "選択されているすべてのノードを削除しますか?"):
            return
        
        self.con.bottom_left_frame.save_command_nodes()
        for node_id in  reversed(node_ids):
            frame = self.commands[self.now_command_name]["nodes"][node_id]["frame"]
            frame.delete_node(conf=False)
        
    
    def node_save(self, event):
        tree: ttk.Treeview = self.commands[self.now_command_name]["tree"]
        node_ids = tree.selection()
        if not any(node_ids):
            return
        if not messagebox.askyesno("確認", "選択されているノードの変更をすべて保存しますか?"):
            return
        
        #self.con.bottom_left_frame.save_command_nodes()
        for node_id in  node_ids:
            frame = self.commands[self.now_command_name]["nodes"][node_id]["frame"]
            frame.change_node()
        
         
    def undo(self, event):
        if len(self.undo_nodes[self.now_command_name])>= self.undo_index:
            if self.undo_index == 1:
                self.con.bottom_left_frame.save_command_nodes()
                self.undo_index += 1
            self._node_data_to_tree(self.undo_nodes[self.now_command_name][-self.undo_index])
            self.undo_index += 1
            self.redo_index += 1
            
    def redo(self, event):
        if self.redo_index > 1:
            self.redo_index -= 1
            self.undo_index -= 1
            self._node_data_to_tree(self.undo_nodes[self.now_command_name][-self.redo_index])
            
    def _node_data_to_tree(self, nodes_data):
        command_name = self.now_command_name
        
        self.commands[command_name]["tree"].destroy()
        self.commands[command_name]["scrollbar"].destroy()
        
        for datas in self.commands[command_name]["nodes"].values():
            datas["frame"].destroy()
        
        tree_frame = self.commands[command_name]["tree_frame"]
        
        self.commands[command_name] = {}
        self.commands[command_name]["tree_frame"] = tree_frame
        
        """スクロールバーに帰るがんばれ未来に自分俺はご飯を食べるbye!!
        """
        
        command_tree = ttk.Treeview(tree_frame, height=100)
        scrollbar = ttk.Scrollbar(tree_frame, orient = tk.VERTICAL, command=command_tree.yview)
        command_tree.configure(yscrollcommand=lambda f, l: scrollbar.set(f, l))
        command_tree.column("#0", width=600)
        command_tree.heading("#0", text=command_name)
        self.commands[command_name]["nodes"] = {}
        self._command_file_to_tree(command_tree, "", nodes_data, command_name)
        command_tree.bind("<<TreeviewSelect>>", self.select_node)
        command_tree.bind("<Control-c>", self.copy)
        command_tree.bind("<Control-v>", self.paste)
        command_tree.bind("<Control-d>", self.deletion)
        command_tree.bind("<Control-s>", self.node_save)
        command_tree.tag_configure("not_save", foreground=self.con.bt.not_save_color)
        command_tree.pack(fill="both", side="left")
        scrollbar.pack(fill="y", side="left")
        self.commands[command_name]["tree"] = command_tree
        self.commands[command_name]["scrollbar"] = scrollbar
        
        
        self.con.bottom_left_frame.initial_setting_node_frame()
        
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
        
        self.create_command_detail_frame()
        
    def initial_setting_node_frame(self):
        for command_name, command_data in self.command_frame.commands.items():
            node_settings = command_data["nodes"]
            for node_id, datas in node_settings.items():
                name = datas["name"]
                data = datas["data"]
                frame = self.create_node_frame(command_name, node_id, name, data)
                frame.Ngrid(row=0, column=0, sticky="nsew")
                self.command_frame.commands[command_name]["nodes"][node_id] = {"name": name, "data": data, "frame": frame}
    
    def create_node_frame(self, command_name, node_id, node_name, data):
        if node_name == "ログ表示":
            return nodede.PrintFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name == "メッセージを送る":
            return nodede.SendMessageFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name == "変数の設定":
            return variable.VarFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name in ("条件分岐", "Else If", "条件を満たす限り繰り返す"):
            return branch.BranchFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name in ("Else", "Break", "Continue"):
            return nodede.EmptyFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name == "一定回数繰り返す":
            return nodede.ForFrame(self, self.command_frame, command_name, node_id, data)
        elif node_name == "メッセージを削除":
            return nodede.ClearMessageFrame(self, self.command_frame, command_name, node_id, data)
    def create_command_detail_frame(self):
        for command_name in self.command_frame.commands.keys():
            self.command_frame.commands[command_name]["frame"] = CommandDetailFrame(self, self.command_frame, command_name)
            self.command_frame.commands[command_name]["frame"].grid(row=0, column=0, sticky="nsew")
            
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
    
    def show_varpre_frame(self, name, command_name = "global"):
        global_var = self.con.top_left_frame.global_var
        if command_name == "global":
            variables = global_var
        else:
            local_var = self.command_frame.commands[command_name]["vars"]
            variables = {**global_var, **local_var}
        frame = variables[name]["frame"]
        frame.tkraise()
    
    def show_command_detail_frame(self, name):
        if "frame" not in self.command_frame.commands[name]:
            return
        frame = self.command_frame.commands[name]["frame"]
        frame.tkraise()
    
    def save_command_nodes(self):
        command_name = self.command_frame.now_command_name
        MAX_UNDO = 30
        nodes_detas = {}
        for node_id, node_datas in self.command_frame.commands[command_name]["nodes"].items():
            nodes_detas[node_id] = {"data": copy.deepcopy(node_datas["data"]), "name": copy.deepcopy(node_datas["name"])}
        tree = self.command_frame.commands[command_name]["tree"]
        nodes_detas = self._node_data_to_dict(tree, "", nodes_detas)
        if self.command_frame.undo_index > 1:
            del self.command_frame.undo_nodes[command_name][-(self.command_frame.undo_index-1):]
        self.command_frame.undo_nodes[command_name].append(nodes_detas)
        if len(self.command_frame.undo_nodes[command_name]) > MAX_UNDO:
            self.command_frame.undo_nodes[command_name].pop(0)
        self.command_frame.undo_index = 1
        self.command_frame.redo_index = 1
    
    def _node_data_to_dict(self, tree, parent, nodes_data):
        dic = {}
        for item in tree.get_children(parent):
            name = nodes_data[item]["name"]
            data = nodes_data[item]["data"]
            dic[item] = [name, self._node_data_to_dict(tree, item, nodes_data), data]
        return dic
        
        
        
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
            parent = self.node_tree.insert(parent="",index='end',text=group_name)
            for node in group:
                self.node_tree.insert(parent=parent,index='end',text=node)
        
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
        if command_name == "":
            messagebox.showerror("エラー", "コマンドが選択されていません")
            return
        
        self.bottom.save_command_nodes()
        
        command_name = self.command_frame.now_command_name
        tree = self.command_frame.commands[command_name]["tree"]
        node_id = tree.insert(parent="", index="end", text=item_name)
        
        frame = self.bottom.create_node_frame(command_name, node_id, item_name, [])
        frame.Ngrid(row=0, column=0, sticky="nsew")
        self.command_frame.commands[command_name]["nodes"][node_id] = {"name": item_name, "data": frame.data, "frame": frame}
    
    
    
class CommandSettingFrame(ttk.Frame):
    def __init__(self, master = None, command_frame: RightCommandFrame = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.command_frame = command_frame
        
        self.name_lab = ttk.Label(self, text="名前", style="MYStyle.TLabel")
        self.name_ent = ttk.Entry(self)
        
        self.name_lab.grid(row=0, column=0)
        self.name_ent.grid(row=0, column=1)

class CommandDetailFrame(CommandSettingFrame):
    def __init__(self, master = None, command_frame = None, command_name = None, tab_id = None):
        super().__init__(master, command_frame)
    
        self.command_name = command_name
    
        self.add_btn = ttk.Button(self, text="変更", command=self.change_command, style="Green.TButton")
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_command, style="Delete.TButton")
        self.add_btn.grid(row=1, column=1)
        self.delete_btn.grid(row=2, column=1)
        
        self.name_ent.insert(0, self.command_name)
    
    def delete_command(self):
        if not messagebox.askyesno("確認", "変更を保存しますか?"):
            return
        
        self.command_frame.now_command_name = ""
        self.command_frame.command_note.forget(self.command_frame.command_note.select())
        for datas in self.command_frame.commands[self.command_name]["nodes"].values():
            datas["frame"].destroy()
        self.command_frame.commands[self.command_name]["tree"].destroy()
        self.command_frame.commands[self.command_name]["var_tree"].destroy()
        self.command_frame.commands.pop(self.command_name)
        self.destroy()
    
    def change_command(self):
        name = self.name_ent.get()
        commands = self.command_frame.commands
        names = [command_name for command_name in commands]
        
        if not name:
            messagebox.showerror('エラー', '空欄を埋めてください')
            return
        if name in names and self.command_name != name:
            messagebox.showerror('エラー', 'すでに同じ名前のコマンドがあります')
            return

        if not messagebox.askyesno("確認", "変更を保存しますか?"):
            return
        
        
        
        #この下どうにか下noteの名前が変わるようにしてください！ご飯食べてくる！！bye
        self.command_frame.command_note.tab(self.command_frame.command_note.select(), text=name)
        self.command_frame.commands[name] = self.command_frame.commands.pop(self.command_name)
        self.command_frame.undo_nodes[name] =  self.command_frame.undo_nodes.pop(self.command_name)
        self.command_frame.con.top_left_frame.var_note.tab(str(self.command_frame.commands[name]["var_tree"]), text="local: "+name)
        self.command_frame.commands[name]["var_tree"].heading('#0', text=name)
        self.command_frame.commands[name]["tree"].heading('#0', text=name)
        for var_data in self.command_frame.commands[name]["vars"].values():
            var_data["frame"].par_name = name
        for node_data in self.command_frame.commands[name]["nodes"].values():
            node_data["frame"].command_name = name
        self.command_name = name
        self.command_frame.now_command_name = name
        
        self.command_frame.con.bottom_left_frame.frames["Variable"].update_dest()
           
class AddCommandFrame(CommandSettingFrame):
    def __init__(self, master = None, command_frame: RightCommandFrame = None):
        super().__init__(master, command_frame)
        
        self.add_btn = ttk.Button(self, text="追加", command=self.add_command, style="Green.TButton")
        self.add_btn.grid(row=1, column=1)
        
        
    def add_command(self):
        name = self.name_ent.get()
        commands = self.command_frame.commands
        names = [command_name for command_name in commands]
        
        if not name:
            messagebox.showerror('エラー', '空欄を埋めてください')
            return
        if name in names:
            messagebox.showerror('エラー', 'すでに同じ名前のコマンドがあります')
            return
        
        frame = ttk.Frame(self.command_frame.command_note)
        tree = ttk.Treeview(frame, height=100)
        scrollbar = ttk.Scrollbar(frame, orient = tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=lambda f, l: scrollbar.set(f, l))
        tree.column("#0", width=600)
        tree.heading("#0", text=name)
        tree.bind("<<TreeviewSelect>>", self.command_frame.select_node)
        tree.bind("<Control-c>", self.command_frame.copy)
        tree.bind("<Control-v>", self.command_frame.paste)
        tree.bind("<Control-d>", self.command_frame.deletion)
        tree.bind("<Control-s>", self.command_frame.node_save)
        tree.pack(fill="both", side="left")
        scrollbar.pack(fill="y", side="left")
        self.command_frame.undo_nodes[name] = []
        self.command_frame.commands[name] = {}
        self.command_frame.command_note.add(frame, text=name)
        self.command_frame.commands[name]["frame"] = CommandDetailFrame(self.command_frame.con.bottom_left_frame, self.command_frame, name)
        self.command_frame.commands[name]["tree_frame"] = frame
        self.command_frame.commands[name]["tree"] = tree
        self.command_frame.commands[name]["vars"] = {}
        self.command_frame.commands[name]["var_tree"] = {}
        self.command_frame.commands[name]["nodes"] = {}
        self.command_frame.commands[name]["frame"].grid(row=0, column=0, sticky="nsew")
        self.command_frame.con.top_left_frame.set_local_vars({}, name)
        
        self.command_frame.con.bottom_left_frame.frames["Variable"].update_dest()



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
        
        
        
        
    
        
        
        