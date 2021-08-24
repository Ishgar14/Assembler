from typing import Dict, List

import re

# File Reading
# PATH = './'
FILE_NAME = './test.asm'


# Constants needed for parser
LC = 0
MEMORY_WIDTH = 1
REGISTERS = {'areg': 0, 'breg': 1, 'creg': 2, 'dreg': 3, }

# Set of all assembler directives
# The tuple represents (opcode, size of instruction)
MEMORY_DIRECTIVES = {'ds': (10, 2), 'dc': (11, 2), 'ltorg': (12, 1)}
DIRECTIVES = {
    'start': (0, 2),
    'end': (0, 1),
    'org': (0, 2)
} | MEMORY_DIRECTIVES


IO_INSTRUCTIONS = {'read': (1, 2), 'print': (2, 2)}

DATA_TRANSFER_INSTRUCTIONS = {'movem': (3, 3), 'mover': (4, 3), 'mov': (0, 3)}

ARITHMETIC_INSTRUCTIONS = {
    'add': (5, 3),
    'sub': (6, 3),
    'mul': (7, 3),
    'div': (8, 3),
    'cmp': (9, 3)
}

JUMP_INSTRUCTIONS = {
    'bc': (10, 3),
    'je': (0, 2), 'jne': (1, 2), 'jz': (0, 2), 'jnz': (1, 2),
    'jl': (2, 2), 'jle': (2, 2), 'jg': (4, 2), 'jge': (5, 2),
    'jc': (6, 2), 'jnc': (7, 2), 'jp': (8, 2), 'jnp': (9, 2),
    'jmp': (10, 2), 'any': (11, 3)
}

MICELLANEOUS_INSTRUCTIONS = {'int': (0, 2), 'nop': (0, 1)}

# The set of valid symbols
MNEMONIC_TABLE = ARITHMETIC_INSTRUCTIONS | JUMP_INSTRUCTIONS | IO_INSTRUCTIONS  \
    | DATA_TRANSFER_INSTRUCTIONS | MICELLANEOUS_INSTRUCTIONS

ERROR_FOUND = False


class Instruction:
    def __init__(self, label: str, opcode: str, operand1: str, operand2: str,
                    inst_type: str = "mnemonic", *, line: int = -1, _LC: int = -1):
        self.label = label
        self.opcode = opcode
        self.operand1 = operand1
        self.operand2 = operand2
        self.instruction_type = inst_type
        self.line = line  # stores line number for instruction in source code
        self.LC = _LC     # stores line counter for instruction in machine and intermediate code

    def __repr__(self) -> str:
        return f"{self.label}\t{self.opcode}\t{self.operand1}\t\t{self.operand2}"


def split(inst: str) -> List[str]:
    parts = list(filter(lambda x: len(x) > 0, re.split(r'\s+|,', inst)))

    if ':' in parts[0] and parts[0][-1] != ':':
        # properly break the instruction into parts
        backup = parts[1:]
        parts = parts[0].split(':')
        parts[0] += ':'
        parts.extend(backup)

    return parts


def directive_processor(parts: List[str], line: int) -> Instruction:
    global LC, ERROR_FOUND, literals
    label, opcode, operand1, operand2 = "", "", "", ""

    p = parts[0].lower()
    if p == 'start':
        if len(parts) > 1:
            if not parts[1].isnumeric():
                ERROR_FOUND = True
                print(
                    f"On line {line} expected a number but got {type(parts[1])}")
                return None

            else:
                LC = int(parts[1])
        else:
            LC = 0
        
        return Instruction('', 'start', '', '', 'directive', _LC=0)

    elif p == 'end':
        return Instruction(label, "end", operand1, operand2, "directive", _LC=LC)

    elif p == 'org':
        if len(parts) < 2:
            ERROR_FOUND = True
            print(f"Expected one integer after `org` on line {line}")
            return None
        else:
            LC = int(parts[1])
        ins = Instruction(
            label, parts[0].lower(), operand1, operand2, "directive")
        return ins

    elif p == 'ds':
        times = int(parts[1])
        collection = []

        for _ in range(times):
            ins = Instruction(
                label, parts[0].lower(), 0, operand2, "memory", _LC=LC)
            LC += MEMORY_WIDTH
            collection.append(ins)
        return collection

    elif p == 'dc':
        if len(parts) > 1:
            operand1 = parts[1]
        if len(parts) > 2:
            operand2 = parts[2]

        ins = Instruction(
            label, parts[0].lower(), operand1, operand2, "memory", LC=LC)
        # ins.LC = LC
        LC += DIRECTIVES[parts[0].lower()][1]
        return ins
    
    elif p == 'ltorg':
        for key in backlog_literals:
            instructions.append(Instruction(backlog_literals[key], key, '', '', "memory", _LC=LC))
            LC += MEMORY_WIDTH
        
        literals = literals | backlog_literals
        backlog_literals.clear()

        return Instruction('', parts[0], '', '', "directive")



# This function parses one instruction at a time and returns an object of class `Instruction`
def parse(inst: str, line: int) -> Instruction:
    global ERROR_FOUND, LC, literal_count
    label, opcode, operand1, operand2 = "", "", "", ""

    parts = split(inst)

    # if first component is a label
    if parts[0][-1] == ':':
        label = parts[0][:-1]

        if label in backlog_labels:
            del backlog_labels[label]

        if label in labels:
            ERROR_FOUND = True
            print(f"Redeclared the label `{label}` on line {line}")
            return None

        # labels.add(label)
        labels[label] = LC
        parts = parts[1:]

    # If first part is a assembler directive
    if parts[0].lower() in DIRECTIVES:
        return directive_processor(parts, line)

    # check for opcode
    if parts[0].lower() in MNEMONIC_TABLE:
        opcode = parts[0]
        size = MNEMONIC_TABLE[parts[0].lower()][1]

        if len(parts) != size:
            ERROR_FOUND = True
            print(
                f"On line {line} `{inst.strip()}`\nExpected {size} tokens but got {len(parts)}")
            return

    else:
        ERROR_FOUND = True
        print(
            f"Unknown instruction `{parts[0]}` on line {line} in file '{FILE_NAME}'")
        return

    # Check for first operand
    if len(parts) < 2:
        ins = Instruction(label, opcode, operand1, operand2)
        ins.LC = LC
        return ins

    op1 = parts[1]

    # The comma is optional
    if op1[-1] == ',':
        op1 = op1[:-1]

    if opcode in IO_INSTRUCTIONS:
        operand1 = op1
    else:
        operand1 = op1.lower()

    if opcode in DATA_TRANSFER_INSTRUCTIONS and operand1 not in REGISTERS:
        ERROR_FOUND = True
        print(f"Illegal operand `{op1}` expected register")
        return

    if len(parts) > 2:
        if opcode in DATA_TRANSFER_INSTRUCTIONS or opcode in ARITHMETIC_INSTRUCTIONS:

            # if second part is a literal
            if parts[2].startswith("=") and parts[2][1:].isnumeric():
                val = int(parts[2][1:])

                # if the literal already exists in backlog
                # then change operand2 to address of literal in instruction
                if val in backlog_literals:
                    ins = Instruction(label, opcode, operand1, backlog_literals[val], _LC=LC)
                    LC += size
                    return ins

                literal_label = "LT" + str(literal_count).zfill(2)

                # make sure label of literal doesnt collide with users labels
                while literal_label in labels:
                    literal_count += 1
                    literal_label = "LT" + str(literal_count).zfill(2)

                backlog_literals[val] = literal_label
                literal_count += 1
                operand2 = literal_label

            else:
                backlog_labels[parts[2]] = (line, LC)
        else:
            operand2 = parts[2]

    ins = Instruction(label, opcode, operand1, operand2, _LC=LC)
    LC += size
    return ins


instructions: List[Instruction] = []

labels: Dict[str, int] = {}
backlog_labels: Dict[str, int] = {}

literals: Dict[str, int] = {}
backlog_literals: Dict[int, str] = {}
literal_count = 0


def pass1() -> bool:
    global ERROR_FOUND, LC
    all_good = True
    i = 0
    f = open(f'{FILE_NAME}')

    line = split(f.readline())

    if line[0] == 'start' and len(line) == 2:
        LC = int(line[1])

    while line := f.readline():
        if len(line.strip()) == 0:
            continue

        i += 1
        comment_index = line.find(';')

        if comment_index > -1:
            line = line[:comment_index]

        if len(line) > 0:
            ins = parse(line, i)
            if ins:
                if isinstance(ins, list):
                    for ii in ins:
                        ii.line = i
                        instructions.append(ii)
                else:
                    ins.line = i  # + LC
                    instructions.append(ins)
            else:
                all_good = False

    f.close()
    return all_good

'''
    In pass 2 we will just write the literals at bottom of code space in machine/intermediate code
'''
def pass2() -> bool:
    global LC, literals
    all_good = True

    for key in backlog_literals:
        instructions.append(Instruction(backlog_literals[key], key, '', '', "memory", _LC=LC))
        LC += MEMORY_WIDTH
    
    literals = literals | backlog_literals
    backlog_literals.clear()
    return all_good


def print_instructions():
    print("Label\tOpcode\tOperand1\tOperand2")

    for ins in instructions:
        if ins.instruction_type != "directive":
            print(ins)


# This function ocnverts given parameters to their equivalent codes
def mnemonic_to_opcode(mnemo, operand1, operand2) -> tuple:
    if mnemo in MNEMONIC_TABLE:
        mnemo = MNEMONIC_TABLE[mnemo][0]
    elif mnemo in DIRECTIVES:
        mnemo = DIRECTIVES[mnemo][0]

    if operand1 in labels or mnemo in IO_INSTRUCTIONS:
        operand1 = labels[operand1]
    elif operand1 in MNEMONIC_TABLE:
        operand1 = MNEMONIC_TABLE[operand1][0]

    if operand1 in REGISTERS:
        operand1 = REGISTERS[operand1]
    if operand2 and operand2 in labels:
        operand2 = labels[operand2]

    return (mnemo, operand1, operand2)


def output(fname="output.txt", *, opcodenumbers=False):
    f = open(fname, 'w')

    for inst in instructions:
        if inst.instruction_type == 'directive':
            if inst.opcode not in MEMORY_DIRECTIVES:
                continue

        opcode = inst.opcode
        op1 = inst.operand1
        op2 = inst.operand2

        if opcode in MEMORY_DIRECTIVES:
            opcode = ''
        if opcodenumbers:
            opcode, op1, op2 = mnemonic_to_opcode(opcode, op1, op2)

        # print(opcode, op1, op2)

        f.write(f"{inst.LC}: {opcode} {op1} {op2}\n")

    f.close()


def error_or_execute():
    if backlog_labels:
        print(
            f"Error: There are {len(backlog_labels)} undefined labels in source code")
        for back in backlog_labels:
            print(
                f"In file {FILE_NAME} on line {backlog_labels[back][0]} label `{back}` is refered to but not declared anywhere in code", end=' ')

    elif not ERROR_FOUND:
        print_instructions()
        output(opcodenumbers=False)


if __name__ == '__main__':
    if not (pass1() and pass2()):
        print("Something went wrong")

    error_or_execute()
