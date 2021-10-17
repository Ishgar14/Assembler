from typing import Dict, List, Union
import macro_processor

ACTUAL_PARAMTER_TABLE: List[List[str]] = []


# This funciton expands the current macro call
def expand(macro_name: str) -> List[str]:
    macro_definition = macro_processor.MACRO_DEFINITION_TABLE
    expansion_variables = {}
    conditions = {
        'ne' : lambda a,b: a != b, 'eq' : lambda a,b: a == b,
        'le' : lambda a,b: a <= b, 'lt' : lambda a,b: a <  b,
        'ge' : lambda a,b: a >= b, 'gt' : lambda a,b: a >  b,
    }
    macro_names = [m[0].strip() for m in macro_processor.MACRO_NAME_TABLE]
    macro_body_ptr = macro_processor.MACRO_NAME_TABLE[macro_names.index(macro_name)][-3]
    macro_body = macro_definition[
        macro_body_ptr: macro_definition.index('mend', macro_body_ptr)]
    
    parameters = ACTUAL_PARAMTER_TABLE[-1]
    instruction = []
    expansion = []

    i = 0
    while i < len(macro_body):
        if macro_processor.classify(macro_body[i]) == 'm':
            # If no parameters in current macro instruction
            if '(' not in macro_body[i]:
                expansion.append(macro_body[i] + '\n')
                i += 1
                continue
            
            mnemonic = macro_body[i][:macro_body[i].index(' ')]
            instruction.append(mnemonic)

            # If operand1 is not a macro parameter
            if macro_body[i].index(',') < macro_body[i].index('('):
                instruction.append(macro_body[i][macro_body[i].index(' ') + 1:macro_body[i].index(',')])

            for para in get_next_parameter(macro_body[i]):
                ind = macro_body[i].index(para)
                if macro_body[i][ind - 1] in '+-':
                    displacement = macro_body[i][ind - 1]
                    value = to_val(macro_body[i][ind:].rstrip(), expansion_variables)
                    instruction[-1] += f"{displacement}{value}"
                    continue
                number = int(para[-1]) - 1
                if para[1].lower() == 'p':
                    try: new_para = parameters[number]
                    except: 
                        keywords = dict(macro_processor.KEYWORD_PARAMTER_TABLE)
                        new_para = keywords[macro_processor.PARAMETER_NAME_TABLE[macro_name][number]]
                else:
                    new_para = expansion_variables[para[para.index(',')+1:]]

                # If the parameter is within a literal then
                if macro_body[i][ind - 2] == '=':
                    instruction.append(f"='{new_para}'")
                else:
                    instruction.append(new_para)

            if '=' in macro_body[i]:
                eq_index = macro_body[i].index('=')
                # if operand 2 is literal number
                if macro_body[i][eq_index + 2:-1].isnumeric():
                    instruction[1] = instruction[1] + ', '
                    instruction.append(macro_body[i][eq_index:])
            instruction.append('\n')
            expansion.append(instruction)
            instruction = []
        
        else: # if it is a preprocessing statement
            parts = [s.strip() for s in macro_body[i].split(' ') if s.strip()]
            if parts[0].lower() == 'lcl':
                _, _, id = parts[1].partition(',')
                expansion_variables[id[:-1]] = 0
            elif parts[1].lower() == 'set':
                _, _, id = parts[0].partition(',')
                if parts[2].isnumeric():
                    expansion_variables[id[:-1]] = int(parts[2])
                else:
                    for ev in get_next_parameter(parts[2]):
                        ev_id = ev[ev.index(',') + 1]
                        parts[2] = parts[2].replace(ev, str(expansion_variables[ev_id]))
                        parts[2] = parts[2].replace(')', '', 1)
                    expansion_variables[id[:-1]] = eval(parts[2])
            elif parts[0].lower() == 'ago':
                sequence_number = int(parts[1][3:-1]) - 1
                i = macro_processor.SEQUENCE_SYMBOL_TABLE[macro_name][sequence_number][1] - 2
            elif parts[0].lower() == 'aif':
                operation = [parts[1][1:], parts[2], parts[3][:-1]]
                jump_to = int(parts[4][3:-1])
                func = conditions[operation[1].lower()]
                op1 = to_val(operation[0], expansion_variables)
                op2 = to_val(operation[2], expansion_variables)
                if func(op1, op2):
                    i = macro_processor.SEQUENCE_SYMBOL_TABLE[macro_name][jump_to - 1][1] - 2
            
        i += 1

    return expansion

def get_next_parameter(instruction: str) -> str:
    i = 0
    while i < len(instruction):
        if instruction[i] == '(':
            index = instruction.index(')', i)
            yield instruction[i: index]
            i = index
        else:
            i += 1
    return ''

# This function takes in a tabular repesentation of symbols and returns their value
# eg.  to_val("(E,1)") returns value of expansion variable 1
def to_val(s: str, ev) -> Union[str, int]:
    s = s.lower()
    if s[1] == 'e':
        return ev[s[3:-1]]
    elif s[1] == 'p':
        return int(ACTUAL_PARAMTER_TABLE[-1][int(s[3:-1]) - 1])


def parse_macro_call(macro_name: str, parameters: List[str]) -> None:
    actual_parameters: List[str] = []
    macro_prototype = {macro[0].strip(): [*macro[1:]] for macro in macro_processor.MACRO_NAME_TABLE}

    parameter_type = [ch for ch in (("p" * macro_prototype[macro_name][0]) + 
                                    ("k" * macro_prototype[macro_name][1]))]
    
    for i in range(len(parameters)):
        if '=' in parameters[i]:
            _, _, val = parameters[i].partition('=')
            actual_parameters.append(val)
        else:
            actual_parameters.append(parameters[i])
    
    # If number if parameters in macro call are not equal to #PP + #KP
    # then acknowledge all those remaining keyword parameters
    if len(parameters) != sum(macro_prototype[macro_name][:2]):
        keywords = [k[1] for k in keywords_of(macro_name, macro_prototype)]
        if len(keywords) == macro_prototype[macro_name][0]:
            keywords = keywords[len(actual_parameters) - parameter_type.count('k'):]
        actual_parameters.extend(keywords)

    ACTUAL_PARAMTER_TABLE.append(actual_parameters)


# This function returns all keyword parameters of given macro
def keywords_of(macro_name: str, macro_prototype_info: Dict[str, list]) -> list:
    keyword_table_ptr = macro_prototype_info[macro_name][-2]
    macro_names = [m[0].strip() for m in macro_processor.MACRO_NAME_TABLE]

    if macro_names.index(macro_name) == len(macro_names) - 1:
        return macro_processor.KEYWORD_PARAMTER_TABLE[keyword_table_ptr:]
        # ^ When there is a single macro definition present in assembly file
        # then just returning above statement is enough
    else:
        end = macro_names.index(macro_name) + 1
        return macro_processor.KEYWORD_PARAMTER_TABLE[keyword_table_ptr:end]


def main(filename: str) -> None:
    macro_processor.parse(filename)
    macro_names = set([m[0].strip() for m in macro_processor.MACRO_NAME_TABLE])

    with open(filename) as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            if line.lower().strip() == 'macro':
                macro_start = i
                while lines[i].strip() != 'mend':
                    i += 1
                lines = lines[:macro_start] + lines[i + 1:]
                i = macro_start
                continue
            
            parts = [ p for p in line.strip().split(' ') if len(p) > 0 ]

            if parts[0] in macro_names:
                parts = [ p.replace(',', '') for p in parts ]
                parse_macro_call(parts[0], parts[1:])
                expanded_macro = [' '.join(exp) if isinstance(exp, list) else exp for exp in expand(parts[0]) ]
                lines = lines[:i] + expanded_macro + lines[i + 1:]
                i += len(expanded_macro)
            else:
                i += 1

    OUTPUT_FILENAME = './output.asm'
    with open(OUTPUT_FILENAME, 'w') as f:
        for line in lines:
            if line != '\n':
                f.write(line)
                # print(line)
    

def print_MDT():
    print(macro_processor.titalize(' Maro Definition Table '))
    print('Index\tInstruction')
    for index, row in enumerate(macro_processor.MACRO_DEFINITION_TABLE):
        print(index + 1, row, sep='\t')

def print_MNT():
    print(macro_processor.titalize(' Macro Name Table '))
    print('Index\tName\t\t#PP\t#KP\t#EV\tMDTP\tKPDTP\tSSTP')
    for index, (name, positionals, keywords, envis, mdtp, kpdtp, sstp) in enumerate(macro_processor.MACRO_NAME_TABLE):
        print(index + 1, name, positionals, keywords, envis, mdtp + 1, 
            (kpdtp + 1) if isinstance(kpdtp, int) else kpdtp, 
            (sstp + 1) if isinstance(sstp, int) else sstp, 
            sep='\t')

def print_APTab():
    print(" Actual Parameter Table ".center(80, '='))
    print("Index\tActual Parameter Values")
    for index, val in enumerate(ACTUAL_PARAMTER_TABLE):
        print(index + 1, *val, sep='\t')
    
if __name__ == '__main__':
    # main('./ass5.asm')
    main('./macro.asm')

    print_MNT()
    print_MDT()
    print_APTab()