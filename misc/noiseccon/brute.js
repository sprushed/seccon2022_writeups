const { noise } = require("./perlin.js");
const sharp = require("sharp");

const IMAGE = "image.webp";
const DEBUG = false;

async function readNumbersFromImage() {
  const { data } = await sharp(IMAGE)
    .toColourspace("b-w")
    .raw()
    .toBuffer({ resolveWithObject: true });

  const arr = [];
  for (let i = 0; i < 1 << 16; i++) {
    arr.push(data[i]);
  }
  return arr;
}

async function generateNoise(byte, rem, first_n) {
  const colors = [];
  const offset = byte + rem / 16;
  let x = 0;
  let y = 0;

  for (y = 0; y * 256 + x < first_n; y++) {
    for (x = 0; y * 256 + x < first_n && x < 256; x++) {
      let v = noise.perlin2(offset + x * 0.05, offset + y * 0.05);
      v = (v + 1.0) * 0.5; // [-1, 1] -> [0, 1]
      colors.push((v * 256) | 0);
    }
    x = 0;
  }

  return colors;
}

async function main() {
  const numbers = await readNumbersFromImage();

  const availableSeeds = new Set();
  for (let seed = 0; seed < 65536; seed++) {
    availableSeeds.add(seed);
  }

  let everything = new Set();
  let checkedLength = 16, i = 1;
  if (DEBUG) console.log(`Round ${i++}: length = ${checkedLength}; num of elements = ${availableSeeds.size}`);
  for (const seed of availableSeeds) {
    noise.seed(seed);
    if (DEBUG && seed % 1000 === 0) console.log(`Checking seed ${seed}`)
    for (let byte = 0; byte < 256; byte++) {
      for (let rem = 0; rem < 16; rem++) {
        const generated = await generateNoise(byte, rem, checkedLength);

        let aborted = false
        for (let i = 0; i < checkedLength; i++) {
          if (numbers[i] !== generated[i]) {
            aborted = true;
            break;
          }
        }

        if (!aborted) {
          everything.add({
            byte, rem, seed
          });
        }
      }
    }
  }

  while (everything.size > 1) {
    checkedLength *= 2;
    if (DEBUG) console.log(`Round ${i++}: length = ${checkedLength}; num of elements = ${everything.size}`);
    const newEverything = new Set();

    for (const { byte, rem, seed } of everything) {
      noise.seed(seed);

      const generated = await generateNoise(byte, rem, checkedLength);
      let aborted = false

      for (let i = 0; i < checkedLength; i++) {
        if (numbers[i] !== generated[i]) {
          aborted = true;
          break;
        }
      }

      if (!aborted) {
        newEverything.add({
          byte, rem, seed
        });
      }
    }

    everything.clear();
    everything = newEverything;
  }

  console.log(everything.values().next().value.byte);
}

(async () => {
  await main();
})();
