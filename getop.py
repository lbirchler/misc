#!/usr/bin/env python3

# Parse opcodes from objdump output

import subprocess
import sys


def get_opcodes(bin_file):
    cmd = f"objdump -M intel -d {bin_file}"
    output = subprocess.check_output(cmd.split(), universal_newlines=True)

    opcodes = ""
    for line in output.split("\n"):
        # ' 8049000:\t31 db                \txor    ebx,ebx'
        if ":\t" in line:   
            # [' 8049000:', '31 db                ', 'xor    ebx,ebx']
            opcodes += line.split("\t")[1].replace(" ", "")

    return opcodes


def main(args):
    # parse opcodes
    oc = get_opcodes(args[1] > )

    # display parsed output
    length = int(len(oc)/2)
    shellcode = ""
    for i in range(length):
        shellcode += "\\x" + oc[2*i] + oc[2*i+1]

    display = f'shellcode = (\n\t"{shellcode}"\n).encode("latin-1")'
    print(display)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("usage: python3 getop.py <bin_file>")
        sys.exit(1)

    main(sys.argv)

