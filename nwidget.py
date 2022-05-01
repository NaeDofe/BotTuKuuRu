from tkinter import ttk
import tkinter as tk


class NButton(ttk.Frame):
    def __init__(self, master, text = "", width = None, height = None, command = None, style=None):
        super().__init__(master=master, width=width, height=height)
        
        self.pack_propagate(0)
        self._btn = ttk.Button(self, text=text, command=command, style=style)
        self._btn.pack(fill=tk.BOTH, expand=1)
        

class NEntry(ttk.Entry):
    
    def __init__(self, master = None, width = None, text = None, state="") -> None:
        super().__init__(master=master, width=width, state=state)
        
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

class NCheckList(ttk.Frame):
    def __init__(self, master, bg = "", width = 400, height=400, values = {}, isOnly = False) -> None:
        super().__init__(master, style="MYStyle.TFrame")
        
        self.values = values
        self.isOnly = isOnly
        self.index = 0
        
        if type(self.values) == list:
            self.values = {valu: False for valu in self.values}
        
        self.canvas = tk.Canvas(self, width=width, height=height, 
                                bg=bg, highlightthickness=0)
        self._frame = ttk.Frame(self.canvas, style="MYStyle.TFrame")
        
        self.booleanvars = []
        self.check_boxes = []
        for i, (val, hasEntry) in enumerate(self.values.items()):
            booleanvar = tk.BooleanVar()
            check_box = NEntryCheckBox(
                            self._frame, text=val, 
                            variable=booleanvar, index=i,
                            command=self.click_check_btn,
                            hasEntry=hasEntry,
                            mcl=self)
            check_box.grid(row=i, column=0, sticky="w")
            self.check_boxes.append(check_box)
            self.booleanvars.append(booleanvar)
        
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.create_window(0, 0, window=self._frame)
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"), 
                           yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind("<MouseWheel>", self._mouse_scroll_y)
        self._frame.bind("<MouseWheel>", self._mouse_scroll_y)
        
        self.canvas.grid(row=0, column=0)
        self.scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        
    def click_check_btn(self, index):
        self.index = index
        if not self.isOnly:
            return
        
        for boolean in self.booleanvars:
            boolean.set(False)
        self.booleanvars[self.index].set(True)
    
    def _mouse_scroll_y(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')


class NEntryCheckBox(ttk.Frame):
    def __init__(self, master, text = "", variable = None, index = 0, command = None, hasEntry = False, mcl = None) -> None:
        super().__init__(master, style="MYStyle.TFrame")
        self.text = text
        self.index = index
        self.command = command
        self.hasEntry = hasEntry
        self._mcl = mcl
        
        self.check_box = ttk.Checkbutton(self, text=text, variable=variable, style="Option.TCheckbutton", command=self.click_check_btn)
        self.check_box.grid(row=0, column=0, sticky="w")
        
        self.bind("<MouseWheel>", self._mcl._mouse_scroll_y)
        self.check_box.bind("<MouseWheel>", self._mcl._mouse_scroll_y)
        
        if not self.hasEntry:
            return
        self.entry = ttk.Entry(self)
        self.entry.grid(row=1, column=0, padx=(20, 0), sticky="w")
        
        self.entry.bind("<MouseWheel>", self._mcl._mouse_scroll_y)
        
    def click_check_btn(self):
        if self.command is None:
            return
        self.command(self.index)