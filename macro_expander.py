# from macro_processor import *
from typing import Dict, List
import macro_processor
import assembler

ACTUAL_PARAMTER_TABLE: List[List[str]] = []


# This funciton expands the current macro call
def expand(macro_name: str) -> List[str]:
    macro_definition = macro_processor.MACRO_DEFINITION_TABLE
    # expansion_variables = {}
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
            # If no parameters in current macro isntruction
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
                number = parameters[int(para[-1]) - 1]

                # If the parameter is within a literal then
                if macro_body[i][ind - 2] == '=':
                    instruction.append(f"='{number}")
                else:
                    instruction.append(number)
            instruction.append('\n')
        else:
            pass
        i += 1
        expansion.append(instruction)
        instruction = []

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

def parse_macro_call(macro_name: str, parameters: List[str]) -> None:
    actual_parameters: List[str] = []
    parameter_type: List[str] = []
    keyword_parameters = {kp[0]: kp[1] for kp in macro_processor.KEYWORD_PARAMTER_TABLE}
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
        keywords = keywords[len(actual_parameters) - parameter_type.count('k'):]
        actual_parameters.extend(keywords)

    ACTUAL_PARAMTER_TABLE.append(actual_parameters)
    # print(ACTUAL_PARAMTER_TABLE)


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

    with open('./output.asm', 'w') as f:
        for line in lines:
            # print(line)
            f.write(line)
    
    assembler.FILE_NAME = './output.asm'
    assembler.pass1()
    assembler.error_or_execute()

    print(" Actual Parameter Table ".center(80, '='))
    print("Index\tParam Values")
    for index, val in enumerate(ACTUAL_PARAMTER_TABLE):
        print(index + 1, *val, sep='\t')

if __name__ == '__main__':
    main('./ass5.asm')