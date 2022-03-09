#!/usr/bin/python3

# objdump single function and output shellcode

import subprocess
import sys

def usage():
    print("""objdump single function and output shellcode
Usage: objshell.py objfile function [-c]

Options:
    -c  Output shellcode in c (default is python)

Examples:
    single function
    objshell.py objfile function

    multiple functions
    objshell.py objfile function1,function2

    print shellcode in c
    objshell.py objfile function1 -c
""" 
)

def main():
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    
    if len(args) != 2:
        usage()
        sys.exit(1)

    shellcode_output = "python" 
    if "-c" in opts:
        shellcode_output = "c"

    objfile = sys.argv[1]
    functions = sys.argv[2].split(",")

    for function in functions:
        print("[+] %s" % function)

        # objdump function
        ps = subprocess.Popen(("objdump", "-d", "-M", "intel",objfile), stdout=subprocess.PIPE)
        disas = subprocess.check_output(("awk", "-v", "RS=", '/^[[:xdigit:]]+ <%s>/' % function), stdin=ps.stdout).decode("latin")

        # parse opcodes
        opcodes = ""
        for line in disas.split("\n"):
            if ":\t" in line:   
                opcodes += line.split("\t")[1].replace(" ", "")

        # generate shellcode
        length = int(len(opcodes)/2)
        shellcode = '"'
        for i in range(length):
            shellcode += "\\x" + opcodes[2*i] + opcodes[2*i+1]
            if i > 0 and i % 8 == 7:
                shellcode += '"\n\t"' 
        shellcode += '"'

        print(disas) 
        if shellcode_output == "c":
            print("char shellcode[] = \n\t%s;\n" % shellcode)
        else:
            print("shellcode = (\n\t%s\n).encode('latin')\n" % shellcode)
        print("length: %d\n" % len(opcodes))

if __name__ == "__main__":
    main()
