import os
import re
from collections import defaultdict
from copy import deepcopy


MAIN_SCRIPT_NAME = "mindstone"
COMPILED_SCRIPT_NAME = "compiled"
LOADOUTS_SCRIPT_NAME = "loadouts"

raw_import_re = re.compile("\s*import\s*(my/)?(?P<module>.+?)$")
var_import_re = re.compile(
    "\s*var\s*(?P<var>.+?)\s*=\s*import\s*(my/)?(?P<module>.+?)$"
)
func_re = re.compile("func (?P<name>.+?)\(.*?\)")

equip_re = re.compile("equip(L|R)?\s+\{(?P<category>.+)\.(?P<spec>.+)\}")
weapon_re = re.compile(
    "(?P<name>.+?)\s+\*(?P<level>\d+)(\s*\+\s*(?P<ench>\d+))?(\s+(?P<elem>.+))?"
)


weapon_aliases = {
    "melee.1h": [
        "poison sword",
        "fire sword",
        "ice sword",
        "aether sword",
        "vigor sword",
        "stone sword",
        "sword",
        "poison hammer",
        "fire hammer",
        "ice hammer",
        "aether hammer",
        "vigor hammer",
        "stone hammer",
        "war hammer",
    ],
    "shields.armor": [
        "poison shield",
        "fire shield",
        "ice shield",
        "aether shield",
        "vigor shield",
        "stone shield",
        "shield",
        "compound shield",
    ],
    "melee.hammer": [
        "poison hammer",
        "fire hammer",
        "ice hammer",
        "aether hammer",
        "vigor hammer",
        "stone hammer",
        "war hammer",
    ],
    "melee.staff": [
        "poison staff",
        "fire staff",
        "ice staff",
        "aether staff",
        "vigor staff",
        "staff",
    ],
    "ranged.1h": [
        "crossbow",
        "poison wand",
        "fire wand",
        "ice wand",
        "aether wand",
        "vigor wand",
        "stone wand",
    ],
    "ranged.2h": [
        "poison crossbow",
        "fire crossbow",
        "ice crossbow",
        "aether crossbow",
        "vigor crossbow",
        "stone crossbow",
        "repeating crossbow",
    ],
    "shields.dashing": ["dashing shield"],
}

generic_functions = {
    "equip_1h_melee": "equip_2_weapons",
    "equip_dps_melee": "equip_2_weapons",
    "equip_staff": "equip_1_weapon",
    "equip_dashing": "equip_2_weapons",
    "equip_armor_piercing": "equip_2_weapons",
    "equip_ranged_healing": "equip_2_weapons",
    "equip_ranged_shield": "equip_2_weapons",
    "equip_ouroboros": "equip_2_weapons",
    "equip_triskelion": "equip_2_weapons",
    "equip_star": "equip_2_weapons",
    "equip_ranged_dps": "equip_1_weapon",
}


def get_weapon(weapon_cache, elem, *args):
    for arg in args:
        if arg not in weapon_cache or len(weapon_cache[arg]) == 0:
            continue
        elem_weapon = None
        weapons = weapon_cache[arg]
        for i, weapon in enumerate(reversed(weapons)):
            if elem and weapon[3] == elem:
                if i == 0:
                    return weapons.pop()[0]
                elem_weapon = weapon
        weapon = weapons[-1]
        if elem_weapon and (elem_weapon[1] + elem_weapon[2]) >= (weapon[1] + weapon[2] - 1):
            weapons.remove(elem_weapon)
            return elem_weapon[0]
        else:
            return weapons.pop()[0]
    return ""


def itemize(line, weapon_cache):
    for spec, gen in generic_functions.items():
        for match in re.finditer(f"{spec}\((?P<elem>.*?)\)", line):
            elem = match.group("elem")
            elem = elem.strip('"') if elem else ""
            weapons = []
            temp_cache = deepcopy(weapon_cache)
            if spec == "equip_ouroboros":
                weaponL = "ouroboros"
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "shields.armor",
                    "shields.dashing",
                    "melee.1h",
                    "melee.hammer",
                    "ranged.1h",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_triskelion":
                weaponL = "triskelion"
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "shields.armor",
                    "shields.dashing",
                    "melee.1h",
                    "melee.hammer",
                    "ranged.1h",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_star":
                weaponL = "star"
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "shields.armor",
                    "shields.dashing",
                    "melee.1h",
                    "melee.hammer",
                    "ranged.1h",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_1h_melee":
                weaponL = get_weapon(
                    temp_cache, elem, "melee.1h", "melee.hammer", "ranged.1h"
                )
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "shields.armor",
                    "shields.dashing",
                    "melee.1h",
                    "melee.hammer",
                    "ranged.1h",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_dps_melee":
                weaponL = get_weapon(
                    temp_cache, elem, "melee.1h", "melee.hammer", "ranged.1h"
                )
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "melee.1h",
                    "melee.hammer",
                    "ranged.1h",
                    "shields.armor",
                    "shields.dashing",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_dashing":
                weaponL = get_weapon(
                    temp_cache, elem, "melee.1h", "melee.hammer", "ranged.1h"
                )
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "shields.dashing",
                    "melee.1h",
                    "melee.hammer",
                    "ranged.1h",
                    "shields.armor",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_armor_piercing":
                weaponL = get_weapon(
                    temp_cache, elem, "melee.hammer", "melee.1h", "ranged.1h"
                )
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "melee.hammer",
                    "melee.1h",
                    "ranged.1h",
                    "shields.armor",
                    "shields.dashing",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_ranged_healing":
                weaponL = get_weapon(
                    temp_cache, elem, "ranged.1h", "melee.1h", "melee.hammer"
                )
                weaponR = "ouroboros"
                weapons = [weaponL, weaponR]
            elif spec == "equip_ranged_shield":
                weaponL = get_weapon(
                    temp_cache, elem, "ranged.1h", "melee.1h", "melee.hammer"
                )
                weaponR = get_weapon(
                    temp_cache,
                    elem,
                    "shields.armor",
                    "shields.dashing",
                    "melee.1h",
                    "melee.hammer",
                    "ranged.1h",
                )
                weapons = [weaponL, weaponR]
            elif spec == "equip_staff":
                weapon = get_weapon(weapon_cache, elem, "melee.staff")
                if weapon:
                    weapons = [weapon]
                else:
                    weaponL = get_weapon(
                        temp_cache, elem, "melee.1h", "melee.hammer", "ranged.1h"
                    )
                    weaponR = get_weapon(
                        temp_cache,
                        elem,
                        "melee.1h",
                        "melee.hammer",
                        "ranged.1h",
                        "shields.armor",
                        "shields.dashing",
                    )
                    weapons = [weaponL, weaponR]
                    gen = "equip_2_weapons"
            elif spec == "equip_ranged_dps":
                weapon = get_weapon(
                    temp_cache,
                    elem,
                    "ranged.2h",
                )
                if weapon:
                    weapons = [weapon]
                else:
                    weaponL = get_weapon(
                        temp_cache, elem, "ranged.1h", "melee.1h", "melee.hammer"
                    )
                    weaponR = get_weapon(
                        temp_cache,
                        elem,
                        "ranged.1h",
                        "melee.1h",
                        "melee.hammer",
                        "shields.armor",
                        "shields.dashing",
                    )
                    weapons = [weaponL, weaponR]
                    gen = "equip_2_weapons"
            weapon_string = '"' + '", "'.join(weapons) + '"'
            line = line.replace(f"{match.group(0)}", f"{gen}({weapon_string})")
    return line


def parse_line(s):
    match = raw_import_re.match(s)
    if match is not None:
        return "module", match.group("module")
    match = var_import_re.match(s)
    if match is not None:
        return "var", match.group("module"), match.group("var")
    match = func_re.match(s)
    if match is not None:
        return "func", match.group("name")
    return "plain", s


def sanitize_line(line, funcs, imported_vars, weapon_cache):
    line = itemize(line, weapon_cache)
    for var in imported_vars:
        line = re.sub(f"{var}\.(?P<func>.+?)\(\)", f"{var}_\g<func>()", line)
    for func in funcs:
        line = re.sub(f"{func}\(\)", f"{funcs[func]}()", line)
    return line


def sanitize_main_line(line, funcs, imported_vars, weapon_cache):
    line = itemize(line, weapon_cache)
    for var in imported_vars:
        line = re.sub(f"{var}\.", "", line)
    for func in funcs:
        line = re.sub(f"{func}\(\)", f"{funcs[func]}", line)
    return line


def load_items():
    matches = {}
    weapon_cache = defaultdict(list)
    with open("weapons.conf") as f:
        for ln, line in enumerate(f.read().splitlines()):
            if not line:
                continue
            match = weapon_re.search(line)
            if match is None:
                print(f"failed to parse weapon.conf: line {ln}: `{line}`")
                continue
            matches[match.group("name")] = match
            if not any(
                match.group("name") in weapon_aliases[cat] for cat in weapon_aliases
            ):
                print(f"unknown weapon type: line {ln}: `{line}`")
    for category, aliases in weapon_aliases.items():
        for alias in aliases:
            if alias in matches:
                match = matches[alias]
                elem = match.group("elem")
                if elem is None:
                    for el in ("fire", "ice", "aether", "poison", "vigor"):
                        if match.group("name").startswith(el):
                            elem = el
                            break
                sig = (
                    match.group(0),
                    int(match.group("level")),
                    int(match.group("ench") or 0),
                    elem,
                )
                weapon_cache[f"{category}"].append(sig)
    for req in ("melee.1h", "shields.armor"):
        if req not in weapon_cache:
            raise RuntimeError(f"Missing at least one weapon in category `{req}`")
    for k, v in weapon_cache.items():
        weapon_cache[k] = sorted(
            v, key=lambda weapon: weapon[1] + weapon[2] + int(bool(weapon[3]))
        )
    return weapon_cache


def main():
    modules = {}
    out = []  #  compiled script

    # load available items
    weapon_cache = load_items()
    print(weapon_cache)

    # read all modules
    for fn in sorted(os.listdir()):
        splt = os.path.splitext(fn)
        if splt[1] == ".txt":
            with open(fn) as f:
                modules[splt[0]] = f.read().splitlines()

    # process loadouts.txt
    imported_vars = set()
    funcs = {}
    itemized_module = []
    for line in modules[LOADOUTS_SCRIPT_NAME]:
        result = parse_line(line)
        if result[0] == "module":
            submodules.add(result[1])
        elif result[0] == "var":
            submodules.add(result[1])
            imported_vars.add(result[2])
        else:
            itemized_module.append(
                sanitize_line(line, funcs, imported_vars, weapon_cache)
            )
    modules[LOADOUTS_SCRIPT_NAME] = itemized_module

    submodules = {"loadouts"}
    # sanitize modules
    for mod_name, module in modules.items():
        if mod_name in (MAIN_SCRIPT_NAME, COMPILED_SCRIPT_NAME, LOADOUTS_SCRIPT_NAME):
            continue
        sanitized_module = []
        imported_vars = set()
        funcs = {}
        for line in module:
            result = parse_line(line)
            if result[0] == "module":
                submodules.add(result[1])
            elif result[0] == "var":
                submodules.add(result[1])
                imported_vars.add(result[2])
            elif result[0] == "func":
                new_func_name = f"{mod_name}_{result[1]}"
                sanitized_module.append(line.replace(result[1], new_func_name))
                funcs[result[1]] = new_func_name
            else:
                sanitized_module.append(
                    sanitize_line(line, funcs, imported_vars, weapon_cache)
                )
            match = equip_re.search(line)
            if match is not None and match.group("item") not in (
                "hatchet",
                "shovel",
                "blade_of_god",
            ):
                print(
                    f"warning, raw equip in module {mod_name}: {match.group('item')}. Use functions from `loadouts.txt` instead."
                )
        modules[mod_name] = sanitized_module

    # inline submodules into the main script
    for submodule in sorted(submodules):
        out.extend(modules[submodule])

    # inline modules into the main script
    imported_vars = set()
    funcs = {}
    for line in modules[MAIN_SCRIPT_NAME]:
        result = parse_line(line)
        if result[0] == "module":
            if result[1] in modules:
                out.extend(modules[result[1]])
        elif result[0] == "var":
            out.extend(modules[result[1]])
            imported_vars.add(result[2])
        elif result[0] == "func":
            new_func_name = f"{result[1]}_{mod_name}"
            out.append(line.replace(result[1], new_func_name))
            funcs[result[1]] = new_func_name
        else:
            out.append(sanitize_main_line(line, funcs, imported_vars, weapon_cache))

    clean_out = []
    comment = False
    for line in out:
        if line.startswith("/*"):
            comment = True
        if not comment:
            clean_out.append(line)
        if line.startswith("*/"):
            comment = False

    with open("compiled.txt", mode="w") as f:
        f.write("\n".join(clean_out))


if __name__ == "__main__":
    main()
