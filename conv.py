from decimal import Decimal
from fractions import Fraction
import discord
import tc

def conversion(msg, options):
    new_msg = ""
    hasStart = False
    start_index = 0
    for index, char in enumerate(msg):
        if char == "[":
            hasStart = True
            start_index = index+1
        elif char == "]" and hasStart:
            hasStart = False
            new_msg += _option_conv(msg[start_index:index], options)
        elif not hasStart:
            new_msg += char
    return new_msg

def _option_conv(option, options):
    option_name = option.split("=")[0]
    val = option.split("=")[1]
    if option_name == "a":
        val = _val_to_variable(val, options["args"])
    if option_name == "vg":
        val = _val_to_variable(val, options["vars"])
    if option_name == "vl":
        val = _val_to_variable(val, options["local_vars"])
    if option_name == "m":
        val = _val_to_message(val, options["message"])
    if option_name == "t":
        val = _val_to_time(val, options["times"])
    
    return val

def _val_to_time(val, times):
    if val == "year":
        return str(times["year"])
    if val == "month":
        return str(times["month"])
    if val == "day":
        return str(times["day"])
    if val == "dow":
        return str(times["dow"])
    if val == "hour":
        return str(times["hour"])
    if val == "minute":
        return str(times["minute"])
    if val == "second":
        return str(times["second"])


def _val_to_message(val, message: discord.Message):
    if val == "content":
        return message.content
    if val == "user_name":
        return message.author.display_name
    if val == "user_id":
        return str(message.author.id)
    if val == "channel_name":
        return message.channel.name
    if val == "channel_id":
        return str(message.channel.id)
    if val == "server_name":
        return message.guild.name
    if val == "server_id":
        return str(message.guild.id)
    pass
    
def _val_to_variable(var_name, vars):
    for name, data in vars.items():
        if var_name == name:
            return str(data)
    return var_name

def get_var_type(msg, vars):
    types = []
    hasStart = False
    start_index = 0
    for index, char in enumerate(msg):
        if char == "[":
            hasStart = True
            start_index = index+1
        elif char == "]" and hasStart:
            hasStart = False
            types.append(_option_to_type(msg[start_index:index], vars)) 
    return types

def _option_to_type(option, vars):
    option_name = option.split("=")[0]
    var_name = option.split("=")[1]
    type = ""
    if option_name in ("vg", "vl"):
        type = vars[var_name]["type"]
    if option_name == "t":
        if var_name == "dow":
            return "str"
        type = "int"
    return type

def odm(msg):
    new_msg = """"""
    hasStart = False
    for char in msg:
        if char == "[":
            hasStart = True
        elif char == "]" and hasStart:
            hasStart = False
        elif char in ["+","-","/","*"]:
            continue
        elif not hasStart:
            new_msg += char
    return new_msg

def calculation(msg, cls = "int", isRightness = False):
    formula = []
    num = ""
    for char in msg:
        if char in ["+", "-", "*", "/"]:
            if not tc.type_check(cls, num):
                return msg, False
            formula.append(float(num))
            formula.append(char)
            num = ""
        else:
            num += char
    if not tc.type_check(cls, num):
        return msg, False
    formula.append(float(num))
    _formula = formula.copy()
    minus = 0
    for i, val in enumerate(_formula):
        i -= minus
        if val == "*":
            if isRightness:
                formula[i-1] = float(Decimal(str(formula[i-1])) * Decimal(str(formula[i+1])))
            else: 
                formula[i-1] *= formula[i+1]
            formula.pop(i)
            formula.pop(i)
            minus += 2
        if val == "/":
            if isRightness:
                formula[i-1] = float(Fraction(str(formula[i-1])) * Fraction(str(formula[i+1])))
            else:
                formula[i-1] /= formula[i+1]
            formula.pop(i)
            formula.pop(i)
            minus += 2
    _formula = formula.copy()
    minus = 0
    for i, val in enumerate(_formula):
        i -= minus
        if val == "+":
            if isRightness:
                formula[i-1] = float(Decimal(str(formula[i-1])) + Decimal(str(formula[i+1])))
            else: 
                formula[i-1] += formula[i+1]
            formula.pop(i)
            formula.pop(i)
            minus += 2
        if val == "-":
            if isRightness:
                formula[i-1] = float(Decimal(str(formula[i-1])) - Decimal(str(formula[i+1])))
            else: 
                formula[i-1] -= formula[i+1]
            formula.pop(i)
            formula.pop(i)
            minus += 2
    rezult = formula[0]
    if cls == "int":
        rezult = round(rezult)
    return rezult, True
        

def all(lis, val):
    allVal = True
    for l in lis:
        if val != l:
            allVal = False
    return allVal

def en_to_ja(en):
        ja = ""
        if en == "Mon":
            ja = "月"
        if en == "Tue":
            ja = "火"
        if en == "Wed":
            ja = "水"
        if en == "Thu":
            ja = "木"
        if en == "Fri":
            ja = "金"
        if en == "Sat":
            ja = "土"
        if en == "Sun":
            ja = "日"
        return ja

