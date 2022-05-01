from tkinter import ttk, messagebox
import tkinter as tk
#from work import RightCommandFrame
#import work


class NodeDetail(tk.Frame):
    
    options = [
        ["time", "year", "年"], ["time", "month", "月"], ["time", "day", "日"], ["time", "dow", "曜日"], ["time", "hour", "時"], ["time", "minute", "分"], ["time", "second", "秒"],
        ["message", "content", "送られたメッセージ"], ["message", "user_name", "メッセージを送ったユーザ名"], ["message", "user_id", "メッセージを送ったユーザid"], 
        ["message", "cahnnel_name", "メッセージを送ったチャンネル名"],["message", "cahnnel_id", "メッセージを送ったチャンネルd"], 
        ["message", "server_name", "メッセージを送ったサーバー名"], ["message", "server_id", "メッセージを送ったサーバーid"]
        ]
    
    def __init__(self, master = None, command_frame = None, node_id = ""):
        super().__init__(master)
        
        self.command_frame = command_frame
        self.con = master.con
        self.node_id = node_id
        self.isSave = True
        
        self.need_save_lab = ttk.Label(self, text="", foreground="#CCCCCC", font=("Lucida Console", 10))
    
    def option_btn(self, option_ent):
        btn = ttk.Button(self, text="...", width=5, command=lambda: self.show_option(option_ent))
        return btn
    
    def show_option(self, option_ent):
        self.top = self.con.top_left_frame
        
        self.option_win = tk.Toplevel()
        self.option_win.geometry("500x270")
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
        self.option_box = tk.Listbox(self.option_win, width=50, listvariable=list_value, justify="center", font=("UD デジタル 教科書体 NP-R", 15, "bold"))
        self.option_box.bind("<<ListboxSelect>>", lambda event, option_ent=option_ent:  self._option_click(event ,option_ent))
        
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
        command_tree = self.command_frame.command_trees[self.command_frame.tab_index]
        command_tree.delete(self.node_id)
        
        self.command_frame.node_settings.pop(self.node_id)
        
        self.destroy()
    
    def on_change(self, sv):
        if not self.isSave:
            return
        self.need_save_lab["text"] = "変更が保存されていません"
        self.isSave = False

class PrintFrame(NodeDetail):
    def __init__(self, master = None, command_frame = None, node_id = "", data = [""]):
        super().__init__(master, command_frame, node_id)
        
        if not any(data):
            data = [""]
        
        self.val_lab = ttk.Label(self, text="値")
        self.option_ent = NEntry(self, width=40, text=data[0])
        self.change_btn = ttk.Button(self, text="変更を保存", command=self.change_node)
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_node)
        
        self.option_ent.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=1)
        self.val_lab.grid(row=1, column=0)
        self.option_ent.grid(row=1, column=1)
        self.option_btn(self.option_ent).grid(row=1, column=2)
        self.change_btn.grid(row=2, column=1)
        self.delete_btn.grid(row=3, column=1)
        
    
    def change_node(self):
        if not messagebox.askyesno("確認", "変更しますか？"):
            return
        
        print_val = self.option_ent.get()
        self.command_frame.node_settings[self.node_id]["data"] = [print_val]
        self.need_save_lab["text"] = ""
        self.isSave = True
        

class SendMessageFrame(NodeDetail):
    
    dest_texts = ["コマンドを打ったチャンネル", "コマンドを打った人のDM"]
    
    def __init__(self, master = None, command_frame = None, node_id = "", data = ["",""]):
        super().__init__(master, command_frame, node_id)
        
        if not any(data):
            data = ["",0]
            
        dest = self.dest_texts[int(data[1])]
        
        self.message_lab = ttk.Label(self, text="メッセージ")
        self.option_ent = NEntry(self, width=40, text=data[0])
        self.dest_lab = ttk.Label(self, text="送り先")
        self.dest_com = ttk.Combobox(self, values=self.dest_texts)
        self.change_btn = ttk.Button(self, text="変更を保存", command=self.change_node)
        self.delete_btn = ttk.Button(self, text="削除", command=self.delete_node)
        
        self.dest_com.insert(0, dest)
        
        self.option_ent.bind("<<ChangeText>>", self.on_change)
        self.dest_com.bind("<<ComboboxSelected>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=1)
        self.message_lab.grid(row=1, column=0)
        self.option_ent.grid(row=1, column=1)
        self.option_btn(self.option_ent).grid(row=1, column=2)
        self.dest_lab.grid(row=0, column=3)
        self.dest_com.grid(row=1, column=3)
        self.change_btn.grid(row=2, column=1)
        self.delete_btn.grid(row=3, column=1)
    
    def change_node(self):
        if not messagebox.askyesno("確認", "変更しますか？"):
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
            
        self.command_frame.node_settings[self.node_id]["data"] = [message, dest]
        self.need_save_lab["text"] = ""
        self.isSave = True


class NEntry(ttk.Entry):
    
    def __init__(self, master = None, width = None, text = None) -> None:
        super().__init__(master=master, width=width)
        
        self.option_str_var = tk.StringVar(value=text)
        self.option_str_var.trace("w", lambda name, index, mode, sv=self.option_str_var: self.on_change(sv))
        
        self.configure(textvariable=self.option_str_var)
    
    
    def on_change(self, sv):
        self.event_generate("<<ChangeText>>")
        
        
           