from tkinter import ttk, messagebox
import tkinter as tk
import tc

class VariableSettingFrame(ttk.Frame):
    def __init__(self, master = None, con = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.con = con
        
        self.name_lab = ttk.Label(self, text="名前", style="MYStyle.TLabel")
        self.name_ent = ttk.Entry(self, width=40)
        self.type_lab = ttk.Label(self, text="型", style="MYStyle.TLabel")
        self.type_com = ttk.Combobox(self, values=["str","int","float","bool"], width=40)
        self.default_lab = ttk.Label(self, text="初期値", style="MYStyle.TLabel")
        self.default_ent = ttk.Entry(self, width=40)
        
        
        self.name_lab.grid(row=1, column=0)
        self.name_ent.grid(row=1, column=1)
        self.type_lab.grid(row=2, column=0)
        self.type_com.grid(row=2, column=1)
        self.default_lab.grid(row=3, column=0)
        self.default_ent.grid(row=3, column=1)
    
    def no_mistake(self, var_name, var_type, var_default, variables, original_name = ""):
        
        if not all([var_name, var_type, var_default]):
            messagebox.showerror('エラー', '空欄を埋めてください')
            return False
        if var_name in variables and var_name != original_name:
            messagebox.showerror('エラー', 'すでに同じ名前の変数があります')
            return False
        if not tc.type_check(var_type, var_default):
            messagebox.showerror('エラー', '型と値が合いません')
            return False
        if not messagebox.askquestion("確認", "変数を変更しますか？"):
            return False
        
        return True
    
    
class VariableDetailFrame(VariableSettingFrame):
    def __init__(self, master = None, top = None, var_name = "", var_type = "", var_default = "", par_name = "global"):
        super().__init__(master, top.con)
        
        self.top = top
        
        self.par_name = par_name
        self.original_name = var_name
        
        self.frame_name = ttk.Label(self, text="変数の詳細設定", style="MYStyle.TLabel")
        self.change_btn = ttk.Button(self, text="変更", command=self.change_var, style="Green.TButton")
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_var, style="Delete.TButton")
        
        self.name_ent.insert(0, var_name)
        self.type_com.insert(0, var_type)
        self.default_ent.insert(0, var_default)
        
        self.frame_name.grid(row=0, column=1)
        self.change_btn.grid(row=4, column=1)
        self.delete_btn.grid(row=5, column=1)
    
    def change_var(self):
        var_name = self.name_ent.get()
        var_type = self.type_com.get()
        var_default = self.default_ent.get()
        global_var = self.top.global_var
        
        vars = {}
        
        if self.par_name == "global":
            var_tree = self.top.var_tree
            variables = global_var
            vars = global_var
            select_id = self.top.selected_var_id
        else:
            var_tree = self.con.right_command_frame.commands[self.par_name]["var_tree"]
            vars = self.con.right_command_frame.commands[self.par_name]["vars"]
            variables = {**global_var, **vars}
            select_id = self.top.selected_var_id
        
        if not self.no_mistake(var_name, var_type, var_default, variables, self.original_name):
            return
        
        index = var_tree.index(select_id)
        
        vars.pop(self.original_name)
        var_tree.delete(self.top.selected_var_id)
        
        
        vars[var_name] = {"type": var_type, "val": var_default, "frame": self}
        item_id = var_tree.insert(parent="", index=index, values=(var_type, var_name, var_default,))
        
        self.original_name = var_name
        self.top.selected_var_id = item_id
        
        if self.par_name == "global":
            self.top.global_var = vars
        else:
            self.con.right_command_frame.commands[self.par_name]["vars"] = vars
    
    def delete_var(self):
        if not messagebox.askquestion("確認", "変数を削除しますか？"):
            return
        if self.par_name == "global":
            var_tree = self.top.var_tree
            self.top.variables.pop(self.original_name)
        else:
            var_tree = self.con.right_command_frame.commands[self.par_name]["var_tree"]
            self.con.right_command_frame.commands[self.par_name]["vars"].pop(self.original_name)
        
        var_tree.delete(self.top.selected_var_id)
        
        self.top.selected_var_id = ""
        
        self.destroy()

class AddVariableFrame(VariableSettingFrame):
    def __init__(self, master = None, con = None):
        super().__init__(master, con)
        

        self.frame_name = ttk.Label(self, text="変数の追加", style="MYStyle.TLabel")
        self.add_btn = ttk.Button(self, text="追加", command=self.append_var_tree, style="Green.TButton")
        self.dest_lab = ttk.Label(self, text="保存先", style="MYStyle.TLabel")
        self.dest_ent = ttk.Combobox(self, values=("global"))
        
        self.frame_name.grid(row=0, column=1)
        self.add_btn.grid(row=4, column=1)
        self.dest_lab.grid(row=0, column=2)
        self.dest_ent.grid(row=1, column=2)
        
        self.update_dest()
    
    def update_dest(self):
        dests = list(self.con.right_command_frame.commands.keys())
        dests.append("global")
        
        self.dest_ent.configure(values=list(reversed(dests)))

    
    def append_var_tree(self):
        global_var = self.con.top_left_frame.global_var
        
        var_name = self.name_ent.get()
        var_type = self.type_com.get()
        var_default = self.default_ent.get()
        var_dest = self.dest_ent.get()
        
        command_names = list(self.con.right_command_frame.commands.keys())
        command_names.append("global")
        
        if var_dest not in command_names:
            messagebox.showerror('エラー', '保存先が間違っています')
            return
        
        variables = {}
        if var_dest == "global":
            variables = global_var
        else:
            local_var = self.con.right_command_frame.commands[var_dest]["vars"]
            variables = {**global_var, **local_var}
        
        if not self.no_mistake(var_name, var_type, var_default, variables):
            return
        
        frame = VariableDetailFrame(
            master=self.con.bottom_left_frame, 
            top=self.con.top_left_frame, 
            var_name=var_name, 
            var_type=var_type, 
            var_default=var_default,
            par_name=var_dest)
        frame.grid(row=0, column=0, sticky="nsew")
        
        if var_dest == "global":
            self.con.top_left_frame.variables[var_name] = {"type": var_type, "val": var_default, "frame": frame}
            
            var_tree = self.con.top_left_frame.var_tree
            var_tree.insert(parent="", index="end", values=(var_type, var_name, var_default,))
        else:
            self.con.right_command_frame.commands[var_dest]["vars"][var_name] = {"type": var_type, "val": var_default, "frame": frame}
            
            var_tree = self.con.right_command_frame.commands[var_dest]["var_tree"]
            var_tree.insert(parent="", index="end", values=(var_type, var_name, var_default,))
        
        
        