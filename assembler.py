from typing import Set, List

import re

# File Reading
PATH = './'
FILE_NAME = 'test3.asm'

# Constants needed for parser

# Set of all assembler directives
DIRECTIVES = {'start','end', 'ds', 'dc'}

REGISTERS = { 'areg', 'breg', 'creg', 'dreg',}

IO_INSTRUCTIONS = { 'read', 'print' }

DATA_TRANSFER_INSTRUCTIONS = { 'movem', 'mover' , 'mov' }

ARITHMETIC_INSTRUCTIONS = { 'add', 'sub', 'mul', 'div', 'inc', 'dec', 'cmp' }

JUMP_INSTRUCTIONS = {
    'je', 'jne', 'jz', 'jnz',
    'jl', 'jle', 'jg', 'jge',
    'jc', 'jnc', 'jp', 'jnp',
    'jmp'
}

MICELLANEOUS_INSTRUCTIONS = { 'int', 'nop' }

# The set of valid symbols
MNEMONIC_TABLE = ARITHMETIC_INSTRUCTIONS | JUMP_INSTRUCTIONS | IO_INSTRUCTIONS  \
    | DIRECTIVES | DATA_TRANSFER_INSTRUCTIONS | MICELLANEOUS_INSTRUCTIONS

ERROR_FOUND = False

class Instruction:
    def __init__(self, label, opcode, operand1, operand2, inst_type='mne'):
        self.label = label
        self.opcode = opcode
        self.operand1 = operand1
        self.operand2 = operand2
        self.instruction_type = inst_type
        self.line = -1

    def __repr__(self) -> str:
        return f"{self.label}\t{self.opcode}\t{self.operand1}\t\t{self.operand2}"


def split(inst: str) -> list:
    parts = list(filter(lambda x: len(x) > 0, re.split(r'\s+|,', inst)))

    if ':' in parts[0] and parts[0][-1] != ':':
        # properly break the instruction into parts
        backup = parts[1:]
        parts = parts[0].split(':')
        parts[0] += ':'
        parts.extend(backup)
    
    return parts

# This function parses one instruction at a time and returns an object of class `Instruction`
def parse(inst: str, line: int) -> Instruction:
    global ERROR_FOUND
    label, opcode, operand1, operand2 = "", "", "", ""

    parts = split(inst)

    # if first component is a label
    if parts[0][-1] == ':':
        label = parts[0][:-1]

        if label in backlog_labels:
            backlog_labels.remove(label)
        
        if label in labels:
            ERROR_FOUND = True
            print(f"Redeclared the label `{label}` on line {line}")
            return None
        
        labels.add(label)
        parts = parts[1:]

    # If first part is a assembler directive
    if parts[0].lower() in DIRECTIVES:
        p = parts[0].lower()
        if p == 'start':
            if  len(parts) > 1 and not parts[1].isnumeric:
                print(f"Expected a number but got {type(parts[1])}")
                return None
        elif p == 'end':
            return Instruction(label, opcode, operand1, operand2, "directive")
        
        return Instruction(label, opcode, operand1, operand2, "directive")
            

    # check for opcode
    if parts[0].lower() in MNEMONIC_TABLE:
        opcode = parts[0]
    
    else:
        ERROR_FOUND = True
        print(
            f"Unknown instruction `{parts[0]}` on line {line} in file '{FILE_NAME}'")
        return None

    # Check for first operand
    if len(parts) < 2:
        return Instruction(label, opcode, operand1, operand2)

    op1 = parts[1]

    # The comma is optional
    if op1[-1] == ',':
        op1 = op1[:-1]

    operand1 = op1.lower()
    
    # if (opcode in JUMP_INSTRUCTIONS or opcode in IO_INSTRUCTIONS) and op1 not in labels:
    #     backlog_labels.add(op1)

    if len(parts) > 2:
        if opcode in DATA_TRANSFER_INSTRUCTIONS and not parts[2].isnumeric():
            # labels.add(parts[2])
            if parts[2] in backlog_labels:
                backlog_labels.remove(parts[2])
        
        operand2 = parts[2].lower()

    return Instruction(label, opcode, operand1, operand2)


instructions: List[Instruction] = []
labels: Set[str] = set()
backlog_labels: Set[str] = set()


def main():
    i, LC = 0, 0
    f = open(f'{PATH}{FILE_NAME}')

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
                ins.line = i + LC
                instructions.append(ins)
    
    f.close()


def print_instructions():
    print("Label\tOpcode\tOperand1\tOperand2")
    
    for ins in instructions:
        if ins.instruction_type != 'directive':
            print(ins)


if __name__ == '__main__':
    main()
    if backlog_labels:
        print(f"Error: There are {len(backlog_labels)} undefined labels in source code")
        for back in backlog_labels:
            print(back, end=' ')

    elif not ERROR_FOUND:
        print_instructions()

    # print(labels)
