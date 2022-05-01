
from discord.ext import commands
from tkinter import ttk
import discord
import tkinter as tk
import threading
import asyncio
import time
import tc
import yaml
import json
import conv

class BotConsole(tk.Tk):
    
    def __init__(self) -> None:
        super().__init__()
        
        
        
        self.stop_btn= ttk.Button(self, text="終了", command=self.stop, width = 20,padding=20)
        
        self.load_btn= ttk.Button(self, text="読み込み", command=self.load_file, width = 20,padding=20)
        
        self.log_box = tk.Listbox(self, bg="gray5", fg="white", width=80, height=23, font= ("UD デジタル 教科書体 NP-R", "16", "normal"))

        self.scroll=tk.Scrollbar(self, width=20, command=self.log_box.yview)
        
        self.scroll.grid(row=1 , column=30, sticky=(tk.N, tk.S))
        self.stop_btn.grid(row=0, column=0)
        self.load_btn.grid(row=0, column=1)
        self.log_box.grid(row=1, column=0, columnspan= 30)
        
        self.load_file()
        
        self.bot = commands.Bot(command_prefix=self.prefix)
        self.bot_cog = BotCog(self.bot, self)
        
    def stop(self):
        self.bot_cog.isStop = True
        self.destroy()

    def load_file(self):
        with open("./config.yml", "r") as yml:
            config = yaml.safe_load(yml)
            
        self.file_name = config["open_file_name"]
        
        with open(f"./data/{self.file_name}.json", "r", encoding="utf-8") as j:
            self.file = json.load(j)
            
        self.prefix = self.file["prefix"]
        self.token = self.file["token"]
        self.command_names = [key for key in  self.file["commands"].keys()]
        self.vars = self._file_to_var(self.file["vars"])
          
        self.log_box.insert("end", "読み込み完了!!!")
    
    def _file_to_var(self, file):
        vars = {}
        for name, data in file.items():
            type = data[0]
            val = data[1]
            vars[name] = tc.type_change(type, val)
        return vars
        
        
    def bot_run(self):
        thread = threading.Thread(target=self._run)
        thread.start()    
    
    def _run(self):
        self.bot.add_cog(self.bot_cog)
        self.bot.run(self.token)
        

class BotCog(commands.Cog):
    
    def __init__(self, bot, con: BotConsole = None) -> None:
        self.bot: commands.Bot  = bot
        self.con = con
        self.isStop = False
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        message_prefix = message.content[0:len(self.con.prefix)]
        
        if message_prefix != self.con.prefix:
            return
        
        args = message.content[len(self.con.prefix)::].split(" ")
        
        command_name = args[0]
        
        if command_name not in self.con.command_names:
            return
        
        args.pop(0)
        
        rc = RunCommand(self.con, message, self.con.file["commands"][command_name], args)
        await rc.run()
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if ctx.invoked_with in self.con.command_names:
            return
        self.con.log_box.insert("end", error)
                
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.con.log_box.insert("end", "起動しました")
        while True:
            await asyncio.sleep(1)
            if not self.isStop:
                continue
            await self.bot.close()
            time.sleep(1)
            print("終了")

class RunCommand():
    
    def __init__(self, con: BotConsole, message: discord.Message, datas, args) -> None:
        self.con = con
        self.message = message
        self.datas = datas
        self.args = args
    
    def create_options(self):
        options = {}
        options["vars"] = self.con.vars
        options["message"] = self.message
        
        return options
        
        
    async def run(self):
        for data in self.datas.values():
            await self.process_start(data)
        
    async def process_start(self, data):
        node_name = data[0]
        child_datas = data[1]
        node_data = data[2]
        
        if node_name == "ログ表示":
            await self.print_process(node_data)
        if node_name == "メッセージを送る":
            await self.send_message_process(node_data)
            
        for child_data in child_datas.values():
            await self.process_start(child_data)
        
    async def print_process(self, data):
        msg = conv.conversion(data[0], self.create_options())
        self.con.log_box.insert("end", msg)
    
    async def send_message_process(self, data):
        msg = conv.conversion(data[0], self.create_options())
        
        if data[1] == 0:
            await self.message.channel.send(msg)
        if data[1] == 1:
            await self.message.author.send(msg)
        


if __name__ == "__main__":
    app = BotConsole()
    
    app.bot_run()
    app.mainloop()
    app.bot_cog.isStop = True