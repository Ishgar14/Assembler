from typing import Dict, Set, Tuple, Union, List

import re

# File Reading
PATH = 'Sem 5/Systems Programming/'
FILE_NAME = 'test.asm'

# Constants needed for parser
# The values of key represent (opcode, exptected token, expected token)
SYMBOL_TABLE: Dict[str, Tuple[int, str, Union[str, None]]] = {
    # Arighmetic Instructions
    'mov': (0, 'register', 'register'),
    'add': (0, 'register', 'register'),
    'sub': (0, 'register', 'register'),
    'mul': (0, 'register', 'register'),
    'div': (0, 'register', 'register'),

    # Branching Instructions
    'jnz': (0, 'label'),
    'jz': (0, 'label'),
    'jnc': (0, 'label'),
    'jc': (0, 'label'),
    'jlt': (0, 'label'),
    'jle': (0, 'label'),
    'jgt': (0, 'label'),
    'jge': (0, 'label'),
    'je': (0, 'label'),
    'jne': (0, 'label'),
    'jmp': (0, 'label'),
    'nop': (0, 'label'),
}
REGISTERS: Set[str] = {'ax', 'bx', 'cx', 'dx'}


f = open(f'{PATH}{FILE_NAME}')


class Instruction:
    def __init__(self, label, opcode, operand1, operand2):
        self.label = label
        self.opcode = opcode
        self.operand1 = operand1
        self.operand2 = operand2

    def __repr__(self) -> str:
        return f"{self.label}\t{self.opcode}\t{self.operand1}\t\t{self.operand2}"


# This function checks whether expected token and given token match
# If they do then return empty string otherwise return string with error message
def check(exptected: str, got: str, line: int) -> str:
    if exptected == 'register':
        if got in REGISTERS:
            return ''
        elif got in labels:
            return f'On line {line} exptected register but got label `{got}`'
        else:
            return f'On line {line} exptected register but got {got}'
    
    elif exptected == 'label':
        if got in labels:
            return ''
        elif got in REGISTERS:
            return f'On line {line} exptected label but got register `{got}`'
        else:
            return f'On line {line} exptected label but got {got}'


# This function parses one instruction at a time and returns an object of class `Instruction`
def parse(inst: str, line: int) -> Instruction:
    (label, opcode, operand1, operand2) = (None, None, None, None)

    parts = re.split(r'\s+', inst)
    if parts[-1] == '':
        parts = parts[:-1]
    # print(parts)

    # if first component is a label
    if parts[0][-1] == ':':
        label = parts[0][:-1]
        labels.add(label)
        parts = parts[1:]

    # check for opcode
    if parts[0].lower() in SYMBOL_TABLE:
        opcode = parts[0]
        exptected_tokens = SYMBOL_TABLE[opcode][1:]
    else:
        print(
            f"Incorrect instruction `{parts[0]}` on line {line} in file `test.asm`")
        return None

    # Check for first operand
    op1 = parts[1].lower()

    # The comma is optional
    if op1[-1] == ',':
        op1 = op1[:-1]

    if err := check(exptected_tokens[0], op1, line):
        print(err)
        return None
    else:
        operand1 = op1

    if len(parts) - 1 != len(exptected_tokens):
        print(f"Incorrect number of operands in {FILE_NAME} on line {line}")
        print(f"Expected {len(exptected_tokens)} tokens got {len(parts) - 1}")
        return None
    else:
        # Check for second operand
        op2 = parts[2].lower()

        if err := check(exptected_tokens[0], op2, line):
            print(err)
            return None
        else:
            operand2 = op2

    return Instruction(label, opcode, operand1, operand2)


instructions: List[Instruction] = []
labels: Set[str] = set()


def main():
    i = 0
    while line := f.readline():
        i += 1
        comment_index = line.find(';')
        if comment_index == -1:
            ins = parse(line, i)

        else:
            line = line[:comment_index]
            if len(line) > 0:
                ins = parse(line, i)
            else:
                ins = None

        # print(line)
        # print(ins)
        instructions.append(ins)


def print_instructions():
    print("Label\tOpcode\tOperand1\tOperand2")
    for ins in instructions:
        print(ins)


if __name__ == '__main__':
    main()
    print_instructions()

f.close()
