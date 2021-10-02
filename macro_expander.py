# from macro_processor import *
from typing import Dict, List
import macro_processor

ACTUAL_PARAMTER_TABLE: List[List[str]] = []


def expand() -> List[str]:
    pass

def parse_macro_call(macro_name: str, parameters: List[str]) -> None:
    actual_parameters: List[str] = []
    parameter_type: List[str] = []
    keyword_parameters = {kp[0]: kp[1] for kp in macro_processor.KEYWORD_PARAMTER_TABLE}
    macro_prototype = {macro[0].strip(): [*macro[1:]] for macro in macro_processor.MACRO_NAME_TABLE}

    for part in parameters:
        parameter_type.append('k' if '=' in part else 'p')
    
    for i in range(len(parameters)):
        if parameter_type[i] == 'p':
            actual_parameters.append(parameters[i])
        else:
            actual_parameters.append(keyword_parameters[parameters[i]])
    
    # If number if parameters in macro call are not equal to #PP + #KP
    # then acknowledge all those remaining keyword parameters
    if len(parameters) != sum(macro_prototype[macro_name][:2]):
        for keyword in keywords_of(macro_name, macro_prototype):
            actual_parameters.append(keyword[1])

    ACTUAL_PARAMTER_TABLE.append(actual_parameters)
    print(ACTUAL_PARAMTER_TABLE)


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
                continue

            if line.lower().strip() == 'macro':
                while f.readline().strip().lower() != 'mend':
                    pass
            
            parts = [ p for p in line.strip().split(' ') if len(p) > 0 ]

            if parts[0] in macro_names:
                parts = [ p.replace(',', '') for p in parts ]
                parse_macro_call(parts[0], parts[1:])
                expanded_macro = expand()
                lines = lines[:i] + expanded_macro + lines[i + 1:]
                i += len(expanded_macro)
            else:
                i += 1


if __name__ == '__main__':
    main('./ass5.asm')