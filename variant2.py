from variant1 import pass1, instructions, labels
import re

FILE_NAME = './ass3.asm'
MACHINE_CODE = []

def pass2():
    instructions = pass1(FILE_NAME)

    for ins in instructions:
        IC = ins.interm()

        # We dont need assembler directives statements
        if 'AD' in ins.instruction_type:
            continue

        if 'IS' in ins.instruction_type:
            operation = get_digit(ins.instruction_type)
            first_num = get_digit(ins.operand1_type)

            # If second operand is a symbol
            if 'S' in ins.operand2_type:
                # Then get its LC
                symbols = {lab[0]: str(lab[1]) for lab in labels}
                second_num = symbols[ins.operand2]
            else:
                second_num = get_digit(ins.operand2_type)

            MC = ' '.join([operation, first_num, second_num])
            MC = str(ins.LC) + ': ' + MC
            MACHINE_CODE.append(MC)
        
        else:
            declarative = str(ins.LC) + ': ' + ins.operand1
            MACHINE_CODE.append(declarative)
    
    return MACHINE_CODE

# Returns first occurence of a number present in given string
def get_digit(line: str) -> str:
    num = ""
    i = 0

    while i < len(line):
        while line[i].isdigit():
            num += line[i]
            i += 1
            if i >= len(line):
                return num

        while not line[i].isdigit():
            i += 1
            if i >= len(line):
                return num

    return num

def print_IC():
    print("------------------------Intermediate Code-------------------------")
    print('Sr\tLC\tLabel\tMnemonic\tOperand1\tOperand2\t\tIC', end='\n\n')
    for i, ins in enumerate(instructions):
        print(i + 1, '\t', ins, ins.interm())

def print_symbols():
    print("-------------------------Symbol Table----------------------------")
    print("Index\tLabel Name\tLine Count\tValue")
    for index, (key, lc, val) in enumerate(labels):
        print(f"{index + 1}\t{key}\t\t{lc}\t\t{val}")


def print_machinecode():
    print('Machine Code'.center(65, '-'))

    for mc in MACHINE_CODE:
        print(mc)


def errors():
    label_names = set()
    print('Errors'.center(65, '-'))

    # Find duplicate definitions of labels
    for index, label in enumerate(labels):
        if label[0] in label_names:
            print(f'Duplicate label "{label[0]}" on statement {index + 1}')
        else:
            label_names.add(label[0])

    # Find undefined symbols
    registers = {'areg', 'breg', 'creg', 'dreg'}
    for index, ins in enumerate(instructions):
        if ins.operand1 and ins.mnemonic.lower() != 'bc':
            if ins.operand1 not in registers | label_names and not str(ins.operand1).isdigit():
                print(f'Undefined label "{ins.operand1}" on statement {index + 1}')
        if ins.operand2:
            if ins.operand2 not in registers | label_names and not str(ins.operand2).isdigit():
                print(f'Undefined label "{ins.operand2}" on statement {index + 1}')


def show_tables():
    print_IC()
    print_symbols()
    print_machinecode()


if __name__ == '__main__':
    pass2()
    show_tables()
    errors()
