from nodede import *
import pyautogui
import json

class ElseFrame(NodeDetail):
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = []):
        super().__init__(master, command_frame, command_name, node_id, data)
        self.data = []
        
        self.need_save_lab.grid(row=0, column=0)
        self.delete_btn.grid(row=1, column=0)

class BranchFrame(NodeDetail):
    
    def __init__(self, master = None, command_frame = None, command_name = "", node_id = "", data = None):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(self.data):
            self.data = ["and", {}]
        
        self.bg = self.con.bt.defalt_bg
        
        self.branch_tree = ttk.Treeview(self, height=12, columns=("Content",))
        self.branch_tree.column("#0", width=200)
        self.branch_tree.column("Content", width=400)
        self.branch_tree.heading("#0", text="条件")
        self.branch_tree.heading("Content", text="内容")
        self.branch_tree.bind("<<TreeviewSelect>>", self.select_condition)
        
        self.and_or_com = NCombobox(self, values=("and","or"), text=self.data[0])
        self.add_branch_btn = ttk.Button(self, text="条件を追加", style="Green.TButton", command=self.click_add_condition)
        
        self.and_or_com.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.branch_tree.grid(row=1, column=0, rowspan=2, columnspan=2)
        self.and_or_com.grid(row=1, column=2)
        self.add_branch_btn.grid(row=2, column=2)
        
        self.change_btn.grid(row=3, column=0)
        self.delete_btn.grid(row=3, column=1)
        
        self.data[1] = self._set_condition(self.data[1], "")
    
    def _set_condition(self, datas, par_id):
        new_data = {}
        for condition in datas.values():
            precond = PreferenceConditions(condition)
            item_id = self.branch_tree.insert(par_id, "end", text=precond.name, values=(precond.content))
            if condition[0] in ("anot", "onot", "and", "or"):
                new_data[item_id] = [condition[0], self._set_condition(condition[1], item_id)]
            else:
                new_data[item_id] = condition
        return new_data
    
    
    def change_node(self):
        and_or = self.and_or_com.get()
        if and_or not in ("and", "or"):
            messagebox.showerror("error" ,"「and」 or 「or」")
            return
        
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"] = [and_or, self.data[1]]
        self.need_save_lab["text"] = ""
        self.isSave = True
    
    def click_add_condition(self):
        ConditionsWindow(bg=self.con.bt.defalt_bg, bf=self)
        
    def select_condition(self, event):
        select_id = self.branch_tree.focus()
        par_id = self.branch_tree.parent(select_id)
        name = self.branch_tree.item(select_id, "text")
        data, _ = self._get_id_data(select_id, self.data[1])
        if name in ("anot", "onot", "and", "or"):
            BoolOperatorDetailWindow(bg=self.bg, bf=self, data=data, cond_id=select_id, par_id=select_id)
        else:
            ConditionDetailWindow(bg=self.bg, bf=self, data=data, cond_id=select_id, par_id=par_id)
    
    def _get_id_data(self, cond_id, datas):
        for item_id, data in datas.items():
            if item_id == cond_id:
                return data, True
            if data[0] in ("anot", "onot", "and", "or"):
                data, hasdata = self._get_id_data(cond_id, data[1])
                if hasdata:
                    return data, True
        return [], False

    def _delete_condition(self, cond_id, datas):
        new_data = {}
        for item_id, data in datas.items():
            if item_id == cond_id:
                continue
            if data[0] in ("anot", "onot", "and", "or"):
                new_data[item_id] = [data[0], self._delete_condition(cond_id, data[1])]
            else:
                new_data[item_id] = data
        
        return new_data
            
        
    def add_condition(self, data, cond_id, par_id):
        precond = PreferenceConditions(data)
        if cond_id ==  "":
            cond_id = self.branch_tree.insert(par_id, "end", text=precond.name)
        self.branch_tree.item(cond_id, values=(precond.content))
        if par_id != "":
            self.data[1] = self._set_child_data(cond_id, par_id, data, self.data[1])
        else:
            self.data[1][cond_id] = data
        self.on_change()
    
    def _set_child_data(self, cond_id, par_id, cond_data, datas):
        new_data = {}
        for item_id, data in datas.items():
            if data[0] in ("anot", "onot", "and", "or"):
                new_data[item_id] = [data[0], self._set_child_data(cond_id, par_id, cond_data, data[1])]
            else:
                new_data[item_id] = data
            if item_id == par_id:
                new_data[item_id][1][cond_id] = cond_data
        return new_data
            
            
    def add_bool_operator(self, name, par_id):
        cond_id = self.branch_tree.insert(par_id, "end", text=name)
        if par_id != "":
            self.data[1] = self._set_child_data(cond_id, par_id, [name, {}], self.data[1])
        else:
            self.data[1][cond_id] = [name, {}]
        self.on_change()
        


class BoolOperatorDetailWindow(tk.Toplevel):
    def __init__(self, bg = "", bf:BranchFrame = None, data = None, cond_id = "", par_id = "") -> None:
        super().__init__(bg=bg)
        self.bg = bg
        self.bf = bf
        self.data = data
        self.cond_id = cond_id
        self.par_id = par_id
        
        posx, posy = pyautogui.position()
        self.geometry(f"100x150+{str(posx-50)}+{str(posy-75)}")
        self.grab_set()
        
        add_btn = ttk.Button(self, text="条件の追加", style="MYStyle.TButton", command=self.click_add_btn)
        delete_btn = ttk.Button(self, text="削除", style="MYStyle.TButton", command=self.click_delete_btn)
        detail_btn = ttk.Button(self, text="詳細", style="MYStyle.TButton", command=self.click_detail_btn)
        
        add_btn.pack(pady=10)
        delete_btn.pack(pady=10)
        detail_btn.pack(pady=10)
        
    def click_add_btn(self):
        ConditionsWindow(bg=self.bg, bf=self.bf, par_id=self.par_id)
        self.destroy()
    
    def click_delete_btn(self):
        if not messagebox.askyesno("確認", "削除しますか?"):
            return
        self.bf.data[1] = self.bf._delete_condition(self.cond_id, self.bf.data[1])
        self.bf.branch_tree.delete(self.cond_id)
        self.destroy()
        self.bf.on_change()
        
    def click_detail_btn(self):
        self.destroy()
        posx, posy = pyautogui.position()
        detail_window = tk.Toplevel(bg=self.bg)
        detail_window.geometry(f"400x400+{str(posx-200)}+{str(posy-200)}")
        detail_window.grab_set()
        
        PreCondFrame(detail_window, data=self.data).pack(fill="both")
        

class ConditionDetailWindow(tk.Toplevel):
    def __init__(self, bg = "", bf:BranchFrame = None, data = None, cond_id = "", par_id = "") -> None:
        super().__init__(bg=bg)
        
        self.bg = bg
        self.bf = bf
        self.data = data
        self.cond_id = cond_id
        self.par_id = par_id
        
        posx, posy = pyautogui.position()
        self.geometry(f"100x150+{str(posx-50)}+{str(posy-75)}")
        self.grab_set()
        
        change_btn = ttk.Button(self, text="設定の変更", style="MYStyle.TButton", command=self.click_change_btn)
        delete_btn = ttk.Button(self, text="削除", style="MYStyle.TButton", command=self.click_delete_btn)
        detail_btn = ttk.Button(self, text="詳細", style="MYStyle.TButton", command=self.click_detail_btn)
        
        change_btn.pack(pady=10)
        delete_btn.pack(pady=10)
        detail_btn.pack(pady=10)
        
    def click_change_btn(self):
        SelectionWindow(self.bg, par=self.bf, name=self.data[0], cond_id=self.cond_id, par_id=self.par_id)
        self.destroy()
    
    def click_delete_btn(self):
        if not messagebox.askyesno("確認", "削除しますか?"):
            return
        self.bf.data[1] = self.bf._delete_condition(self.cond_id, self.bf.data[1])
        self.bf.branch_tree.delete(self.cond_id)
        self.destroy()
        self.bf.on_change()
        
        
    def click_detail_btn(self):
        self.destroy()
        posx, posy = pyautogui.position()
        detail_window = tk.Toplevel(bg=self.bg)
        detail_window.geometry(f"400x400+{str(posx-200)}+{str(posy-200)}")
        detail_window.grab_set()
        
        PreCondFrame(detail_window, data=self.data).pack(fill="both")



class ConditionsWindow(tk.Toplevel):
    def __init__(self, bg = "", bf = None, par_id = "") -> None:
        super().__init__(bg=bg)
        self.bg = bg
        self.selected_id = ""
        self.bf = bf
        self.par_id = par_id
        
        self.geometry("500x600+710+210")
        self.grab_set()
        
        self.conditions_tree = ttk.Treeview(self, height=12)
        self.conditions_tree.column("#0", width=500)
        self.conditions_tree.heading("#0", text="条件一覧")
        self.conditions_tree.bind("<<TreeviewSelect>>", self.select_condition)
        
        with open("conditions.json", "r", encoding="utf-8") as j:
            self.conditions = json.load(j)
        
        for group_name, group in self.conditions.items():
            parent = self.conditions_tree.insert("", "end", text=group_name)
            for condition in group:
                self.conditions_tree.insert(parent, "end", text=condition)
        
        self.add_btn = ttk.Button(self, text="追加", style="Green.TButton", command=self.click_add_btn)
        self.des_lab = ttk.Label(self, text="説明", style="Setting.TLabel")
        self.descri_lab = ttk.Label(self, text="", style="MYStyle.TLabel")
        
        self.conditions_tree.grid(row=0, column=0, columnspan=3)
        self.des_lab.grid(row=1, column=0, columnspan=3)
        self.descri_lab.grid(row=2, column=0, columnspan=3)
        self.add_btn.grid(row=3, column=2)
    
    def select_condition(self, event):
        select_id = self.conditions_tree.focus()
        parent = self.conditions_tree.parent(select_id)
        
        if parent == "":
            return
        
        self.selected_id = select_id
        
        par_text = self.conditions_tree.item(parent, "text")
        text = self.conditions_tree.item(select_id, "text")
        
        self.descri_lab["text"] = self.conditions[par_text][text]
    
    def click_add_btn(self):
        if self.selected_id == "":
            messagebox.showerror("エラー", "条件が選択されていません")
            return
        
        name = self.conditions_tree.item(self.selected_id, "text")
        
        if name in ("anot", "onot", "and", "or"):
            self.bf.add_bool_operator(name, self.par_id)
            self.destroy()
            return
        
        SelectionWindow(bg=self.bg, par=self, name=name, par_id=self.par_id)
    
    def next_frame(self, old_frame, new_frame):
        old_frame.destroy()
        new_frame.grid(row=0, column=0, sticky=tk.NSEW)
    
    def add_condition(self, data, cond_id, par_id):
        self.bf.add_condition(data, cond_id, par_id)
        self.destroy()
        
        

class SelectionWindow(tk.Toplevel):
    def __init__(self, bg = "", par = None, name = "", cond_id = "", par_id = "") -> None:
        super().__init__(bg=bg)
        
        self.par = par
        self.bg = bg
        self.cond_id = cond_id
        self.par_id = par_id
        
        self.geometry("420x600+750+210")
        self.grab_set()
        
        frame = self.create_selection_frame(self, name)
        frame.grid(row=0, column=0, sticky=tk.NSEW)
    
    def add_condition(self, data, cond_id, par_id):
        self.par.add_condition(data, cond_id, par_id)
        self.destroy()
        
    def next_frame(self, old_frame, new_frame):
        old_frame.destroy()
        new_frame.grid(row=0, column=0, sticky=tk.NSEW)
    
    def create_selection_frame(self, master, name):
        if name == "ユーザー名":
            return UserNameFrameFirst(master, self.bg, data=[name, 0, 0, "", ""], sw=self, cond_id=self.cond_id, par_id=self.par_id)
        return ttk.Frame(master, style="MYStyle.TFrame")


class SelectionFrame(ttk.Frame):
    def __init__(self, master = None, bg = "", data = None, sw:SelectionWindow = None, values = {}, title = "", cond_id = "", par_id = "") -> None:
        super().__init__(master, style="MYStyle.TFrame")
        
        self.selection_win = master
        self.data = data
        self.sw = sw
        self.bg = bg
        self.title = title
        self.values = values
        self.cond_id = cond_id
        self.par_id = par_id
        
        self.title_lab = ttk.Label(self, text=self.title, style="Setting.TLabel")
        self.check_list = NCheckList(self, values=self.values, isOnly=True, bg=self.bg)
        self.ok_btn = ttk.Button(self, text="OK", command=self.click_ok_btn, style="Green.TButton")
        
        self.title_lab.grid(row=0, column=0)
        self.check_list.grid(row=1, column=0)
        self.ok_btn.grid(row=2, column=0, sticky="e")
        
    def click_ok_btn(self):
        return

class UserNameFrameFirst(SelectionFrame):
    
    pre_conds = {"コマンドを打ったユーザー": False, "idで指定したユーザー": True}
    
    def __init__(self, master = None, bg = "", data = None, sw = None, cond_id = "", par_id = "") -> None:
        super().__init__(master, bg, data, sw, self.pre_conds, "ユーザーを選択", cond_id, par_id)

    def click_ok_btn(self):
        index = self.check_list.index
        ent_check_box:NEntryCheckBox = self.check_list.check_boxes[index]
        if ent_check_box.hasEntry:
            ent_text = ent_check_box.entry.get()
            if ent_text == "":
                messagebox.showerror("エラー", "空白です")
                return
            self.data[3] = ent_text
        self.data[1] = index
        self.sw.next_frame(self, UserNameFrameLast(self.selection_win, bg=self.bg, data=self.data, sw=self.sw, cond_id=self.cond_id, par_id=self.par_id))

class UserNameFrameLast(SelectionFrame):
    
    pre_conds = {"コマンドを打ったユーザー": False, "idで指定したユーザー": True, "ユーザー名入力": True}
    
    def __init__(self, master = None, bg = "", data = None, sw = None, cond_id = "", par_id = "") -> None:
        super().__init__(master, bg, data, sw, self.pre_conds, "ユーザー名選択", cond_id, par_id)

    def click_ok_btn(self):
        index = self.check_list.index
        ent_check_box:NEntryCheckBox = self.check_list.check_boxes[index]
        if ent_check_box.hasEntry:
            ent_text = ent_check_box.entry.get()
            if ent_text == "":
                messagebox.showerror("エラー", "空白です")
                return
            self.data[4] = ent_text
        self.data[2] = index
        self.sw.add_condition(self.data, self.cond_id, self.par_id)
        self.destroy()
        
        
class PreCondFrame(ttk.Frame):
    
    def __init__(self, master = None, data = []) -> None:
        super().__init__(master, style="MYStyle.TFrame")
        precond = PreferenceConditions(data)
        self.info = precond.detail
        self.name = data[0]

        for title, descri in self.info.items():
            title_label = ttk.Label(self, text=title, style="Setting.TLabel")
            descri_label = ttk.Label(self, text=descri, style="MYStyle.TLabel")
            title_label.pack()
            descri_label.pack()

class PreferenceConditions():
     def __init__(self, data = []) -> None:
        self.detail = {}
        self.content = ""
        self.name = data[0]
        if self.name == "ユーザー名":
            self.detail["説明"] = "[ユーザー1]と[ユーザー2]の名前が一致したらTrueを返す\n"
            user1 = list(UserNameFrameFirst.pre_conds.keys())[data[1]]
            self.content += user1 + "=="
            if data[3] != "":
                user1 = user1 + "\n入力: " + data[3]
            self.detail["ユーザー1"] = user1  +"\n"
            user2 = list(UserNameFrameLast.pre_conds.keys())[data[2]]
            self.content += user2
            if data[4] != "":
                user2 = user2 + "\n入力: " + data[4]
            self.detail["ユーザー2"] = user2  +"\n"
        
"""
    VarBranchFrameの説明

    一時的に脳死で作ったから適当
    
    todo:
        条件一覧とか作って使いやすくする
        マクロノイド観たいにする
    
    botの処理は作ってない
"""     
"""class VarBranchFrame(NodeDetail):
    
    com_opes = {"と等しい": 0, "と異なる": 1, "よりも小さい": 2, "よりも大きい": 3, "以下である": 4, "以上である": 5, "含まれる": 6, "含まれない": 7}
    
    def __init__(self, master = None, command_frame = None,command_name = "", node_id = "", data = [""]):
        super().__init__(master, command_frame, command_name, node_id, data)
        
        if not any(self.data):
            self.data = ["", "", 0]
        
        compre_strs = [comope_str for comope_str in self.com_opes]
        com_ope = compre_strs[self.data[2]]
        
        self.a_val_ent = NEntry(self, width=30, text=self.data[0])
        self.ga_lab = ttk.Label(self, text="が", style="MYStyle.TLabel")
        self.b_val_ent = NEntry(self, width=30, text=self.data[1])
        
        self.com_ope_lab = NLable(self, text="条件", style="MYStyle.TLabel")
        self.com_ope_com = NCombobox(self, values=compre_strs, text=com_ope)
        
        
        self.a_val_ent.bind("<<ChangeText>>", self.on_change)
        self.b_val_ent.bind("<<ChangeText>>", self.on_change)
        self.com_ope_com.bind("<<ChangeText>>", self.on_change)
        
        self.need_save_lab.grid(row=0, column=0)
        self.a_val_ent.grid(row=2, column=0)
        self.option_btn(self.a_val_ent).grid(row=2, column=1)
        
        self.ga_lab.grid(row=2, column=2)
        
        self.b_val_ent.grid(row=2, column=3)
        self.option_btn(self.b_val_ent).grid(row=2, column=4)
        
        self.com_ope_lab.grid(row=1, column=5)
        self.com_ope_com.grid(row=2, column=5)
        
        self.change_btn.grid(row=3, column=0, columnspan=6)
        self.delete_btn.grid(row=4, column=0, columnspan=6)
        
    
    def change_node(self):
        if not messagebox.askyesno("確認", "変更を保存しますか？"):
            return
        a_val = self.a_val_ent.get()
        b_val = self.b_val_ent.get()
        com_ope = self.com_ope_com.get()
        
        if com_ope not in self.com_opes:
            messagebox.showerror("エラー", "条件が間違っています")
            return
        
        com_ope = self.com_opes[com_ope]
        
        self.command_tree.item(self.node_id, tags="")
        self.command_frame.commands[self.command_name]["nodes"][self.node_id]["data"] = [a_val, b_val, com_ope]
        self.need_save_lab["text"] = ""
        self.isSave = True"""