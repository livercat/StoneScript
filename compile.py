import os
import re


MAIN_SCRIPT_NAME = 'mindstone'
COMPILED_SCRIPT_NAME = 'compiled'
raw_import_re = re.compile('\s*import\s*(my/)?(?P<module>.+?)$')
var_import_re = re.compile('\s*var\s*(?P<var>.+?)\s*=\s*import\s*(my/)?(?P<module>.+?)$')
func_re = re.compile('func (?P<name>.+?)\(.*?\)')
equip_re = re.compile('equip(L|R)?\s+(?P<item>.+)')


def parse_line(s):
    match = raw_import_re.match(s)
    if match is not None:
        return 'module', match.group('module')
    match = var_import_re.match(s)
    if match is not None:
        return 'var', match.group('module'), match.group('var')
    match = func_re.match(s)
    if match is not None:
        return 'func', match.group('name')
    return 'plain', s


if __name__ == "__main__":
    modules = {}
    out = [] #  compiled script
    items = set()

    # read all modules
    for fn in sorted(os.listdir()):
        splt = os.path.splitext(fn)
        if splt[1] == '.txt':
            with open(fn) as f:
                modules[splt[0]] = f.read().splitlines()

    submodules = set()
    # sanitize modules
    for mod_name, module in modules.items():
        if mod_name in (MAIN_SCRIPT_NAME, COMPILED_SCRIPT_NAME):
            continue
        sanitized_module = []
        imported_vars = set()
        funcs = {}
        for line in module:
            result = parse_line(line)
            if result[0] == 'module':
                submodules.add(result[1])
            elif result[0] == 'var':
                submodules.add(result[1])
                imported_vars.add(result[2])
            elif result[0] == 'func':
                new_func_name = f"{mod_name}_{result[1]}"
                sanitized_module.append(line.replace(result[1], new_func_name))
                funcs[result[1]] = new_func_name
            else:
                for var in imported_vars:
                    line = re.sub(f"{var}\.(?P<func>.+?)\(\)", f"{var}_\g<func>()", line)
                for func in funcs:
                    line = re.sub(f"{func}\(\)", f"{funcs[func]}()", line)
                sanitized_module.append(line)
            match = equip_re.search(line)
            if match is not None:
                items.add(match.group('item'))
        modules[mod_name] = sanitized_module

    # inline submodules into the main script
    for submodule in sorted(submodules):
        out.extend(modules[submodule])

    # inline modules into the main script
    imported_vars = set()
    funcs = {}
    for line in modules[MAIN_SCRIPT_NAME]:
        result = parse_line(line)
        if result[0] == 'module':
            if result[1] in modules:
                out.extend(modules[result[1]])
        elif result[0] == 'var':
            out.extend(modules[result[1]])
            imported_vars.add(result[2])
        elif result[0] == 'func':
            new_func_name = f"{result[1]}_{mod_name}"
            out.append(line.replace(result[1], new_func_name))
            funcs[result[1]] = new_func_name
        else:
            for var in imported_vars:
                line = re.sub(f"{var}\.", "", line)
            for func in funcs:
                line = re.sub(f"{func}\(\)", f"{funcs[func]}", line)
            out.append(line)
            
    with open('compiled.txt', mode='w') as f:
        f.write('\n'.join(out))
    
    print(sorted(items))