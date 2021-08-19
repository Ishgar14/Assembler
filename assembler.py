from typing import Set, List

import re

# File Reading
PATH = './'
FILE_NAME = 'test3.asm'

# Constants needed for parser

# Set of all assembler directives
DIRECTIVES = {'start','end'}

# The values of table represent tuple of expected tokens
MNEMONIC_TABLE = {
    # Data transfer Instructions
    'mov': [('register', 'numeric_literal'),],
    'mover': [('register', 'label'),],
    'movem': [('register', 'label'),],

    # IO Instructions
    'read': [('label',)],
    'print': [('label',)],

    # Arithmetic Instructions
    'add': [('register', 'label'), ('register', 'numeric_literal')],
    'sub': [('register', 'label'), ('register', 'numeric_literal')],
    'mul': [('register', 'label'), ('register', 'label'), ('register', 'numeric_literal')],
    'div': [('register', 'label'), ('register', 'label'), ('register', 'numeric_literal')],
    'inc': [('register',)],
    'dec': [('register',)],

    # Branching Instructions
    'jnz': [('label',)],
    'jz': [('label',)],
    'jnc': [('label',)],
    'jc': [('label',)],
    'jlt': [('label',)],
    'jle': [('label',)],
    'jgt': [('label',)],
    'jge': [('label',)],
    'je': [('label',)],
    'jne': [('label',)],
    'jmp': [('label',)],

    # Memory Creation Instructions
    'ds': [('numeric_literal',)],
    'dc': [('numeric_literal',)],

    # Micellaneous
    'int': [('numeric_literal',)],
    'cmp': [('register', 'register'), ('register', 'label'), ('register', 'numeric_literal')],
    'nop': [],
}

REGISTERS = {
    'areg': 0, 
    'breg': 1,
    'creg': 2,
    'dreg': 3,
}

IO_INSTRUCTIONS = {
    'read', 'print'
}

JUMP_INSTRUCTIONS = {
    'je', 'jne', 'jz', 'jnz',
    'jl', 'jle', 'jg', 'jge',
    'jc', 'jnc', 'jp', 'jnp',
    'jmp'
}

OPCODES = {
    
}

ERROR_FOUND = False

class Instruction:
    def __init__(self, label, opcode, operand1, operand2, inst_type='mne'):
        self.label = label
        self.opcode = opcode
        self.operand1 = operand1
        self.operand2 = operand2
        self.instruction_type = inst_type

    def __repr__(self) -> str:
        return f"{self.label}\t{self.opcode}\t{self.operand1}\t\t{self.operand2}"


def is_valid_numeric_literal(num: str) -> bool:
    # It could be a hexadecimal value
    if num.startswith('0x'):
        return re.match('[a-zA-Z0-9]', num[2:]) is not None

    elif num.endswith('h') or num.endswith('H'):
        return re.match('[a-zA-Z0-9]', num[:-1]) is not None

    # Check for octal value
    elif num.startswith('0') and len(num) > 1:
        return num[1:].isnumeric()

    # Check for decimal value
    return num.isnumeric()


def get_token_type(token: str) -> str:
    if token in REGISTERS:
        return 'register'
    elif token in DIRECTIVES:
        return 'directive'
    elif token in labels:
        return 'label'
    elif is_valid_numeric_literal(token):
        return 'numeric_literal'
    else:
        return None

# This function checks whether expected token and given token match
# If they do then return empty string otherwise return string with error message


def check(expected: List[str], got: str, line: int) -> str:
    expected = (set(expected))
    token_type = get_token_type(got.lower())

    if token_type in expected or 'label' in expected:
        return ''

    expected = list(expected)
    
    if len(expected) > 1:
        expectations = ', '.join(expected[:-1]) + ' or ' + expected[-1]
        return f'On line {line} expected any of {expectations} but got `{got}`'
    else:
        return f'On line {line} expected {expected[0]} but got `{got}`'


# This function parses one instruction at a time and returns an object of class `Instruction`
def parse(inst: str, line: int) -> Instruction:
    global ERROR_FOUND
    label, opcode, operand1, operand2 = "", "", "", ""

    parts = list(filter(lambda x: len(x) > 0, re.split(r'\s+|,', inst)))

    if ':' in parts[0] and parts[0][-1] != ':':
        # properly break the instruction into parts
        backup = parts[1:]
        parts = parts[0].split(':')
        parts[0] += ':'
        parts.extend(backup)
    # print(parts)

    # if first component is a label
    if parts[0][-1] == ':':
        label = parts[0][:-1]

        if label in backlog_labels:
            backlog_labels.remove(label)
        
        if label in labels:
            ERROR_FOUND = True
            print(f"Redeclared the label {label} on line {line}")
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
        expected_tokens = MNEMONIC_TABLE[opcode.lower()]
        
        if len(expected_tokens) > 0:
            pass
            # exptected_tokens = [tup[0] for tup in exptected_tokens]
        else:
            return Instruction(label, opcode, operand1, operand2)
    
    else:
        ERROR_FOUND = True
        print(
            f"Unknown instruction `{parts[0]}` on line {line} in file '{FILE_NAME}'")
        return None

    # if len(parts) - 1 != len(expected_tokens):
    #     print(f"Incorrect number of operands in {FILE_NAME} on line {line}")
    #     print(f"Expected {len(expected_tokens)} tokens got {len(parts) - 1}")
    #     ERROR_FOUND = True
    #     return None

    # Check for first operand
    op1 = parts[1]

    # The comma is optional
    if op1[-1] == ',':
        op1 = op1[:-1]

    err = check(expected_tokens, op1, line)
    
    if err and opcode.lower() not in JUMP_INSTRUCTIONS:
        ERROR_FOUND = True
        print(err)
        return None
    else:
        operand1 = op1.lower()
        
        if (opcode in JUMP_INSTRUCTIONS or opcode in IO_INSTRUCTIONS) and op1 not in labels:
            backlog_labels.add(op1)

    if len(parts) > 2:
        expected_tokens = MNEMONIC_TABLE[opcode.lower()]
        expected_tokens = [tup[1] for tup in expected_tokens]
    
        # Check for second operand
        if err := check(expected_tokens, parts[2], line):
            ERROR_FOUND = True
            print(err)
            return None
        else:
            operand2 = parts[2].lower()

    return Instruction(label, opcode, operand1, operand2)


instructions: List[Instruction] = []
labels: Set[str] = set()
backlog_labels: Set[str] = set()


def main():
    i = 0
    f = open(f'{PATH}{FILE_NAME}')
    
    while line := f.readline():
        if len(line.strip()) == 0:
            continue

        i += 1
        comment_index = line.find(';')
        
        if comment_index == -1:
            ins = parse(line, i)
            instructions.append(ins)

        else:
            line = line[:comment_index]
    
            if len(line) > 0:
                ins = parse(line, i)
                instructions.append(ins)

        # print(line)
        # print(ins)
    
    f.close()


def print_instructions():
    print("Label\tOpcode\tOperand1\tOperand2")
    
    for ins in instructions:
        if ins.instruction_type != 'directive':
            print(ins)


if __name__ == '__main__':
    main()
    if backlog_labels:
        print(f"Warning: There are {len(backlog_labels)} undefined labels in source code")
        print(backlog_labels)

    elif not ERROR_FOUND:
        print_instructions()


    # print(labels)
    # print(backlog_labels)
