from nodede import *

class VarFrame(NodeDetail):
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = ["",[]]):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(data):
            self.data = ["",[]]
        
        self.vars =  self.con.top_left_frame.variables
        
        if self.data[0] in self.vars:
            self.frame = self._get_type_frame()
        else:
            self.frame = VarSettingFrame(self, self.command_frame, self.command_name, self.node_id)
        
        self.frame.Ngrid(row=0, column=0, sticky="nsew")
        
    def _get_type_frame(self):
        type = self.vars[self.data[0]]["type"]
        frame = ttk.Frame(self, style="MYStyle.TFrame")
        if type == "str":
            frame = VarStringFrame(self, self.command_frame, self.command_name, self.node_id)
        elif type == "int":
            frame = VarIntFrame(self, self.command_frame, self.command_name, self.node_id)
        elif type == "float":
            frame = VarFloatFrame(self, self.command_frame, self.command_name, self.node_id)
        elif type == "bool":
            frame = VarBoolFrame(self, self.command_frame, self.command_name, self.node_id)
        return frame
    def change_node(self):
        if self.frame is None:
            return
        self.frame.change_node()

class VarNodeDetail(NodeDetail):
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = ""):
        super().__init__(master, command_frame, command_name, node_id, None)
        
        self.vf = master
        
        self.var_lab = NLable(self, text=self.vf.data[0], style="MYStyle.TLabel", Ntext="設定している変数")
        self.change_var_btn = ttk.Button(self, text="変数を変更", command=self.change_var, style="Green.TButton")
    
    def change_var(self):
        if not messagebox.askyesno("確認", "変更しますか？"):
            return
        self.vf.data = ["",[]]
        frame = VarSettingFrame(self.vf, self.command_frame, self.command_name, self.node_id)
        frame.Ngrid(row=0, column=0, sticky="nsew")
        self.destroy()
        
    def delete_node(self):
        self.vf.delete_node()
        
            

class VarSettingFrame(VarNodeDetail):
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = ""):
        super().__init__(master, command_frame, command_name, node_id)
        
        self.vars = self.vf.vars
        
        var_names = [name for name in self.vars.keys()]
        self.var_lab = NLable(self, text="設定する変数", style="MYStyle.TLabel")
        self.vars_com = NCombobox(self, values=var_names)
        
        self.vars_com.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.var_lab.grid(row=1, column=0)
        self.vars_com.grid(row=2, column=0)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
    
    def change_node(self):
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        var = self.vars_com.get()
        if var not in self.vars:
            messagebox.showerror("エラー", "変数名が間違っています")
            return
        self.vf.data[0] = var
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"][0] = var
        frame = self.vf._get_type_frame()
        frame.Ngrid(row=0, column=0, sticky="nsew")
    
class VarIntFrame(VarNodeDetail):
    
    seme_texts = ["追加する", "変更する"]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = ""):
        super().__init__(master, command_frame, command_name, node_id)
        
        detail_data = self.vf.data[1]
        
        if not any(detail_data):
            detail_data = ["", 0]
        
        same = self.seme_texts[detail_data[1]]
            
        self.val_lab = NLable(self, text="値", style="MYStyle.TLabel")
        self.val_ent = NEntry(self, width=40, text=detail_data[0])
        self.seme_lab = NLable(self, text="設定方法", style="MYStyle.TLabel")
        self.seme_com = NCombobox(self, values=self.seme_texts, text=same)
        
        self.val_ent.bind("<<ChangeText>>", self.on_change)
        self.seme_com.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.val_lab.grid(row=1, column=0)
        self.val_ent.grid(row=2, column=0)
        self.option_btn(self.val_ent).grid(row=2, column=1, sticky="w")
        self.seme_lab.grid(row=2, column=2)
        self.seme_com.grid(row=3, column=2)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
        self.var_lab.grid(row=4, column=1)
        self.change_var_btn.grid(row=5, column=1)
        
    
    def change_node(self):
        
        val = self.val_ent.get()
        seme = self.seme_com.get()
        odm =  conv.odm(val)
        types = conv.get_var_type(val, self.vf.vars)
        
        if seme not in self.seme_texts:
            messagebox.showerror("エラー", "設定方法がうまく設定されていません")
            return
        if not conv.all(types, "int") or (not tc.type_check("int", odm) and odm != ""):
            messagebox.showerror("エラー", "型があっていません")
            return
        
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        if seme == self.seme_texts[0]:
            seme = 0
        elif seme == self.seme_texts[1]:
            seme = 1
        
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"][1] = [val, seme]
        self.need_save_lab["text"] = ""
        self.isSave = True

class VarFloatFrame(VarNodeDetail):
    
    seme_texts = ["追加する", "変更する"]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = ""):
        super().__init__(master, command_frame, command_name, node_id)
        
        detail_data = self.vf.data[1]
        
        if not any(detail_data):
            detail_data = ["", 0, "False"]
        
        same = self.seme_texts[detail_data[1]]
            
        self.val_lab = NLable(self, text="値", style="MYStyle.TLabel")
        self.val_ent = NEntry(self, width=40, text=detail_data[0])
        self.seme_lab = NLable(self, text="設定方法", style="MYStyle.TLabel")
        self.seme_com = NCombobox(self, values=self.seme_texts, text=same)

        self.bln = tk.BooleanVar(value=tc.type_change("bool", detail_data[2]))
        self.check_box = ttk.Checkbutton(self, variable=self.bln, text="正確に計算する", command=self.on_change, style="MYStyle.TCheckbutton")
        
        self.val_ent.bind("<<ChangeText>>", self.on_change)
        self.seme_com.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.val_lab.grid(row=1, column=0)
        self.val_ent.grid(row=2, column=0)
        self.option_btn(self.val_ent).grid(row=2, column=1, sticky="w")
        self.seme_lab.grid(row=2, column=2)
        self.seme_com.grid(row=3, column=2)
        self.check_box.grid(row=3, column=3)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
        self.var_lab.grid(row=4, column=1)
        self.change_var_btn.grid(row=5, column=1)
        
    
    def change_node(self):
        
        val = self.val_ent.get()
        seme = self.seme_com.get()
        isRightness = self.bln.get()
        odm =  conv.odm(val)
        types = conv.get_var_type(val, self.vf.vars)
        
        if seme not in self.seme_texts:
            messagebox.showerror("エラー", "設定方法がうまく設定されていません")
            return
        if not conv.all(types, "float") or (not tc.type_check("float", odm) and odm != ""):
            messagebox.showerror("エラー", "型があっていません")
            return
        
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        if seme == self.seme_texts[0]:
            seme = 0
        elif seme == self.seme_texts[1]:
            seme = 1
        
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"][1] = [val, seme, str(isRightness)]
        self.need_save_lab["text"] = ""
        self.isSave = True
        
        
class VarStringFrame(VarNodeDetail):
    
    seme_texts = ["追加する", "変更する"]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = ""):
        super().__init__(master, command_frame, command_name, node_id)
        
        detail_data = self.vf.data[1]
        
        if not any(detail_data):
            detail_data = ["", 0]
        
        same = self.seme_texts[detail_data[1]]
            
        self.val_lab = NLable(self, text="値", style="MYStyle.TLabel")
        self.val_ent = NEntry(self, width=40, text=detail_data[0])
        self.seme_lab = NLable(self, text="設定方法", style="MYStyle.TLabel")
        self.seme_com = NCombobox(self, values=self.seme_texts, text=same)
        
        self.val_ent.bind("<<ChangeText>>", self.on_change)
        self.seme_com.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.val_lab.grid(row=1, column=0)
        self.val_ent.grid(row=2, column=0)
        self.option_btn(self.val_ent).grid(row=2, column=1, sticky="w")
        self.seme_lab.grid(row=2, column=2)
        self.seme_com.grid(row=3, column=2)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
        self.var_lab.grid(row=4, column=1)
        self.change_var_btn.grid(row=5, column=1)
        
    
    def change_node(self):
        
        val = self.val_ent.get()
        seme = self.seme_com.get()
        
        if seme not in self.seme_texts:
            messagebox.showerror("エラー", "設定方法がうまく設定されていません")
            return
        
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        if seme == self.seme_texts[0]:
            seme = 0
        elif seme == self.seme_texts[1]:
            seme = 1
        
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"][1] = [val, seme]
        self.need_save_lab["text"] = ""
        self.isSave = True

class VarBoolFrame(VarNodeDetail):
    
    seme_texts = ["Trueにする", "Falseにする", "反転する", "変数設定"]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = ""):
        super().__init__(master, command_frame, command_name, node_id)
        
        detail_data = self.vf.data[1]
        
        if not any(detail_data):
            detail_data = ["", 0]
        
        same = self.seme_texts[detail_data[1]]
            
        self.seme_lab = NLable(self, text="設定方法", style="MYStyle.TLabel")
        self.seme_com = NCombobox(self, values=self.seme_texts, text=same)
        
        var_names =  [name for name in self.con.top_left_frame.variables.keys()]
        self.var_name_lab = NLable(self, text="変数名", style="MYStyle.TLabel")
        self.var_name_com = NCombobox(self, values=var_names, text=detail_data[0])
        
        self.seme_com.bind("<<ChangeText>>", self.on_change)
        self.var_name_com.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.seme_lab.grid(row=1, column=0)
        self.seme_com.grid(row=2, column=0)
        self.var_name_lab.grid(row=1, column=2)
        self.var_name_com.grid(row=2, column=2)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
        self.var_lab.grid(row=4, column=1)
        self.change_var_btn.grid(row=5, column=1)
        
    
    def change_node(self):
        
        val = self.var_name_com.get()
        seme = self.seme_com.get()
        
        if seme not in self.seme_texts:
            messagebox.showerror("エラー", "設定方法がうまく設定されていません")
            return
        
        if seme == self.seme_texts[0]:
            seme = 0
        elif seme == self.seme_texts[1]:
            seme = 1
        elif seme == self.seme_texts[2]:
            seme = 2
        elif seme == self.seme_texts[3]:
            seme = 3
            var_names = [name for name in self.con.top_left_frame.variables.keys()]
            if val not in var_names:
                messagebox.showerror("エラー", "変数名が間違っています")
                return
        
        if not messagebox.askyesno("確認", "変更しますか？"):
            return
        
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"][1] = [val, seme]
        self.need_save_lab["text"] = ""
        self.isSave = True
 