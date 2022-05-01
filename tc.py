

def type_change(type, val):
    try:
        if type == "str":
            return val
        if type == "int":
            return int(val)
        if type == "float":
            return float(val)
        if type == "bool":
            return True if val in ["True","true"] else False
        if type == "list":
            return eval(val)
        if type == "dict":
            return eval(val)
    except:
        return None
    return None

def type_check(type, val):
    if type == "str":
        return is_str(val)
    if type == "int":
        return is_int(val)
    if type == "float":
        return is_float(val)
    if type == "bool":
        return is_bool(val)
    if type == "list":
        return is_list(val)
    if type == "dict":
        return is_dict(val)
    return False

def comp_check(comp, val1, val2):
    if comp == "==":
        return val1 == val2
    elif comp == "!=":
        return val1 != val2
    elif comp == ">":
        return val1 > val2
    elif comp == ">=":
        return val1 >= val2
    elif comp == "<":
        return val1 < val2
    elif comp == "<=":
        return val1 <= val2
    elif comp == "is":
        return val1 is val2
    elif comp == "is not":
        return val1 is not val2
    elif comp == "in":
        return val1 in val2
    elif comp == "not in":
        return val1 not in val2

def ass(ass, val1, val2):
    if ass == "=":
        val1 = val2
    elif ass == "+=":
        val1 += val2
    elif ass == "-=":
        val1 -= val2
    elif ass == "*=":
        val1 *= val2
    elif ass == "/=":
        val1 /= val2
    elif ass == "//=":
        val1 //= val2
    elif ass == "%=":
        val1 %= val2
    elif ass == ">>=":
        val1 >>= val2
    elif ass == "<<=":
        val1 <<= val2
    elif ass == "&=":
        val1 &= val2
    elif ass == "^=":
        val1 ^= val2
    elif ass == "|=":
        val1 |= val2
        
    return val1

def is_str(val):
    return type(val) == str

def is_int(val):
    if type(val) == int:
        return True
    try:
        int(val, 10)
    except:
        return False
    else:
        return True

def is_float(val):
    if type(val) == float:
        return True
    try:
        float(val)
        return True
    except:
        return False

def is_bool(val):
    return val in ["True","true","False","false"]

def is_list(val):
    if type(val) == list:
        return True
    try:
        lis=eval(val)
    except:
        return False
    else:
        return type(lis) == list

def is_dict(val):
    if type(val) == dict:
        return True
    try:
        dic=eval(val)
    except:
        return False
    else:
        return type(dic) == dict