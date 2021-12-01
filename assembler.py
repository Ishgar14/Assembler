from typing import Dict, List, Tuple
import re

# File Reading
FILE_NAME = './ass1.asm'

# Constants needed for parser
LC = 0
MEMORY_WIDTH = 1
REGISTERS = {'areg': 1, 'breg': 2, 'creg': 3, 'dreg': 4, }

# Set of all assembler directives
# The tuple represents (opcode, number of tokens)
DECLARATIVES = {'ds': (1, 2), 'dc': (2, 2), }
DIRECTIVES = {
    'start': (1, 2),
    'end': (2, 1),
    'org': (3, 2),
    'ltorg': (4, 1)
} | DECLARATIVES
IO_INSTRUCTIONS = {'read': (1, 2), 'print': (2, 2)}
DATA_TRANSFER_INSTRUCTIONS = {'movem': (3, 3), 'mover': (4, 3)}
ARITHMETIC_INSTRUCTIONS = { 'add': (5, 3), 'sub': (6, 3), 'mul': (7, 3), 'div': (8, 3), 'cmp': (9, 3)}
JUMP_INSTRUCTIONS = { 'bc': (10, 3), }
JUMP_CONDITIONS = { 'lt': 1, 'le': 2, 'eq': 3, 'gt': 4, 'ge': 5, 'ne': 6, }

# The set of valid symbols
MNEMONIC_TABLE = ARITHMETIC_INSTRUCTIONS | JUMP_INSTRUCTIONS | IO_INSTRUCTIONS  \
    | DATA_TRANSFER_INSTRUCTIONS

ERROR_FOUND = False


class Instruction:
    def __init__(self, label: str = "", mnemonic: str = "", operand1: str = "", operand2: str = "",
                    inst_type: str = 'IS', op1_type='', op2_type='', *,
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
        return f'{self.LC}\t{self.label}\t{self.mnemonic}\t\t{self.operand1}\t\t{self.operand2}\t\t'

    def interm(self) -> str:
        return f'{self.instruction_type}' + \
            f' {self.operand1_type} {self.operand2_type}'


instructions: List[Instruction] = []

labels: List[Tuple[str, int, str]] = []
backlog_labels: Dict[str, int] = {}

for_ref_labels = set()
label_names = lambda lab: set(lab[0] for lab in labels)

# This function parses one instruction at a time and returns an object of class `Instruction`
def parse(inst: str, line: int) -> Instruction:
    global ERROR_FOUND, LC, literal_count
    label, mnemo, operand1, operand2, inst_type = '', '', '', '', 'IS'
    parts = re.split(r'\s+', inst)

    # if first component is a label
    if parts[0][-1] == ':':
        label = parts[0][:-1]

        if label in backlog_labels:
            del backlog_labels[label]

        if label in for_ref_labels:
            names = [lab[0] for lab in labels]
            index = names.index(label)
            labels[index] = [label, LC]
        else:
            labels.append([label, LC])
        parts = parts[1:]

    # If first part is an assembler directive
    if parts[0].lower() in DIRECTIVES:
        key = parts[0].lower()
        if parts[0].lower() in {'dc', 'ds'}:
            inst_type = (f'(DL, {str(DECLARATIVES[key][0])})')
        else:
            inst_type = (f'(AD, {str(DIRECTIVES[key][0])})')
        mnemo = parts[0].lower()

    # check for opcode
    elif parts[0].lower() in MNEMONIC_TABLE:
        mnemo = parts[0].lower()
        inst_type = (f'(IS, {str(MNEMONIC_TABLE[mnemo][0])})')
        size = MNEMONIC_TABLE[mnemo][1]

    else:
        ERROR_FOUND = True
        print(f'Unknown instruction `{parts[0]}` on line {line} in file "{FILE_NAME}"')
        return

    # If first operand doesn't exist
    if len(parts) < 2:
        return Instruction(label, mnemo, operand1, operand2, _LC=LC, inst_type=inst_type)

    op1 = parts[1]

    # The comma is optional
    if op1[-1] == ',':op1 = op1[:-1]
    operand1 = op1

    if (mnemo in DATA_TRANSFER_INSTRUCTIONS | ARITHMETIC_INSTRUCTIONS) and operand1 not in set(REGISTERS) | label_names(labels):
        ERROR_FOUND = True
        print(f'On line {line} found illegal operand `{op1}`')
        return

    if len(parts) > 2:
        operand2 = parts[2]
        if parts[2] not in REGISTERS and parts[2] not in label_names(labels):
            backlog_labels[parts[2]] = (line, LC)
            labels.append([parts[2], LC])
            for_ref_labels.add(parts[2])

    ins = Instruction(label, mnemo, operand1, operand2, inst_type=inst_type, _LC=LC, line=line)

    if 'IS' in inst_type:
        LC += 2
    elif mnemo in DECLARATIVES:
        if mnemo == 'dc':   LC += MEMORY_WIDTH
        elif mnemo == 'ds': LC += int(op1) * MEMORY_WIDTH

    return ins


def pass1() -> bool:
    global ERROR_FOUND, LC
    i = 0
    f = open(f'{FILE_NAME}')
    line = [l for l in re.split(r'\s+', f.readline()) if len(l) > 0]

    if line[0] == 'start':
        i = 1
        inst_type = (f'(AD, {str(DIRECTIVES["start"][0])})')
        if len(line) == 2:
            LC = int(line[1])
            instructions.append(Instruction(mnemonic="start", operand1=LC, inst_type=inst_type, op1_type=f'(C, {LC})', _LC=LC, line=i))
        else:
            instructions.append(Instruction(mnemonic="start", inst_type=inst_type, _LC=LC, line=i))

    while line := f.readline():
        line = line.strip()
        i += 1
        if len(line) == 0:
            continue

        inst = parse(line, i)
        if not inst:
            continue
        
        instructions.append(inst)

        label_dict = {lab[0]: lab[1] for lab in labels}
        label_name_list = [lab[0] for lab in labels]

        if inst.operand1 in label_dict:
            inst.operand1_type = (f'(S, {str(label_name_list.index(inst.operand1))})')
        elif inst.operand1 in REGISTERS:
            inst.operand1_type = (f'(R, {str(REGISTERS[inst.operand1])})')
        elif inst.operand1 in JUMP_CONDITIONS:
            inst.operand1_type = (f'({str(JUMP_CONDITIONS[inst.operand1])})')
        elif str(inst.operand1).isnumeric():
            inst.operand1_type = (f'(C, {str(inst.operand1)})')

        if inst.operand2 in label_dict:
            inst.operand2_type = (f'(S, {str(label_name_list.index(inst.operand2) + 1)})')
        elif inst.operand2 in REGISTERS:
            inst.operand2_type = (f'(R, {str(REGISTERS[inst.operand2])})')

    f.close()


def print_IC():
    print("------------------------Intermediate Code-------------------------")
    print('LC\tLabel\tMnemonic\tOperand1\tOperand2\t\tIC', end='\n\n')
    for ins in instructions:
        print(ins, ins.interm())

def print_symbols():
    print("-------------------------Symbol Table----------------------------")
    print("Index\tLabel Name\tAddress")
    for index, (key, lc) in enumerate(labels):
        print(f"{index + 1}\t{key}\t\t{lc}")


def error_or_execute():
    if backlog_labels:
        print(f'Error: There are {len(backlog_labels)} undefined labels in source code')
        for back in backlog_labels:
            print(f'In file {FILE_NAME} on line {backlog_labels[back][0]} label `{back}` is refered to but not declared anywhere in code')

    elif not ERROR_FOUND:
        print_symbols()
        print_IC()


if __name__ == '__main__':
    pass1()
    error_or_execute()
