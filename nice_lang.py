#!/usr/bin/env python3

LIST_START = '['
LIST_END = ']'

#TUPLE_START = '{'
#TUPLE_END = '}'

class Ram:
    #RETURN_VALUE_VAR = 'RET'
    ANON_VAR_FORMAT = '___anon_var_{num}___'
    ANON_VAR_LNUM = float('-inf')
    def __init__(s):
        s.names = []
        s.values = []
        s.lnums = []
        s.anon_var_ind = 0
    def set_anon_var(s, value):# add lnum as an argument ?
        name = s.ANON_VAR_FORMAT.format(num=s.anon_var_ind)
        s.anon_var_ind += 1
        s.create_var(name, value, s.ANON_VAR_LNUM)
        return name

    def create_var(s, name, value, lnum):
        assert name not in s.names
        s.names.append(name)
        s.values.append(value)
        s.lnums.append(lnum)
        #print(f'created var "{name}" with value "{value}"')
    def set_var(s, name, value, lnum):
        assert name in s.names
        ind = s.names.index(name)
        s.values[ind] = value
        s.lnums[ind] = lnum
        #print(f'modified var "{name}" with new value "{value}"')

    def var_exists(s, name):
        return name in s.names
    def get_var(s, name):
        assert s.var_exists(name)
        ind = s.names.index(name)
        return s.values[ind], s.lnums[ind]


def get_till_end_of_str(code, lnum, end):
    assert end != '\n'# implement correct behaviour in this case
    assert len(end) == 1# implement correct behaviour in this case
    new = ''
    while code:
        c = code[0]
        code = code[1:]

        if c == '\n':
            lnum += 1
        
        if c == end:
            return code,lnum,new
        elif c == '\\':
            assert len(code)
            c2 = code[0]
            code = code[1:]
            if c2 == '\\':
                new += '\\'
            elif c2 == 'n':
                new += '\n'
            elif c2 == 't':
                new += '\t'
            elif c2 == "'":
                new += "'"
            elif c2 == '"':
                new += '"'
            else:
                assert not f'unknown \\ partnet: {c2}'
        else:
            new += c
    assert not f'start start found, but str end not found: {end}'# implement error mechanism      
def parse_str(code, ram, lnum_offset=1):
    IGNORED_SEPARATORS = [' ', '\t', ',', '\n']
    KEPT_SEPARATORS = [LIST_START, LIST_END]
    STRING_SEPARATORS = ["'", '"']
    SEPARATORS = IGNORED_SEPARATORS + KEPT_SEPARATORS + STRING_SEPARATORS

    parsed = []
    lnums = []
    lnum = lnum_offset
    while code:
        closest_dist = -1
        closest_sep = ''
        for sep in SEPARATORS:
            if sep in code:
                ind = code.index(sep)
                if (closest_dist == -1) or (ind < closest_dist):
                    closest_dist = ind
                    closest_sep = sep

        if closest_dist == -1:
            parsed.append(code)
            lnums.append(lnum)
            code = ''
            break
        else:
            ind = closest_dist
            sep = closest_sep

            block = code[:ind]
            code = code[ind+len(sep):]
            
            parsed.append(block)
            lnums.append(lnum)
            if sep == '\n':
                lnum += 1
            if sep in IGNORED_SEPARATORS:
                pass
            elif sep in KEPT_SEPARATORS:
                parsed.append(sep)
                lnums.append(lnum)
            elif sep in STRING_SEPARATORS:
                code,lnum,str_ = get_till_end_of_str(code,lnum,sep)
                new = ram.set_anon_var(str_)
                parsed.append(new)
                lnums.append(lnum)
            else:
                assert not f'forgot to add a case for a separator type: {sep=}'

    while '' in parsed:
        ind = parsed.index('')
        del parsed[ind]
        del lnums[ind]

    for ind, atom in enumerate(parsed):
        try:
            int_ = int(atom)
        except ValueError:
            try:
                float_ = float(atom)
            except ValueError:
                pass
            else:
                new = ram.set_anon_var(float_)
                parsed[ind] = new
        else:
            new = ram.set_anon_var(int_)
            parsed[ind] = new
    
    return parsed,lnums

def pop_from_code(code, lnums, ram):
    atom = code.pop(0)
    atoml = lnums.pop(0)
    #print(f'popped: {atoml}: {atom}')
    if atom == LIST_START:
        #raise AssertionError(f'{atoml}: lists are not yet implemented')
        list_ = []
        while code:
            item,iteml = pop_from_code(code, lnums, ram)
            if item == LIST_END:
                break
            else:
                item,iteml = ram.get_var(item)
                list_.append(item)
        else:
            raise AssertionError(f'{atoml}: list has no end')
        return ram.set_anon_var(list_), atoml
    else:
        return atom, atoml
def run_str(code, ram_constructor=Ram, lnum_offset=1):
    ram = ram_constructor()

    code,lnums = parse_str(code, ram, lnum_offset)
    assert len(code) == len(lnums)
    '''
    if len(lnums):
        spaces = len(str(lnums[-1]))
    for lnum,token in zip(lnums,code):
        print('%{spaces}d %s'.format(spaces=spaces)%(lnum,token))
    '''
    while code:
        f,fl = pop_from_code(code, lnums, ram)
        if not code:
            assert not f'{fl}: wtf do you want me to do with a single variable: {f}'
        else:
            s,sl = pop_from_code(code, lnums, ram)
            if s == '-=>':
                if not code:
                    assert not f'{sl}: {s} (creating variables) requires 1 more argument'
                t,tl = pop_from_code(code, lnums, ram)
                tv,tvl = ram.get_var(t)
                if ram.var_exists(f):
                    assert not f'{fl,sl}: variable already exists: {fl}'
                ram.create_var(f, tv, tl)
            elif s == '=':
                if not code:
                    assert not f'{sl}: {s} (modifying variables) requires 1 more argument'
                t,tl = pop_from_code(code, lnums, ram)
                tv,tvl = ram.get_var(t)
                if not ram.var_exists(f):
                    raise AssertionError(f'{fl,sl}: variable doesn\'t exist: {f}')
                ram.set_var(f, tv, tl)
            elif s == '<>':
                if f == 'echo':
                    t,tl = pop_from_code(code, lnums, ram)
                    tv,tvl = ram.get_var(t)
                    print(tv, end='')
                else:
                    raise AssertionError(f'{fl,sl}: unknown built-in function: {f}')
            else:
                if not ram.var_exists(s):
                    raise AssertionError(f'{sl}: variable doesn\'t exist: {s}')
                sv,svl = ram.get_var(s)
                if type(sv) == list:
                    fnc,fncl = ram.get_var(f)
                    #print(f'{fncl=}')
                    assert len(fnc) == 2
                    args,body = fnc
                    assert type(args) == list
                    assert type(body) == str
                    assert len(args) == len(sv)
                    #print(f'{args=}')
                    new_ram = Ram()
                    for name,value in zip(args,sv):
                        new_ram.create_var(name, value, svl)
                    run_str(body, lambda:new_ram, fncl)
                else:
                    raise AssertionError(f'{fl,sl}: bad syntax: {f} {s}:{sv}')
    
 
def run_file(name):
    with open(name) as f:
        cont = f.read()
    return run_str(cont)


run_file('test1.nl')

# TODO: give every assert a line number and info
# TODO: implement callback stack
