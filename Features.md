1. Assembler detects duplicate declaration of labels

2. Lines in source code can be empty to make the source code more readable 

For example

    start
    
    mover creg, one
    repeat:add creg, one

    cmp creg, five
    bc jle repeat

    one: dc 1
    five: dc 5
    
    end

is a valid program

3. Assembler informs you about undefined labels

For example
    
    mover creg, MEMORYLOC

if `MEMORYLOC` label is not defined anywhere in source code then a friendly error message is displayed on screen