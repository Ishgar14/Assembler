from typing import Dict, List
import re

# File Reading
FILE_NAME = './ass1.asm'

# Constants needed for parser
LC = 0
MEMORY_WIDTH = 1
REGISTERS = {'areg': 0, 'breg': 1, 'creg': 2, 'dreg': 3, }

# Set of all assembler directives
# The tuple represents (opcode, size of instruction)
MEMORY_DIRECTIVES = {'ds': (0, 2), 'dc': (0, 2), 'ltorg': (0, 1)}
DIRECTIVES = {
    'start': (0, 2),
    'end': (0, 1),
    'org': (0, 2)
} | MEMORY_DIRECTIVES


IO_INSTRUCTIONS = {'read': (1, 2), 'print': (2, 2)}

DATA_TRANSFER_INSTRUCTIONS = {'movem': (3, 3), 'mover': (4, 3)}

ARITHMETIC_INSTRUCTIONS = { 'add': (5, 3), 'sub': (6, 3), 'mul': (7, 3), 'div': (8, 3), 'cmp': (9, 3)}

JUMP_INSTRUCTIONS = {
    'bc': (10, 3),
    'je': (0, 2), 'jne': (1, 2), 'jz': (0, 2), 'jnz': (1, 2),
    'jl': (2, 2), 'jle': (2, 2), 'jg': (4, 2), 'jge': (5, 2),
    'jc': (6, 2), 'jnc': (7, 2), 'jp': (8, 2), 'jnp': (9, 2),
    'jmp': (10, 2), 'any': (11, 2)
}


# The set of valid symbols
MNEMONIC_TABLE = ARITHMETIC_INSTRUCTIONS | JUMP_INSTRUCTIONS | IO_INSTRUCTIONS  \
    | DATA_TRANSFER_INSTRUCTIONS

ERROR_FOUND = False


class Instruction:
    def __init__(self, label: str = "", mnemonic: str = "", operand1: str = "", operand2: str = "",
                    inst_type: str = 'mnemonic', op1_type='', op2_type='', *,
                    line: int = -1, _LC: int = -1):
        self.label = label
        self.mnemonic = mnemonic
        self.operand1 = operand1
        self.operand2 = operand2

        self.instruction_type = inst_type
        self.operand1_type = op1_type
        self.operand2_type = op2_type
        self.line = line  # stores line number for instruction in source code
        self.LC = _LC     # stores line counter for instruction in machine and intermediate code

    def __repr__(self) -> str:
        return f'{self.LC}\t{self.label}\t{self.mnemonic}\t\t{self.operand1}\t\t{self.operand2}\t\t{self.instruction_type}' + \
            f'\t{self.operand1_type}\t{self.operand2_type}'


instructions: List[Instruction] = []

labels: Dict[str, int] = {}
backlog_labels: Dict[str, int] = {}


# This function parses one instruction at a time and returns an object of class `Instruction`
def parse(inst: str, line: int) -> Instruction:
    global ERROR_FOUND, LC, literal_count
    label, opcode, operand1, operand2, inst_type = '', '', '', '', 'mnemonic'
    parts = re.split(r'\s+', inst)

    # if first component is a label
    if parts[0][-1] == ':':
        label = parts[0][:-1]

        if label in backlog_labels:
            del backlog_labels[label]

        if label in labels:
            ERROR_FOUND = True
            print(f'Redeclared the label `{label}` on line {line}')
            return None

        labels[label] = LC
        parts = parts[1:]

    # If first part is an assembler directive
    if parts[0].lower() in DIRECTIVES:
        inst_type = 'declarative' if parts[0].lower() in {'dc', 'ds'} else 'directive'
        opcode = parts[0].lower()

    # check for opcode
    elif parts[0].lower() in MNEMONIC_TABLE:
        opcode = parts[0]
        size = MNEMONIC_TABLE[parts[0].lower()][1]

        if len(parts) != size:
            ERROR_FOUND = True
            print(f'On line {line} `{inst.strip()}`\nExpected {size} tokens but got {len(parts)}')
            return

    else:
        ERROR_FOUND = True
        print(f'Unknown instruction `{parts[0]}` on line {line} in file "{FILE_NAME}"')
        return

    # If first operand doesn't exist
    if len(parts) < 2:
        return Instruction(label, opcode, _LC=LC)

    op1 = parts[1]

    # The comma is optional
    if op1[-1] == ',':op1 = op1[:-1]
    operand1 = op1

    if (opcode in DATA_TRANSFER_INSTRUCTIONS or opcode in ARITHMETIC_INSTRUCTIONS) and operand1 not in REGISTERS:
        ERROR_FOUND = True
        print(f'On line {line} found illegal operand `{op1}` expected register')
        return

    if len(parts) > 2:
        operand2 = parts[2]
        if opcode in DATA_TRANSFER_INSTRUCTIONS or opcode in ARITHMETIC_INSTRUCTIONS or opcode in JUMP_INSTRUCTIONS:
            if parts[2] not in labels:
                backlog_labels[parts[2]] = (line, LC)    

    ins = Instruction(label, opcode, operand1, operand2, inst_type=inst_type, _LC=LC, line=line)

    if inst_type == 'mnemonic':
        LC += size
    elif opcode in {'ds', 'dc'}:
        LC += MEMORY_WIDTH

    return ins


'''
    In pass1 we will read the source code line by line
    and convert it to intermediate code
'''
def pass1() -> bool:
    global ERROR_FOUND, LC
    i = 0
    f = open(f'{FILE_NAME}')
    line = [l for l in re.split(r'\s+', f.readline()) if len(l) > 0]

    if line[0] == 'start':
        i = 1
        if len(line) == 2:
            LC = int(line[1])
            instructions.append(Instruction(mnemonic="start", operand1=LC, inst_type="directive", op1_type='constant', _LC=LC, line=i))
        else:
            instructions.append(Instruction(mnemonic="start", inst_type="directive", _LC=LC, line=i))

    while line := f.readline():
        line = line.strip()
        i += 1
        if len(line) > 0:
            ins = parse(line, i)
            if not ins:
                continue

            instructions.append(ins)

    for inst in instructions:
        if inst.operand1 in labels:
            inst.operand1_type = 'label'
        elif inst.operand1 in REGISTERS:
            inst.operand1_type = 'register'
        elif inst.operand1 in JUMP_INSTRUCTIONS:
            inst.operand1_type = 'jump cond'
        elif str(inst.operand1).isnumeric():
            inst.operand1_type = 'constant'

        if inst.operand2 in labels:
            inst.operand2_type = 'label'

    f.close()


def print_IC():
    print("------------------------Intermediate Code-------------------------")
    print('LC\tLabel\tMnemonic\tOperand1\tOperand2\tInst Type\tOperand1 Type\tOperand2 Type')
    for ins in instructions:
        print(ins)

def print_symbols():
    print("-------------------------Symbol Table----------------------------")
    print("Label Name\tLine Count")
    for key, val in labels.items():
        print(f"{key}\t\t{val}")


def error_or_execute():
    if backlog_labels:
        print(f'Error: There are {len(backlog_labels)} undefined labels in source code')
        for back in backlog_labels:
            print(f'In file {FILE_NAME} on line {backlog_labels[back][0]} label `{back}` is refered to but not declared anywhere in code', end=' ')

    elif not ERROR_FOUND:
        print_IC()
        print_symbols()


if __name__ == '__main__':
    pass1()
    error_or_execute()
