from typing import List, Tuple

# TODO: Implement error checking

KEYWORDS = []
DELIMITERS = r"(){}[],;"
OPERATOR = r'=<>+-*/&|'

def classify(word: str) -> str:
    if not word or len(word) == 0: 
        return None

    if word in DELIMITERS:
        return 'delimiter'
    elif word in KEYWORDS:
        return 'keyword'
    elif word in OPERATOR:
        return 'operator'
    elif word.isnumeric():
        return 'constant'
    elif word.isalnum() and word[0].isalpha:
        return 'identifier'
    else:
        return None

# This function parses one line and returns list of tuple of (line number, lexeme, token type)
def parse_line(line: str, linenumber: int) -> List[Tuple[int, str, str]]:
    token_list = []
    prev, now = 0, 0
    i = 0
    while i < len(line):
        if line[i].isalnum():
            now += 1
        elif line[i] == ' ':
            if line[prev] == ' ': prev += 1
            word = line[prev:i]
            
            if not word:
                prev = now = i
                i += 1
                continue

            classification = classify(word)
            if not classification:
                print("The fuq did you just type? ws '", word, "'", sep="")
            else:
                token_list.append((linenumber, word, classification))
            
            # i += 1
            prev, now = now, i + 1

        elif line[i] in DELIMITERS:
            if prev < now:
                if line[prev] == ' ': prev += 1
                word = line[prev:i]

                if word:
                    classification = classify(word)

                    if not classification:
                        print("The line is '", word, "'" , sep='')
                    else:
                        token_list.append((linenumber, word, classification))
            
            # if token_list[-1][2] != 'delimiter':
            token_list.append((linenumber, line[i], 'delimiter'))
            prev, now = i + 1, i + 2
        
        elif line[i] in OPERATOR:
            if line[i+1] in OPERATOR:
                token_list.append((linenumber, line[i:i+2], 'operator'))
                i += 1
            else:
                token_list.append((linenumber, line[i], 'operator'))
            prev = now = i + 1
        
        elif line[i] in '\'"':
            prev = i
            i += 1
            while line[i] not in '\'"':
                i += 1

            token_list.append((linenumber, line[prev:i+1], 'constant'))
            prev = now = i

        i += 1

    return token_list


# This function initializes some of the global variables
def setup():
    with open('./keywords.txt', 'r') as keys:
        for keyword in keys:
            KEYWORDS.append(keyword.lower().strip())


def main(filename: str):
    all_tokens = []

    with open(filename, 'r') as f:
        linenumber = 1
        for line in f.readlines():
            if '//' in line:
                line = line[:line.index('//')]

            tokens = parse_line(line.strip(), linenumber)
            
            all_tokens.extend(tokens)
            linenumber += 1

    lexeme_padding = max([len(t[1]) for t in all_tokens])
    print("Line Number", "Lexeme".ljust(lexeme_padding), "Token Type")
    for (ln, lexeme, ttype) in all_tokens:
        print(str(ln).center(11), lexeme.ljust(lexeme_padding), ttype)
    

if __name__ == '__main__':
    setup()
    main('./ass6.c')