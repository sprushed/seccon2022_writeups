# noiseccon

In this task we're given an application that generates noisy image from flag
using [perlin noise algorithm](https://en.wikipedia.org/wiki/Perlin_noise).
Only thing we can control is `offsetX` and `offsetY` variables, which are used
to change flag part that is used in image generatinon.

## Solution

By examining provided source files and perlin noise script, we can deduce
multiple points that are important for figuring out the solution to this task:

1. Only 36 bits of flag are used when generating the noise:

```javascript
const div = (x, y) => {
  const p = 4;
  return Number(BigInt.asUintN(32 + p, (x * BigInt(1 << p)) / y)) / (1 << p);
};

const offsetX = div(flagInt, scaleX);
const offsetY = div(flagInt, scaleY);
```

The scary `div(x, y)` function actually just divides `flagInt` by user-supplied
number, then shifts result 4 bits to the left, after which takes lower 36 bits
of the result and shifts it back 4 bits to the right. After that procedure we
get 36-bit, 4 of which are after decimal point.

2. Only 12 of those 36 bits actually matter

```javascript
module.perlin2 = function(x, y) {
  // Find unit grid cell containing point
  var X = Math.floor(x), Y = Math.floor(y);
  // Get relative xy coordinates of point within that cell
  x = x - X; y = y - Y;
  // Wrap the integer cells at 255 (smaller integer period can be introduced here)
  X = X & 255; Y = Y & 255;
  
  // ...
}
```

Perlin noise function wraps integer cells at 255, so only lower 8 bits of
floored number are used. After adding this number with 4 decimal bits, we get
just 12 bits that affect noice generation.

3. Noise random is seeded by `2**16` value

```javascript
noise.seed(crypto.randomInt(65536));
const colors = [];
for (let y = 0; y < HEIGHT; y++) {
  for (let x = 0; x < WIDTH; x++) {
    let v = noise.perlin2(offsetX + x * 0.05, offsetY + y * 0.05);
    v = (v + 1.0) * 0.5; // [-1, 1] -> [0, 1]
    colors.push((v * 256) | 0);
  }
}
```

By combining these 3 points, we can conclude that we only need to bruteforce
`2**28` values for each character. We can validate each attempt by comparing
values that we received from generating image localy with values from the
server. This process can be done relatively fast, but we can speed it up a bit.

We can avoid comparing (and generating) all `256 * 256` bytes of image for each
case by filtering tuples of `(seed, byte, rem)` which generate sequence that
differs from server values in first `N` bytes. We chose to start by checking
first 16 bytes and then multiplying check length by 2, until only one possible
value is left. At that point script was spending ~100s on each byte, which was
good enough, so we decided not to optimize it any further.

---

Exploit is separated into multiple parts:
1. [brute.js](./brute.js) expects to have `image.webp` in working directory,
   received from the server. It bruteforces all possible inputs and outputs
   single integer value of flag byte, used to generate this image
2. [perlin.js](./perlin.js) is the noise generation script from server
3. [exploit.py](./exploit.py) communicates with the server, starts process of
   bruteforcing value using [brute.js](./brute.js) and collects flag
   byte-by-byte
   
To run it just start [exploit.py](./exploit.py) script and wait for it to print
the flag. Beware that it will take some time.
