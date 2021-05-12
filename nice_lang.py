#!/usr/bin/env python3

class Ram:
    RETURN_VALUE_VAR = 'RET'
    ANON_VAR_FORMAT = '___anon_var_{num}___'
    def __init__(s):
        s.names = []
        s.values = []
        s.anon_var_ind = 0
    def set_anon_var(s, value):
        name = s.ANON_VAR_FORMAT.format(num=s.anon_var_ind)
        s.anon_var_ind += 1
        s.create_var(name, value)
        return name

    def create_var(s, name, value):
        assert name not in s.names
        s.names.append(name)
        s.values.append(value)
    def set_var(s, name, value):
        assert name in s.names
        ind = s.names.index(s.name)
        s.values[ind] = value
        


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
            else:
                assert False
        else:
            new += c
    assert False# implement error mechanism      
def parse_str(code, ram):
    LIST_START = '['
    LIST_END = ']'

    IGNORED_SEPARATORS = [' ', '\t', ',']
    KEPT_SEPARATORS = [LIST_START, LIST_END]# put ',' here ?
    SPECIAL_SEPARATORS = ['\n', "'"]# move '\n' to ignored ?
    SEPARATORS = IGNORED_SEPARATORS+KEPT_SEPARATORS+SPECIAL_SEPARATORS
    # 1 more for STRING_SEPARATORS or smt

    parsed = []
    lnums = []
    lnum = 1
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
            #print(f'{sep=}')

            block = code[:ind]
            code = code[ind+len(sep):]
            
            parsed.append(block)
            lnums.append(lnum)
            if sep in IGNORED_SEPARATORS:
                pass
            elif sep in KEPT_SEPARATORS:
                parsed.append(sep)
                lnums.append(lnum)
            elif sep in SPECIAL_SEPARATORS:
                if sep == '\n':
                    lnum += 1
                elif sep == "'":
                    code,lnum,str_ = get_till_end_of_str(code,lnum,sep)
                    new = ram.set_anon_var(str_)
                    parsed.append(new)
                    lnums.append(lnum)
                else:
                    assert False
            else:
                assert False

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
                
    

def run_str(code):
    ram = Ram()

    code,lnums = parse_str(code, ram)

    assert len(code) == len(lnums)
    for lnum,token in zip(lnums,code):
        print(lnum,token)
        
def run_file(name):
    with open(name) as f:
        cont = f.read()
    return run_str(cont)


run_file('test1.nl')
