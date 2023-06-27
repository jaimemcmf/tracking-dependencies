'''some extra important functions'''
import tokenize
from called_functions import FuncCallVisitor, get_func_calls
import ast
import pickle
import os

url_combinations = ['url="https://', 'url="http://', 'url = "https://', 'url = "http://', "url='https://", "url='http://", "url = 'https://", "url = 'http://"]

def remove_comments(path, filename):
    '''
    removes comments and docstrings
    used so any urls in comments are not flagged
    taken from https://stackoverflow.com/questions/1769332/script-to-remove-python-comments-docstrings/1769577#1769577
    with little tweaks
    '''
    #TODO deletes string that shouldn't be deleted
    #     particularly in package PyYAML-6.0
    os.chdir(path)
    
    source = open(filename)
    mod = open('clean_'+filename, "w")
    
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(source.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        if token_type == tokenize.COMMENT:
            pass
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                if prev_toktype != tokenize.NEWLINE:
                    if start_col > 0:
                        out += token_string
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    out = '\n'.join(l for l in out.splitlines() if l.strip())
    mod.write(out)
    return 'clean_'+filename

def url_in_prints(cfile):
    '''
    function to find hardcoded urls in printing functions, to exclude this cases from the suspicious
    '''
    with open(cfile, 'r', encoding="utf-8") as file:
        content = file.read()
    tree = ast.parse(content)
    calls = get_func_calls(tree)
    for func in calls:
        if 'print' or 'textwrap.dedent' in func[0]:
            try:
                combined = '\t'.join(func)
                if "url='https://" in combined or "url='http://" in combined or 'url="https://' in combined:
                    return True
            except:
                pass
    
    return False

    
def url_in_setup(cfile):
    '''
    function to check if url parameter in setup function is used, to exclude from the suspicious
    '''
    with open(cfile, 'r', encoding="utf-8") as file:
        content = file.read()
    if "setup" in content:
        for comb in url_combinations:
            if comb in content:
                return True
    #content2 = content.split('setup(',1)[1]
    #urls_in_setup = re.findall('https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)', content)
    #print(urls_in_setup)
    return False

def manual_pip_install(cfile):
    '''
    function that tries to find attempts of pip installing "manually"
    '''
    with open(cfile, 'r', encoding="utf-8") as file:
        content = file.read()
    try:
        tree = ast.parse(content)
    except:
        return False
    
    calls = get_func_calls(tree)
    for func in calls:
        if 'getoutput' in func[0] or 'system' in func[0] or 'subprocess' in func[0]:
            try:
                if 'pip install' in func[1] or 'pip download' in func[1]:
                    return True
            except:
                pass
            if 'pipinstall' in '\t'.join(func):
                return True
    
    return False


def save_visited(visited):
    with open('last_visited.txt', 'wb') as file:
        pickle.dump(visited, file)


def flatten(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten(i))
        else: rt.append(i)
    return rt
