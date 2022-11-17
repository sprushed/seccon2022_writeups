### Introduction
In this task we have **check.sh** and  **flag.cbc** clamav bytecode.

### Understanding clamav

clamscan from clamav is used to determine the flag in **check.sh**: 

```Bash
...
else
    clamscan --bytecode-unsigned=yes --quiet -dflag.cbc "$1"
    if [ $? -eq 1 ]
    then
        echo "Correct!"
    else
        echo "Wrong..."
    fi
fi
```

I've used ***clambc -c*** to get instrutions of **flag.cbc**.
But them was looked very weird, so I used **bytecode_vm.c** from clamav github repository to reverse bytecode.
Then we get encrypting function that looks like this:
```C++
unsigned int func(unsigned int v0)
{
	unsigned int i = 0;
	unsigned int huinya = 0xacab3c9;
	for(;i != 4;i++)
		huinya = ((huinya ^ (0xff & (v0 >> (i << 3)))) << 8) | (huinya >> 24);
	 return huinya;
}
```

I think that bruteforce all possible input to that function and check if they are equal to encrypted flag parts using this code:
```C++
unsigned int hash(unsigned int input)
{
	unsigned int i = 0;
	unsigned int ret = 0xacab3c9;
	for(;i != 4;i++)
		ret = ((ret ^ (0xff & (input >> (i << 3)))) << 8) | (ret >> 24);
	 return ret;
}

int check(unsigned int ret_val)
{
	unsigned int keys[9] = {0x739e80a2,0x3aae80a3,0x3ba4e79f,0x78bac1f3,0x5ef9c1f3,0x3bb9ec9f,0x558683f4,0x55fad594,0x6cbfdd9f};
	for(int i=0;i < 9; i++)
		if(keys[i] == ret_val)
			return i;
	return -1;
}

int main()
{
	int S = 0x20, E = 0x7f;
	char brute[4];
	for(int a = S; a <= E; a++)
		for(int b = S; b <= E; b++)
			for(int c = S; c <= E; c++)
				for(int d = S; d <= E; d++)
				{
					brute[0] = a;
					brute[1] = b;
					brute[2] = c;
					brute[3] = d;
					unsigned int integer = *(unsigned int*)(brute), MATb_ABTOPA = hash(integer);
					int is_alive = check(MATb_ABTOPA);
					if( is_alive != -1)
						cout << s <<" "<< brute[0] << brute[1] << brute[2] << brute[3] << endl;
					//else 
					//	cout << "😢"; //Kakoi zhe krutoi task na llvm vsei komande zashlo 🙂👍🙂👍
				}	
	return 0;
  }
```
