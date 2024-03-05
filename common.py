import ui, re
from random import randint



BNUMS = { 0: ( "#########", "#########", "###   ###", "###   ###", "###   ###", "###   ###", "#########", "#########", ),
        1: ( "    ###  ", "    ###  ", "    ###  ", "    ###  ", "    ###  ", "    ###  ", "    ###  ", "    ###  " ),
        2: ( "#########", "#########", "      ###", "#########", "#########", "###      ", "#########", "#########", ),
        3: ( "#########", "#########", "      ###", "  #######", "  #######", "      ###", "#########", "#########", ),
        4: ( "###   ###", "###   ###", "###   ###", "#########", "#########", "      ###", "      ###", "      ###", ),
        5: ( "#########", "#########", "###      ", "#########", "#########", "      ###", "#########", "#########", ),
        6: ( "#########", "#########", "###      ", "#########", "#########", "###   ###", "#########", "#########", ),
        7: ( "#########", "#########", "      ###", "      ###", "      ###", "      ###", "      ###", "      ###", ),
        8: ( "#########", "#########", "###   ###", "#########", "#########", "###   ###", "#########", "#########", ),
        9: ( "#########", "#########", "###   ###", "#########", "#########", "      ###", "#########", "#########", ),
        -1: ( "         ", "         ", "         ", "         ", "         ", "         ", "         ", "         ", ), }

def isfloat(what):
    if what.startswith('-'):
        what = what[1:]
    parts = what.split('.')
    return len(parts) == 2 and parts[0].isnumeric() and parts[1].isnumeric()

def is_valid(value, type_str, char_list = None):

    v_types = ( 'is_number', 'is_num', 'is_float', 'is_fl',
        'is_negative', 'is_neg', 'in_lst', 'in_ls', 'len_g', )

    if type_str not in v_types:
        raise ValueError(f'"{type_str}" is not implemented yet')

    value = str(value).strip()

    return (
        type_str.startswith('is_num') and value.isnumeric() or
        type_str.startswith('is_neg') and value.startswith('-') or
        type_str.startswith('is_fl') and isfloat(value) or
        type_str.startswith('in_ls') and value in char_list# or
        #  type_str.startswith('len_g') and len(value) >
    )

def create_tables(cur, db_path):
    for stmt in [
            "CREATE TABLE IF NOT EXISTS food(title TEXT, kcal REAL, p REAL, f REAL, c REAL)",
            "CREATE TABLE IF NOT EXISTS diary(user INT, date TEXT, title TEXT, value REAL)",
            "CREATE TABLE IF NOT EXISTS users(name TEXT, sex TEXT, age INT, height REAL, weight REAL, activity REAL)",
            "CREATE TABLE IF NOT EXISTS current_user(user_id INT)",
            "CREATE TABLE IF NOT EXISTS dishes(title TEXT, ingredients TEXT, kcal REAL, p REAL, f REAL, c REAL)",
            'CREATE TABLE IF NOT EXISTS trainings (name TEXT, repeats INT, pause TEXT, relax TEXT, on_end TEXT)',
            'CREATE TABLE IF NOT EXISTS exercises (title TEXT, body_part TEXT)',
            'CREATE TABLE IF NOT EXISTS exercises_lists (exer_id INT, duration TEXT, training_id INT)',

    ]:

        cur.execute(stmt)

def empty_start(PROG_NAME):
    '''Fileless startup handler'''
    print("No file set.\nUsage: " + PROG_NAME + ".py [OPTIONS] [FILE]")
    exit(-1)


def incr_or_av(some_dict, key):
    '''try increment value of key in some_dict'''
    '''create pair with given key if no key in dict'''
    try:
        some_dict[key] += 1
    except KeyError:
        some_dict[key] = 0

def show_statistic(stat_dict):
    if len(stat_dict) < 1:
        exit(0)
    total_counter = 0

    ui.clear()
    ui.header(HEADERS['statistic'])
    for title, duration in stat_dict.items():
        if title in STRINGS['params'].values():
            continue
        total_counter += duration
        print(title + ': ' + sec_to_hms(duration))

    if total_counter > 0:
        print(f'\nОбщее время тренировки: {sec_to_hms(total_counter)}')
    ui.restore_cursor()
    a = input()
    ui.clear()

def hms_to_sec(time):
    '''takes time and return it in seconds'''
    try:
        match = re.search(r'^([\d\.]+)(.*)$', time).groups()
        mult = 1

        # without if expreasion it returns multiplied on 60
        if match[1] == '':
            mult = 1
        elif match[1] in 'мm':
            mult = 60
        elif match[1] in 'hч':
            mult = 3600

        return int(float(match[0]) * mult)

    except AttributeError:
        return None

def sec_to_hms(sec):
    '''takes time in seconds'''
    '''returns formated string with time in hours, minutes and seconds'''
    h, m = 0, 0
    res = ''
    h = sec // 3600
    sec -= 3600 * h
    m = sec // 60
    sec -= 60 * m

    if h > 0:
        res += '{}ч '.format(h)
    if m > 0:
        res += '{}м '.format(m)
    res += '{}с'.format(sec)
    return res

def hms_to_sec(time):
    '''takes time and return it in seconds'''
    try:
        match = re.search(r'^([\d\.]+)(.*)$', time).groups()
        mult = 1

        # without if expreasion it returns multiplied on 60
        if match[1] == '':
            mult = 1
        elif match[1] in 'мm':
            mult = 60
        elif match[1] in 'hч':
            mult = 3600

        return int(float(match[0]) * mult)

    except AttributeError:
        return None

def sec_to_hms(sec):
    '''takes time in seconds'''
    '''returns formated string with time in hours, minutes and seconds'''
    h, m = 0, 0
    res = ''
    h = sec // 3600
    sec -= 3600 * h
    m = sec // 60
    sec -= 60 * m

    if h > 0:
        res += '{}ч '.format(h)
    if m > 0:
        res += '{}м '.format(m)
    res += '{}с'.format(sec)
    return res

def parse_file(file_name):
    '''takes a training file name and parses it'''
    '''return dict with data from .fct file'''

    data = dict.fromkeys(('name', 'repeats', 'pause', 'relax', 'on_end', ), None)
    data['training_list'] = list()

    try:
        file = open(file_name, 'rt')
        for line in file:
            # chomp line
            line = line.strip()

            if line.startswith('#') or len(line) == 0:
                # skip comments
                continue
            try:
                match = re.search(r'^(.+)([:=]|(?:->))(.+)$', line).groups()
            except AttributeError:
                continue

            if match[1] == '=':
                # line with param splits and set in dict
                data[match[0]] = match[2]

            else:
                # line with exercise splits on tuple of title and duration
                # and appends to list in dict
                data['training_list'].append((match[0], match[2]))

        file.close()
    except:
        pass

    return data

def prepare_training(data, current_repeat):
    '''takes data dict and current repeat number'''
    '''repeats list of exercises for current repeat in right order'''
    r_list = []
    for k, v in data['training_list']:
        k =  k.split('|')
        v = hms_to_sec(v)

        r_list.append((STRINGS['params']['pause'], hms_to_sec(data['pause'])))
        r_list.append((k[randint(0, len(k) - 1)], v))

    if current_repeat == 0:
        r_list[0] = (STRINGS['params']['prepare'], hms_to_sec(data['pause']))
    else:
        r_list[0] = (STRINGS['params']['relax'], hms_to_sec(data['relax']))

    if current_repeat == int(data['repeats']) - 1:
        r_list.append((STRINGS['params']['on_end'], hms_to_sec(data['on_end'])))

    return r_list

def print_big_nums(num):
    '''takes a num and prints big digits of it'''
    l, c  = -1, -1
    if num > 99:
        l = num // 100
        num %= 100
    c = num // 10
    num %= 10
    if c == 0 and l == -1:
        c = -1

    for i in range(8):
        ui.print_as_table([(BNUMS[l][i], BNUMS[c][i],BNUMS[num][i],)], ' ')


HEADERS = {
    'interactive': 'Выберите тренировку',
    'timer': 'Таймер',
    'statistic': 'Статистика тренировки',
}

MENU_ENTRIES = {
    'interactive': ('create', 'remove', 'edit', 'help', 'quit'),
}


SQLS = {
    'training_params':
        'SELECT rowid, * FROM trainings WHERE rowid = ?',
    'training_list':
        'WITH tmp AS (SELECT exer_id, duration FROM exercises_lists WHERE training_id = ?) SELECT e.title, tmp.duration FROM tmp INNER JOIN exercises AS e WHERE tmp.exer_id = e.rowid',

}

STRINGS = {
    'params':
    {'name': 'имя','pause': 'Пауза', 'prepare': 'Приготовьтесь', 'relax': 'Время отдохнуть', 'on_end': 'Конец тренировки'},
    'speeds':
        ('Средне', 'Быстро'),
}
