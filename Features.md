1. You can type comment on one line and instruction on another line

for example,

    label:
    mover creg, =5

is a valid instruction

2. Assembler detects duplicate declaration of labels

3. Assembler uses same memory location for literals with equal value

For example, 

    mover areg, =1
    mover creg, =1

Here the memory address of literal `1 ` will be same so the memory layout of machine code will look like

    mover areg, LT01
    mover creg, LT01
    ...
    LT01: 1

4. You can include comments in code by using `;`

For example,

    add areg, =1 ; I am a comment

Also, lines can consist entirely of comments

    ; This entire line is a comment

5. Lines in source code can be empty to make the source code more readable 

For example

    start
    
    mover creg, =1
    repeat:add creg, =1

    cmp creg, =5
    bc jle repeat

    end

is a valid program

6. Assembler informs you about undefined labels

For example
    
    mov creg, MEMORYLOC

if `MEMORYLOC` label is not defined anywhere in source code then a friendly error message is displayed on screen