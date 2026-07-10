import re, time

def next_free_number(category, prefix):
    if not category: return 1
    used = set()
    pat = re.compile(rf"^{re.escape(prefix)}\s+(\d+)$")
    for ch in category.voice_channels:
        m = pat.match(ch.name)
        if m: used.add(int(m.group(1)))
    n = 1
    while n in used: n += 1
    return n

def format_duration(seconds):
    s = int(max(0, seconds))
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def now():
    return time.time()

def xp_for_level(level):
    return 100 * (level ** 2) + 100

def calc_level(xp):
    level = 0
    while xp >= xp_for_level(level + 1):
        xp -= xp_for_level(level + 1)
        level += 1
    return level

def parse_duration(s):
    total, num = 0, ""
    for c in s:
        if c.isdigit(): num += c
        elif c == "d" and num: total += int(num)*86400; num=""
        elif c == "h" and num: total += int(num)*3600;  num=""
        elif c == "m" and num: total += int(num)*60;    num=""
        elif c == "s" and num: total += int(num);        num=""
    return total
