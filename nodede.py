from tkinter import ttk, messagebox
import tkinter as tk
import conv
import tc
import re
#from work import RightCommandFrame
#import work


class NodeDetail(ttk.Frame):
    
    options = [
        ["time", "year", "年"], ["time", "month", "月"], ["time", "day", "日"], ["time", "dow", "曜日"], ["time", "hour", "時"], ["time", "minute", "分"], ["time", "second", "秒"],
        ["message", "content", "送られたメッセージ"], ["message", "user_name", "メッセージを送ったユーザ名"], ["message", "user_id", "メッセージを送ったユーザid"], 
        ["message", "cahnnel_name", "メッセージを送ったチャンネル名"],["message", "cahnnel_id", "メッセージを送ったチャンネルid"], 
        ["message", "server_name", "メッセージを送ったサーバー名"], ["message", "server_id", "メッセージを送ったサーバーid"]
        ]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.command_frame = command_frame
        self.con = master.con
        self.command_name = command_name
        self.node_id = node_id
        self.data = data
        
        self.command_tree = self.command_frame.command_trees[command_name]
        self.isSave = True
        
        self.change_btn = ttk.Button(self, text="変更を保存", command=self.change_node, style="Green.TButton")
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_node, style="Delete.TButton")
        self.need_save_lab = ttk.Label(self, text="", style="NotSaveStyle.TLabel")
    
    def option_btn(self, option_ent, master=None):
        if master is None:
            master = self
        btn = NButton(master, text="...", width=40,height=22, command=lambda: self.show_option(option_ent), style="NodeStyle.TButton")
        return btn
    
    def show_option(self, option_ent):
        self.top = self.con.top_left_frame
        
        self.option_win = tk.Toplevel()
        self.option_win.geometry("450x600")
        self.option_win.grab_set()
        self.title_lab = ttk.Label(self.option_win, text="オプションの選択")
        
        
        self.option_list = [["var",name] for name in self.top.variables.keys()]
        for option in self.options:
            self.option_list.append([option[0], option[1]])
        
        var_list = ["変数:"+name for name in self.top.variables.keys()]
        for option in self.options:
            if option[0] == "time":
                var_list.append(["時間:"+option[2]])
            if option[0] == "message":
                var_list.append(["メッセージ:"+option[2]])
                
        list_value = tk.StringVar(value=var_list)
        self.option_box = tk.Listbox(self.option_win, width=50, height=30, listvariable=list_value, justify="center", font=("Yu Gothic UI Semibold", 12, "bold"), background="#1a1a1a")
        self.option_box.bind("<<ListboxSelect>>", lambda event, option_ent=option_ent:  self._option_click(event ,option_ent))
        
        for i ,val in enumerate(var_list):
            if i%2 == 0:
                self.option_box.itemconfigure(i, background="#1a1a1a", foreground="#e6e6e6")
            else:
                self.option_box.itemconfigure(i, background="#333333", foreground="#e6e6e6")
        
        self.title_lab.grid(row=0, column=0)
        self.option_box.grid(row=1, column=0)
    
    def _option_click(self, event, option_ent):
        option_index = self.option_box.curselection()[0]
        option_data = self.option_list[option_index]
        
        option_text = ""
        if option_data[0] == "var":
            option_text = f"[v={option_data[1]}]"
        elif option_data[0] == "time":
            option_text = f"[t={option_data[1]}]"
        elif option_data[0] == "message":
            option_text = f"[m={option_data[1]}]"
        
        option_ent.insert("end", option_text)
        
        self.option_win.destroy()

    def delete_node(self):
        if not messagebox.askyesno("確認", "ノードを削除しますか"):
            return
        
        self.command_tree.delete(self.node_id)
        self.command_frame.node_settings[self.command_name].pop(self.node_id)
        
        self.destroy()
    
    def change_node(self):
        return
    
    def on_change(self, sv = None):
        if not self.isSave:
            return
        self.command_tree.item(self.node_id, tags="not_save")
        self.need_save_lab["text"] = "変更が保存されていません"
        self.isSave = False
    
    def Ngrid(self, row=0, column=0, sticky="nsew"):
        self.Nbind()
        self.grid(row=row, column=column, sticky=sticky)
        
    def Nbind(self):
        for widget in self.winfo_children():
            widget.bind("<Control-d>", lambda event: self.delete_node())
            widget.bind("<Control-s>", lambda event: self.change_node())

class PrintFrame(NodeDetail):
    def __init__(self, master = None, command_frame = None,command_name = "", node_id = "", data = [""]):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(self.data):
            self.data = [""]
            
        
        self.val_lab = NLable(self, text="値", style="MYStyle.TLabel")
        self.option_ent = NEntry(self, width=40, text=self.data[0])
        
        self.option_ent.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.val_lab.grid(row=1, column=0)
        self.option_ent.grid(row=2, column=0)
        self.option_btn(self.option_ent).grid(row=2, column=1)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
        
    
    def change_node(self):
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        print_val = self.option_ent.get()
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.node_settings[self.command_name][self.node_id]["data"] = [print_val]
        self.need_save_lab["text"] = ""
        self.isSave = True
        

class SendMessageFrame(NodeDetail):
    
    dest_texts = ["コマンドを打ったチャンネル", "コマンドを打った人のDM"]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = ["",""]):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(data):
            self.data = ["",0]
            
        dest = self.dest_texts[int(self.data[1])]
        
        self.message_lab = NLable(self, text="メッセージ", style="MYStyle.TLabel")
        self.option_ent = NEntry(self, width=40, text=self.data[0])
        self.dest_lab = NLable(self, text="送り先", style="MYStyle.TLabel")
        self.dest_com = ttk.Combobox(self, values=self.dest_texts)
        
        self.dest_com.insert(0, dest)
        
        self.option_ent.bind("<<ChangeText>>", self.on_change)
        self.dest_com.bind("<<ComboboxSelected>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.message_lab.grid(row=1, column=0)
        self.option_ent.grid(row=2, column=0)
        self.option_btn(self.option_ent).grid(row=2, column=1)
        self.dest_lab.grid(row=2, column=2)
        self.dest_com.grid(row=3, column=2)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
    
    def change_node(self):
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        message = self.option_ent.get()
        dest = self.dest_com.get()
        
        if dest not in self.dest_texts:
            messagebox.showerror("エラー", "送り先がうまく設定されていません")
            return
        
        if dest == self.dest_texts[0]:
            dest = 0
        elif dest == self.dest_texts[1]:
            dest = 1
        
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.node_settings[self.command_name][self.node_id]["data"] = [message, dest]
        self.need_save_lab["text"] = ""
        self.isSave = True

class VarFrame(NodeDetail):
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = ["",[]]):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(data):
            self.data = ["",[]]
        
        self.vars =  self.con.top_left_frame.variables
        
        if self.data[0] in self.vars:
            self._set_type_frame()
        else:
            self.frame = VarSettingFrame(self, self.command_frame, self.command_name, self.node_id)
        
        self.frame.Ngrid(row=0, column=0, sticky="nsew")
        
    def _set_type_frame(self):
        type = self.vars[self.data[0]]["type"]
        
        if type == "str":
            self.frame = VarStringFrame(self, self.command_frame, self.command_name, self.node_id)
        elif type == "int":
            self.frame = VarIntFrame(self, self.command_frame, self.command_name, self.node_id)
        elif type == "float":
            self.frame = VarFloatFrame(self, self.command_frame, self.command_name, self.node_id)
        elif type == "bool":
            self.frame = VarBoolFrame(self, self.command_frame, self.command_name, self.node_id)
    
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
        self.command_frame.node_settings[self.command_name][self.node_id]["data"][0] = var
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
        self.command_frame.node_settings[self.command_name][self.node_id]["data"][1] = [val, seme]
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
        self.check_box = ttk.Checkbutton(self, variable=self.bln, text = "正確に計算する", command=self.on_change, style="MYStyle.TCheckbutton")
        
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
        self.command_frame.node_settings[self.command_name][self.node_id]["data"][1] = [val, seme, str(isRightness)]
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
        self.command_frame.node_settings[self.command_name][self.node_id]["data"][1] = [val, seme]
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
        self.command_frame.node_settings[self.command_name][self.node_id]["data"][1] = [val, seme]
        self.need_save_lab["text"] = ""
        self.isSave = True
        
        
        
        
        
        
        
        
        
    
class NButton(ttk.Frame):
    def __init__(self, master, text = "", width = None, height = None, command = None, style=None):
        super().__init__(master=master, width=width, height=height)
        
        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, command=command, style=style)
        self._btn.pack(fill=tk.BOTH, expand=1)
        

class NEntry(ttk.Entry):
    
    def __init__(self, master = None, width = None, text = None) -> None:
        super().__init__(master=master, width=width)
        
        self.option_str_var = tk.StringVar(value=text)
        self.option_str_var.trace("w", lambda name, index, mode, sv=self.option_str_var: self.on_change(sv))
        
        self.configure(textvariable=self.option_str_var)
    
    
    def on_change(self, sv):
        self.event_generate("<<ChangeText>>")

class NLable(ttk.Labelframe):
    def __init__(self, master,text = None, style = None, Ntext = ""):
        super().__init__(master, style="Dict.TLabelframe", text=Ntext)
        
        self._lab = ttk.Label(self, text=text, style=style)
        self._lab.pack()

class NCombobox(ttk.Combobox):
    def __init__(self, master = None, width = None, text = None, values = None) -> None:
        super().__init__(master=master, width=width)
        self.option_str_var = tk.StringVar(value=text)
        self.option_str_var.trace("w", lambda name, index, mode, sv=self.option_str_var: self.on_change(sv))
            
        self.configure(textvariable=self.option_str_var, values=values)
        
        self.bind("<<ComboboxSelected>>", self.on_change)
        
    def on_change(self, sv = None):
        self.event_generate("<<ChangeText>>")
        
           