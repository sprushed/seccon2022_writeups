# find flag

Task source:
```python
#!/usr/bin/env python3.9
import os

FLAG = os.getenv("FLAG", "FAKECON{*** REDUCTED ***}").encode()

def check():
    try:
        filename = input("filename: ")
        if open(filename, "rb").read(len(FLAG)) == FLAG:
            return True
    except FileNotFoundError:
        print("[-] missing")
    except IsADirectoryError:
        print("[-] seems wrong")
    except PermissionError:
        print("[-] not mine")
    except OSError:
        print("[-] hurting my eyes")
    except KeyboardInterrupt:
        print("[-] gone")
    return False

if __name__ == '__main__':
    try:
        check = check()
    except:
        print("[-] something went wrong")
        exit(1)
    finally:
        if check:
            print("[+] congrats!")
            print(FLAG.decode())
```

## Solution

So we have an input function with a bunch of exception catches. We need to somehow get to the 'print flag' statement. The first thing I thought about is sending null byte and without further understanding of what's going on and how to bypass the exceptions I just typed:
```bash
echo '\x00' | nc find-flag.seccon.games 10042
```

And simply got the flag :)
