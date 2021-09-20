from variant1 import pass1, instructions, labels

FILE_NAME = './ass3.asm'
MACHINE_CODE = []

def pass2():
    instructions = pass1(FILE_NAME)

    for ins in instructions:
        IC = ins.interm()
        if 'IS' not in IC:
            continue

        MC = ' '.join(list(filter(lambda x: x.isdigit(), IC)))
        MC = str(ins.LC) + ': ' + MC
        MACHINE_CODE.append(MC)
    
    return MACHINE_CODE


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
