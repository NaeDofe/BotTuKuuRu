from nwidget import *
from tkinter import ttk, messagebox
import tkinter as tk
import tc


class CommandSettingFrame(ttk.Frame):
    def __init__(self, master = None, command_frame = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.command_frame = command_frame
        
        self.name_lab = ttk.Label(self, text="名前", style="MYStyle.TLabel")
        self.name_ent = NEntry(self)
        self.need_save_lab = ttk.Label(self, text="", style="NotSaveStyle.TLabel")
        
        self.name_lab.grid(row=2, column=0)
        self.name_ent.grid(row=2, column=1)
        
    def on_change(self):
        self.need_save_lab["text"] = "変更が保存されていません"

class CommandDetailFrame(CommandSettingFrame):
    def __init__(self, master = None, command_frame = None, command_name = None, args = {}):
        super().__init__(master, command_frame)
        
        self.args = args
    
        self.command_name = command_name
    
        self.title_lab = ttk.Label(self, text="コマンドの設定", style="MYStyle.TLabel")
        self.add_btn = ttk.Button(self, text="変更を保存", command=self.change_command, style="Green.TButton")
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_command, style="Delete.TButton")
        
        self.args_lab = ttk.Label(self, text="引数", style="MYStyle.TLabel")
        self.args_delete_btn = ttk.Button(self, text="引数削除", command=self.click_delete_args_btn, style="Delete.TButton")
        self.args_add_btn = ttk.Button(self, text="引数追加", command=self.click_add_args_btn, style="Green.TButton")
        
        self.need_save_lab.grid(row=0, column=1)
        self.title_lab.grid(row=1, column=1)
        self.add_btn.grid(row=3, column=1)
        self.delete_btn.grid(row=4, column=1)
        self.args_lab.grid(row=4, column=2)
        self.args_add_btn.grid(row=5, column=3)
        self.args_delete_btn.grid(row=6, column=3)
        
        self.name_ent.insert(0, self.command_name)
        
        self.name_ent.bind("<<ChangeText>>", lambda event: self.on_change())
        
        self.args_tree = ttk.Treeview(self)
        self.args_tree['columns'] = ('ID','Name','Score')
        self.args_tree.column('#0',width=0, stretch='no')
        self.args_tree.column('ID', anchor='center', width=60)
        self.args_tree.column('Name',anchor='w', width=100)
        self.args_tree.column('Score', anchor='center', width=80)
            
        self.args_tree.heading('#0',text="")
        self.args_tree.heading('ID', text='型',anchor='center')
        self.args_tree.heading('Name', text='名前', anchor='w')
        self.args_tree.heading('Score',text='初期値', anchor='center')
        
        self.args_tree.grid(row=5, column=2, rowspan=2)
        
        for arg_name, arg_datas in self.args.items():
            arg_type = arg_datas[0]
            arg_default = arg_datas[1]
            self.args_tree.insert("", "end", values=(arg_type, arg_name, arg_default,))
    
    def click_add_args_btn(self):
        self.aaw = AddArgsWindow(self.add_args, bg=self.command_frame.con.bt.defalt_bg)
    
    def click_delete_args_btn(self):
        select_ids = self.args_tree.selection()
        if not any(select_ids):
            return
        if not messagebox.askyesno("確認", "選択されている引数をすべて削除しますか?"):
            return
        for select_id in select_ids:
            args_name = self.args_tree.item(select_id, "values")[1]
            self.args.pop(args_name)
        self.args_tree.delete(select_ids)
        self.on_change()
        
        
        
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
        

        self.command_frame.command_note.tab(self.command_frame.command_note.select(), text=name)
        self.command_frame.commands[name] = self.command_frame.commands.pop(self.command_name)
        self.command_frame.undo_nodes[name] =  self.command_frame.undo_nodes.pop(self.command_name)
        self.command_frame.con.top_left_frame.var_note.tab(str(self.command_frame.commands[name]["var_tree"]), text="local: "+name)
        self.command_frame.commands[name]["var_tree"].heading('#0', text=name)
        self.command_frame.commands[name]["tree"].heading('#0', text=name)
        self.command_frame.commands[name]["args"] = self.args
        for var_data in self.command_frame.commands[name]["vars"].values():
            var_data["frame"].par_name = name
        for node_data in self.command_frame.commands[name]["nodes"].values():
            node_data["frame"].command_name = name
        self.command_name = name
        self.command_frame.now_command_name = name
        
        self.command_frame.con.bottom_left_frame.frames["Variable"].update_dest()
        
        self.need_save_lab["text"] = ""
        
    def add_args(self, arg_name, arg_type, arg_default):
        if not all([arg_name, arg_type]):
            messagebox.showerror('エラー', '空欄を埋めてください')
            return False
        if arg_name in self.args:
            messagebox.showerror('エラー', 'すでに同じ名前の変数があります')
            return False
        if not tc.type_check(arg_type, arg_default) and arg_default != "":
            messagebox.showerror('エラー', '型と値が合いません')
            return False
        
        self.args_tree.insert("", "end", values=(arg_type, arg_name, arg_default,))
        self.args[arg_name] = [arg_type, arg_default]
        
        self.aaw.destroy()
        self.on_change()

class AddArgsWindow(tk.Toplevel):
    
    def __init__(self, func, bg = "") -> None:
        super().__init__(bg=bg)
        self.func = func
        self.geometry("350x130+785+475")
        self.grab_set()
        
        self.title_lab = ttk.Label(self, text="引数の追加", style="MYStyle.TLabel")
        self.name_lab = ttk.Label(self, text="名前", style="MYStyle.TLabel")
        self.name_ent = ttk.Entry(self, width=40)
        self.type_lab = ttk.Label(self, text="型", style="MYStyle.TLabel")
        self.type_com = ttk.Combobox(self, values=["str","int","float","bool"], width=40)
        self.default_lab = ttk.Label(self, text="初期値", style="MYStyle.TLabel")
        self.default_ent = ttk.Entry(self, width=40)
        self.add_btn = ttk.Button(self, text="追加", command=self.click_add_btn, style="Green.TButton")
        
        self.title_lab.grid(row=0, column=1)
        self.name_lab.grid(row=1, column=0)
        self.name_ent.grid(row=1, column=1)
        self.type_lab.grid(row=2, column=0)
        self.type_com.grid(row=2, column=1)
        self.default_lab.grid(row=3, column=0)
        self.default_ent.grid(row=3, column=1)
        self.add_btn.grid(row=4, column=1, sticky="e")
    
    def click_add_btn(self):
        arg_name = self.name_ent.get()
        arg_type = self.type_com.get()
        arg_default = self.default_ent.get()
        
        self.func(arg_name, arg_type, arg_default)
        
           
class AddCommandFrame(CommandSettingFrame):
    def __init__(self, master = None, command_frame = None):
        super().__init__(master, command_frame)
        
        self.add_btn = ttk.Button(self, text="追加", command=self.add_command, style="Green.TButton")
        self.add_btn.grid(row=3, column=1)
        
        
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
        self.command_frame.commands[name]["args"] = {}
        self.command_frame.commands[name]["nodes"] = {}
        self.command_frame.commands[name]["frame"].grid(row=0, column=0, sticky="nsew")
        self.command_frame.con.top_left_frame.set_local_vars({}, name)
        
        self.command_frame.con.bottom_left_frame.frames["Variable"].update_dest()