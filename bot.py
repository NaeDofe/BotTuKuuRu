from discord.ext import commands
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from decimal import Decimal
import discord
import tkinter as tk
import threading
import asyncio
import time
import tc
import yaml
import json
import conv
import datetime

class LogBox(ScrolledText):
    def __init__(self, master = None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.tag_config('error', foreground='red')
    
    def linsert(self, index, chars, *args):
        self.insert(index,chars+"\n", args)
        self.see("end")
        

class BotConsole(tk.Tk):
    
    def __init__(self) -> None:
        super().__init__()
        
        self.stop_btn= ttk.Button(self, text="終了", command=self.stop, width = 20,padding=20)
        
        self.load_btn= ttk.Button(self, text="読み込み", command=self.load_file, width = 20,padding=20)
        
        self.log_box = LogBox(self, bg="gray5", fg="white", width=80, height=23, font= ("Yu Gothic UI Semibold", "16", "normal"))
        
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
          
        self.log_box.linsert("end", "読み込み完了!!!")
    
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
        try:
            self.bot.run(self.token)
        except:
            self.log_box.linsert("end", "TOKENが間違っています", "error")
            self.log_box.linsert("end", "起動できませんでした", "error")
            

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
        
        rc = RunCommand(self.bot, self.con, message, self.con.file["commands"][command_name], args)
        await rc.run()
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if ctx.invoked_with in self.con.command_names:
            return
        self.con.log_box.linsert("end", str(error))
                
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.con.log_box.linsert("end", "起動しました")
        
    @commands.Cog.listener()
    async def on_connect(self):
        while True:
            await asyncio.sleep(1)
            if not self.isStop:
                continue
            await self.bot.close()
            time.sleep(1)
            print("終了")
        

class RunCommand():
    
    def __init__(self, bot:commands.Bot, con: BotConsole, message: discord.Message, datas, args) -> None:
        self.bot = bot
        self.con = con
        self.message = message
        self.datas = datas
        self.args = args
    
    def create_options(self):
        options = {}
        options["vars"] = self.con.vars
        options["message"] = self.message
        options["times"] = self._get_time()
        
        return options
    
    def _get_time(self):
        times = {}
        now = datetime.datetime.now()
        times["year"] = now.year
        times["month"] = now.month
        times["day"] = now.day
        times["dow"] = conv.en_to_ja(now.strftime('%a'))
        times["hour"] = now.hour
        times["minute"] = now.minute
        times["second"] = now.second
        
        return times

        
    async def run(self):
        can_branch = False
        for data in self.datas.values():
            canSuccess, can_branch = await self.process_start(data, can_branch)
            if not canSuccess:
                return
        
    async def process_start(self, data, can_branch):
        node_name = data[0]
        child_datas = data[1]
        node_data = data[2]
        
        canSuccess = True
        can_child_process = True
        
        if node_name == "ログ表示":
            canSuccess = await self.print_process(node_data)
        if node_name == "メッセージを送る":
            canSuccess = await self.send_message_process(node_data)
        if node_name == "変数の設定":
            canSuccess = await self.var_setting_process(node_data)
        
        if node_name == "条件分岐":
            can_child_process = await self.branch_process(node_data[1], node_data[0])
            can_branch = False if can_child_process else True
        elif node_name == "Else If":
            if can_branch:
                can_child_process = await self.branch_process(node_data[1], node_data[0])
                if can_child_process:
                    can_branch = False
            else:
                can_child_process = False
        elif node_name == "Else":
            if not can_branch:
                can_child_process = False
        else:
            can_branch = False
        
        if not canSuccess:
            self.con.log_box.linsert("end","コマンドを終了しました", "error")
            return False, False
        if can_child_process:
            child_can_branch = False
            for child_data in child_datas.values():
                canSuccess, child_can_branch = await self.process_start(child_data, child_can_branch)
                if not canSuccess:
                    return False, False
        
        return True, can_branch
        
    async def print_process(self, data):
        msg = conv.conversion(data[0], self.create_options())
        self.con.log_box.linsert("end", msg)
        return True
    
    async def send_message_process(self, data):
        msg = conv.conversion(data[0], self.create_options())
        
        if data[1] == 0:
            await self.message.channel.send(msg)
        if data[1] == 1:
            await self.message.author.send(msg)
        return True
    
    async def var_setting_process(self, data):
        var = self.con.vars[data[0]]
        val = data[1][0]
        if type(var) is int:
            val = conv.conversion(val, self.create_options())
            val, isFormula = conv.calculation(val)
            if not isFormula:
                self.con.log_box.linsert("end","値がintではありません。", "error")
                return False
            if data[1][1] == 0:
                var += val
            if data[1][1] == 1:
                var = val
        elif type(var) is float:
            val = conv.conversion(val, self.create_options())
            isRightness = tc.type_change("bool", data[1][2])
            val, isFormula = conv.calculation(val, "float", isRightness)
            if not isFormula:
                self.con.log_box.linsert("end","値がfloatではありません。", "error")
                return False
            if data[1][1] == 0:
                if isRightness:
                    var = float(Decimal(str(var)) + Decimal(str(val)))
                else:
                    var += val
            if data[1][1] == 1:
                var = val
        elif type(var) is str:
            val = conv.conversion(val, self.create_options())
            if data[1][1] == 0:
                var += val
            if data[1][1] == 1:
                var = val
        elif type(var) is bool:
            if data[1][1] == 0:
                var = True
            if data[1][1] == 1:
                var = False
            if data[1][1] == 2:
                var = not var
            if data[1][1] == 3:
                val = self.con.vars[val]
                if type(val) is not bool:
                    self.con.log_box.linsert("end","値がboolではありません。", "error")
                    return False
                var = val
        self.con.vars[data[0]] = var
        return True
    
    async def branch_process(self, datas, bool_operator):
        results = []
        for data in datas.values():
            if data[0] == "ユーザー名":
                user_name1 = ""
                if data[1] == 0:
                    user_name1 = self.message.author.name
                elif data[1] == 1:
                    try:
                        user1 = await self.bot.fetch_user(int(data[3]))
                    except:
                        self.con.log_box.linsert("end","UserIdが間違っています", "error")
                        results.append(False)
                        continue
                    user_name1 = user1.name
                user_name2 = ""
                if data[2] == 0:
                    user_name2 = self.message.author.name
                elif data[2] == 1:
                    try:
                        user2 = await self.bot.fetch_user(int(data[4]))
                    except:
                        self.con.log_box.linsert("end","UserIdが間違っています", "error")
                        results.append(False)
                        continue
                    user_name2 = user2.name
                elif data[2] == 2:
                    user_name2 = data[4]
                results.append(True) if user_name1 == user_name2 else results.append(False)
            
            if data[0] in ("anot", "onot", "and", "or"):
                results.append(await self.branch_process(data[1], data[0]))
        
        if bool_operator == "and":
            return all(results)
        if bool_operator == "or":
            return any(results)
        if bool_operator == "anot":
            return all([not val for val in results])
        if bool_operator == "onot":
            return any([not val for val in results])
        return False
                


if __name__ == "__main__":
    app = BotConsole()
    app.bot_run()
    app.mainloop()
    app.bot_cog.isStop = True