from tkinter import ttk, messagebox
from nwidget import *
import tkinter as tk
import conv
import tc
#from work import RightCommandFrame
#import work


class NodeDetail(ttk.Frame):
    
    options = [
        ["time", "year", "年"], ["time", "month", "月"], ["time", "day", "日"], ["time", "dow", "曜日"], ["time", "hour", "時"], ["time", "minute", "分"], ["time", "second", "秒"],
        ["message", "content", "送られたメッセージ"], ["message", "user_name", "メッセージを送ったユーザ名"], ["message", "user_id", "メッセージを送ったユーザid"], 
        ["message", "cahnnel_name", "メッセージを送ったチャンネル名"],["message", "cahnnel_id", "メッセージを送ったチャンネルid"], 
        ["message", "sever_name", "メッセージを送ったサーバー名"], ["message", "server_id", "メッセージを送ったサーバーid"]
        ]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = None):
        super().__init__(master, style="MYStyle.TFrame")
        
        self.command_frame = command_frame
        self.con = master.con
        self.command_name = command_name
        self.node_id = node_id
        self.data = data
        
        self.command_tree = self.command_frame.commands[command_name]["tree"]
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
        self.cf = self.con.right_command_frame
        
        self.option_win = tk.Toplevel(bg=self.con.bt.defalt_bg)
        self.option_win.geometry("450x600")
        self.option_win.grab_set()
        
        title_lab = ttk.Label(self.option_win, text="オプションの選択")
        
        self.option_list = [["args",name] for name in self.cf.commands[self.command_name]["args"].keys()]
        self.option_list.extend([["var_global",name] for name in self.top.global_var.keys()])
        self.option_list.extend([["var_local",name] for name in self.cf.commands[self.command_name]["vars"].keys()])
        for option in self.options:
            self.option_list.append([option[0], option[1]])
        
        varop_list = ["引数:"+name for name in self.cf.commands[self.command_name]["args"].keys()]
        varop_list.extend(["グローバル変数:"+name for name in self.top.global_var.keys()])
        varop_list.extend(["ローカル変数:"+name for name in self.cf.commands[self.command_name]["vars"].keys()])
        
        for option in self.options:
            if option[0] == "time":
                varop_list.append("時間:"+option[2])
            if option[0] == "message":
                varop_list.append("メッセージ:"+option[2])
        
        self.check_list = NCheckList(self.option_win, width=400, height=400, bg=self.con.bt.defalt_bg, values=varop_list)
        
        add_btn = ttk.Button(self.option_win, text="追加", style="Green.TButton", command=lambda: self._add_option(option_ent))
    
        title_lab.grid(row=0, column=0)
        self.check_list.grid(row=1, column=0)
        add_btn.grid(row=2, column=0, sticky="e")
        
    
    def _add_option(self, option_ent):
        
        option_text = ""
        for i, check_value in enumerate(self.check_list.booleanvars):
            isClick = check_value.get()
            if isClick:
                option_data = self.option_list[i]
                if option_data[0] == "var_global":
                    option_text += f"[vg={option_data[1]}]"
                elif option_data[0] == "var_local":
                    option_text += f"[vl={option_data[1]}]"
                elif option_data[0] == "args":
                    option_text += f"[a={option_data[1]}]"
                elif option_data[0] == "time":
                    option_text += f"[t={option_data[1]}]"
                elif option_data[0] == "message":
                    option_text += f"[m={option_data[1]}]" 
        
        option_ent.insert("end", option_text)
        
        self.option_win.destroy()

    def delete_node(self, conf = True):
        if conf:
            if not messagebox.askyesno("確認", "ノードを削除しますか"):
                return
            self.con.bottom_left_frame.save_command_nodes()
        
        self.command_tree.delete(self.node_id)
        self.command_frame.commands[self.command_name]["nodes"].pop(self.node_id)
        self.destroy()
    
    def change_node(self):
        return
    
    def save_node(self, datas):
        self.con.bottom_left_frame.save_command_nodes()
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"] = datas
        self.need_save_lab["text"] = ""
        self.isSave = True
    
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
        
        self.save_node([print_val])
        

class SendMessageFrame(NodeDetail):
    
    dest_texts = ["コマンドを打ったチャンネル", "コマンドを打った人のDM","channel_idで指定", "user_idで指定"]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = ["",""]):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(data):
            self.data = ["", 0, ""]
            
        dest = self.dest_texts[int(self.data[1])]
        
        self.message_lab = NLable(self, text="メッセージ", style="MYStyle.TLabel")
        self.message_ent = NEntry(self, width=40, text=self.data[0])
        self.dest_lab = NLable(self, text="送り先", style="MYStyle.TLabel")
        self.dest_com = ttk.Combobox(self, values=self.dest_texts)
        
        self.user_id_lab = NLable(self, text="id", style="MYStyle.TLabel")
        self.user_id_ent = NEntry(self, width=40, text=self.data[2])
        
        self.dest_com.insert(0, dest)
        
        self.message_ent.bind("<<ChangeText>>", self.on_change)
        self.user_id_ent.bind("<<ChangeText>>", self.on_change)
        self.dest_com.bind("<<ComboboxSelected>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.message_lab.grid(row=1, column=0)
        self.message_ent.grid(row=2, column=0)
        self.option_btn(self.message_ent).grid(row=2, column=1)
        self.dest_lab.grid(row=2, column=2)
        self.dest_com.grid(row=3, column=2)
        self.user_id_lab.grid(row=2, column=3)
        self.user_id_ent.grid(row=3, column=3)
        self.option_btn(self.user_id_ent).grid(row=3, column=4)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
    
    def change_node(self):
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        message = self.message_ent.get()
        dest = self.dest_com.get()
        user_id  = self.user_id_ent.get()
        if dest not in self.dest_texts:
            messagebox.showerror("エラー", "送り先がうまく設定されていません")
            return
        
        dest = self.dest_texts.index(dest)
        
        self.save_node([message, dest, user_id])

class ForFrame(NodeDetail):
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = ["",""]):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(data):
            self.data = [""]
            
        self.times_lab = NLable(self, text="回数", style="MYStyle.TLabel")
        self.times_ent = NEntry(self, width=40, text=self.data[0],)
        
        self.times_ent.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.times_lab.grid(row=1, column=0)
        self.times_ent.grid(row=2, column=0)
        self.option_btn(self.times_ent).grid(row=2, column=1)
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
    
    def change_node(self):
        
        times = self.times_ent.get()
        
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        self.save_node([times])

class EmptyFrame(NodeDetail):
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = []):
        super().__init__(master, command_frame, command_name, node_id, data)
        self.data = data
        
        self.need_save_lab.grid(row=0, column=0)
        self.delete_btn.grid(row=1, column=0)


class ClearMessageFrame(NodeDetail):
    
    delmes_texts = ["行数で削除", "コマンドを打ったメッセージ"]
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = []):
        super().__init__(master, command_frame, command_name, node_id, data)

        if not any(data):
            self.data = ["", 0]
            
        delmes = self.delmes_texts[self.data[1]]
        
        self.line_lab = NLable(self, text="行数", style="MYStyle.TLabel")
        self.line_ent = NEntry(self, width=40, text=self.data[0])
        
        self.delmes_lab = NLable(self, text="削除メッセージ", style="MYStyle.TLabel")
        self.delmes_com = NCombobox(self, values=self.delmes_texts, text=delmes)
        
        self.delmes_com.bind("<<ChangeText>>", self.change_delmes_com)
        
        self.need_save_lab.grid(row=0, column=0)
        self.line_lab.grid(row=1, column=0)
        self.line_ent.grid(row=2, column=0)
        self.option_btn(self.line_ent).grid(row=2, column=1)
        
        self.delmes_lab.grid(row=2, column=2)
        self.delmes_com.grid(row=3, column=2)
        
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=4, column=0)
    
    def change_delmes_com(self, event):
        delmes = self.delmes_com.get()
        if delmes == self.delmes_texts[0]:
            self.line_ent["state"] = "normal"
        else:
            self.line_ent["state"] = "disable"
        
        
    def change_node(self):
        
        line = self.line_ent.get()
        delmes = self.delmes_com.get()
        
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        if delmes not in self.delmes_texts:
            messagebox.showerror("エラー", "削除メッセージがうまく設定されていません")
            return

        delmes = self.delmes_texts.index(delmes)
        
        self.save_node([line, delmes])
        
    

        
        