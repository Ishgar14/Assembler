start 101
mover creg, one

loop: add creg, one
cmp creg, N
bc jle loop

N: dc 5
one: dc 1
end