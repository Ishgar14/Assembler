import re
from typing import Set, Tuple, List

FILE_NAME = './macro.asm'


PREPROCESSOR_TOKENS = {'lcl', 'set', 'aif', 'ago'}


# All the Tables
MACRO_NAME_TABLE = [] # List of lists of [name, #pp, #kp, #ev, #MDTP, #KPTP, #SSIP]
MACRO_DEFINITION_TABLE: List[str] = [] # list of all instructions of macro
KEYWORD_PARAMTER_TABLE: List[Tuple[str, str]] = [] # List of tuple of (keyword parameter, actual value)
PARAMETER_NAME_TABLE: List[str] = [] # List of names of all positional parameters
SEQUENCE_SYMBOL_TABLE: List[int] = [] # List of positions in MDT of all sequence symbols
EXPANSION_VARIABLE_TABLE: List[str] = [] # List of names of all expansion time variables
UWU_TABLE: List[str] = [] # List of all your dopamine

# To keep track of forward referenced symbols
backlog_symbols: Set[str] = set()

# This function parses the prototype of the macro
def parse_proto(line: str) -> None:
    name, positionals, keywords, expansionals = '', 0, 0, 0
    macro_def_tab_ptr, keyword_tab_ptr, seq_symbol_ptr = len(MACRO_DEFINITION_TABLE), len(KEYWORD_PARAMTER_TABLE), len(SEQUENCE_SYMBOL_TABLE)

    parts = [ p for p in re.split(r'\s+', line) if len(p) > 0 ]
    name = parts[0].ljust(10)

    for p in parts[1:]:
        p = p.replace(',', '')

        # If it is a formal parameter
        if p.startswith('&'):
            # If it is a keyword parameter
            if '=' in p:
                keywords += 1
                eq_index = p.index('=')
                parameter_name = p[1:eq_index]
                default_val = p[eq_index + 1:]

                KEYWORD_PARAMTER_TABLE.append((parameter_name, default_val))
                PARAMETER_NAME_TABLE.append(parameter_name)

            
            # If it is a positional parameter
            else:
                positionals += 1
                PARAMETER_NAME_TABLE.append(p[1:])

    MACRO_NAME_TABLE.append([name, positionals, keywords, expansionals, 
        macro_def_tab_ptr, keyword_tab_ptr, seq_symbol_ptr])


# This function properly filters out the crap and returns valid name of expansion variable
def get_name(line: str) -> str:
    line = line[line.index('&') + 1:]
    for i in range(len(line)):
        if not line[i].isalpha():
            return line[:i]

    return line

# Replace all formal parameters with their table pointers
def purify(part: str) -> str:
    if '&' not in part:
        return part

    try: 
        name = get_name(part)
        if name in EXPANSION_VARIABLE_TABLE:
            var_type = 'E'
            index = EXPANSION_VARIABLE_TABLE.index(name)
        elif name in PARAMETER_NAME_TABLE:
            var_type = 'P'
            index = PARAMETER_NAME_TABLE.index(name)

    except ValueError: 
        print(f"expansion variable `{name}` not declared anywhere in code") 
        exit(1)

    return part.replace(f'&{name}', f'({var_type}, {index+1})')

# This function parses model statements
def parse_models(line: str):
    parts = [ p for p in re.split(r'\s+', line) if len(p) > 0 ]
    
    # If first part is a sequence symbol
    if parts[0].startswith('.'):
        sequence = parts[0][1:]
        parts = parts[1:]
        if sequence in backlog_symbols: backlog_symbols.remove(sequence)
        SEQUENCE_SYMBOL_TABLE.append((sequence, len(MACRO_DEFINITION_TABLE) + 1))


    i = 0
    while i < len(parts):
        # if there are formal parameters in current part
        if '&' in parts[i]:
            # then replace them with their proper representation
            while (replacement := purify(parts[i])) != parts[i]:
                parts[i] = replacement
        
        i += 1

    instruction = f'{" ".join(parts)}'
    return instruction


# This function parses preprocessor statements
def parse_prepro(line: str):
    parts = [ p for p in re.split(r'\s+', line) if len(p) > 0 ]
    # If first part is a sequence symbol
    if parts[0].startswith('.'):
        sequence = parts[0][1:]
        parts = parts[1:]
        SEQUENCE_SYMBOL_TABLE.append((sequence, len(MACRO_DEFINITION_TABLE) + 1))
        if sequence in backlog_symbols: backlog_symbols.remove(sequence)
        parts[0] = f'(S, {len(SEQUENCE_SYMBOL_TABLE)})'
    
    # If last part is a sequence symbol
    if parts[-1].startswith('.'):
        sequence = parts[-1][1:]
        symbol_names = [seq[0] for seq in SEQUENCE_SYMBOL_TABLE]
        if sequence in symbol_names:
            parts[-1] = f'(S, {symbol_names.index(sequence) + 1})'
        else:
            backlog_symbols.add(sequence)

    # If we are defining a expansion time variable
    if parts[0] == 'lcl':
        MACRO_NAME_TABLE[-1][3] += 1
        EXPANSION_VARIABLE_TABLE.append(parts[1][1:])

    # If it is a set operation
    elif parts[0].startswith('&') and parts[1] == 'set':
        pass

    i = 0
    while i < len(parts):
        # if there are formal parameters in current part
        if '&' in parts[i]:
            # then replace them with their proper representation
            while (replacement := purify(parts[i])) != parts[i]:
                parts[i] = replacement
        
        i += 1

    instruction = f'{" ".join(parts)}'
    return instruction


# This function classifies wehther a given line is model or preprocessor statement
def classify(line: str) -> str:
    parts = [ p.lower() for p in re.split(r'\s+', line) if len(p) > 0 ]

    if parts[0] in PREPROCESSOR_TOKENS or parts[1] in PREPROCESSOR_TOKENS:
        return 'p'
    else:
        return 'm'



def parse() -> None:
    with open(FILE_NAME) as f:
        while line := f.readline():
            if line.lower().strip() != 'macro':
                continue
            
            parse_proto(f.readline())

            while (l := f.readline()).lower() != 'mend':
                if len(l) == 0 or len(l.strip()) == 0:
                    continue
                
                classification = classify(l)

                if classification == 'm':
                    ins = parse_models(l)
                elif classification == 'p':
                    ins = parse_prepro(l)
                
                MACRO_DEFINITION_TABLE.append(ins)

            MACRO_DEFINITION_TABLE.append('mend')

    # Now we have to parts the Instructions again
    # To make sure that forward referenced symbols have their proper representation
    i = 0
    while i < len(MACRO_DEFINITION_TABLE):
        l = MACRO_DEFINITION_TABLE[i][:3].lower()
        if l == 'ago' or l == 'aif':
            MACRO_DEFINITION_TABLE[i] = parse_prepro(MACRO_DEFINITION_TABLE[i])
        i += 1

def print_MDT():
    print(titalize(' Maro Definition Table '))
    print('Index\tInstruction')
    for index, row in enumerate(MACRO_DEFINITION_TABLE):
        print(index + 1, row, sep='\t')

def print_MNT():
    print(titalize(' Macro Name Table '))
    print('Index\tName\t\t#PP\t#KP\t#EV\tMDTP\tKPDTP\tSSTP')
    for index, (name, positionals, keywords, envis, mdtp, kpdtp, sstp) in enumerate(MACRO_NAME_TABLE):
        print(index + 1, name, positionals, keywords, envis, mdtp + 1, kpdtp + 1, sstp + 1, sep='\t')


def print_PNT():
    print(titalize(' Parameter Name Table '))
    print('Index\tName')
    for index, row in enumerate(PARAMETER_NAME_TABLE):
        print(index + 1, row, sep='\t')

def print_KPT():
    print(titalize(' Keyword Parameter Default Table '))
    print('Index\tName\tValue')
    for index, row in enumerate(KEYWORD_PARAMTER_TABLE):
        print(index + 1, '\t'.join(row), sep='\t')


def print_EVT():
    print(titalize(' Expansion Variable Name Table '))
    print('Index\tName')
    for index, row in enumerate(EXPANSION_VARIABLE_TABLE):
        print(index + 1, '\t'.join(row), sep='\t')

def print_SST():
    print(titalize(' Sequence Symbol Name Table '))
    print('Index\tName')
    for index, (name, _) in enumerate(SEQUENCE_SYMBOL_TABLE):
        print(index + 1, name, sep='\t')

def print_SNT():
    print(titalize(' Sequence Symbol Table '))
    print('Index\tName\tEntry')
    for index, (name, entry) in enumerate(SEQUENCE_SYMBOL_TABLE):
        print(index + 1, name, entry, sep='\t')

def print_all_tables():
    print_MNT()
    print_MDT()
    print_PNT()
    print_KPT()
    print_EVT()
    print_SST()
    print_SNT()
    

def titalize(title: str, size: int = 75, pattern: str = '=') -> str:
    return title.center(size, pattern)

if __name__ == '__main__':
    parse()
    print_all_tables()
