from variant1 import pass1, instructions, labels

def pass2():
    pass1('./ass3.asm')

    pass


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
    # if backlog_labels:
    #     print(f'Error: There are {len(backlog_labels)} undefined labels in source code')
    #     for back in backlog_labels:
    #         print(f'In file {FILE_NAME} on line {backlog_labels[back][0]} label `{back}` is refered to but not declared anywhere in code')
    print_IC()
    print_symbols()


if __name__ == '__main__':
    pass2()
    show_tables()
    errors()