from tkinter import ttk, messagebox
import tkinter as tk
import tc

class VariableSettingFrame(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        
        self.frame_name = ttk.Label(self, text="変数の詳細設定")
        self.name_lab = ttk.Label(self, text="名前")
        self.name_ent = ttk.Entry(self)
        self.type_lab = ttk.Label(self, text="型")
        self.type_com = ttk.Combobox(self, values=["str","int","float","bool"])
        self.default_lab = ttk.Label(self, text="初期値")
        self.default_ent = ttk.Entry(self)
        
        self.frame_name.grid(row=0, column=1)
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
    def __init__(self, master = None, top = None, var_name = "", var_type = "", var_default = ""):
        super().__init__(master)
        
        self.top = top
        
        
        self.change_btn = ttk.Button(self, text="変更", command=self.change_var)
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_var)
        
        self.name_ent.insert(0, var_name)
        self.type_com.insert(0, var_type)
        self.default_ent.insert(0, var_default)
        
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
        
        if not self.no_mistake(var_name, var_type, var_default, variables, original_name):
            return
        
        index = var_tree.index(select_id)
        
        variables.pop(original_name)
        var_tree.delete(self.top.selected_var_id)
        
        variables[var_name] = {"type": var_type, "val": var_default, "frame": self}
        item_id = var_tree.insert(parent="", index=index, values=(var_type, var_name, var_default,))
        
        self.top.selected_var_id = item_id
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

class AddVariableFrame(VariableSettingFrame):
    def __init__(self, master = None, con = None):
        super().__init__(master)
        
        self.con = con

        self.add_btn = ttk.Button(self, text="追加", command=self.append_var_tree)
        
        self.add_btn.grid(row=4, column=1)

    
    def append_var_tree(self):
        var_tree = self.con.top_left_frame.var_tree
        variables = self.con.top_left_frame.variables
        
        var_name = self.name_ent.get()
        var_type = self.type_com.get()
        var_default = self.default_ent.get()
        
        if not self.no_mistake(var_name, var_type, var_default, variables):
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
        