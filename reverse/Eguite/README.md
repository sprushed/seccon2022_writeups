### Introduction
We have Rust binary that checks inputted flag:

![image](https://user-images.githubusercontent.com/55788168/201711611-c09c9816-7a16-4ea7-ac06-ad8ed063c3ed.png)

### Finding function that checks flag
If we try to input wrong flag we will recive:

![image](https://user-images.githubusercontent.com/55788168/201712161-6d6d32b5-7731-4798-81b5-d9ba37bce040.png)

So let's try to find "Invalid license..." string references in IDA:
![image](https://user-images.githubusercontent.com/55788168/201714943-8da45514-5c68-430a-bd1c-70a2e284454d.png)

This string uses in main dialogue function of our application and got recived only if ***eguite::Crackme::onclick::ha26112793d42c9d8*** function returns 0 on our input.
***eguite::Crackme::onclick::ha26112793d42c9d8*** checks if our flag format is:
> SECCON{aaaaaaaaaaaa-bbbbbb-cccccc-dddddddd} 
> where a,b,c,d are numbers in hexademical

and passes this condition:
![image](https://user-images.githubusercontent.com/55788168/201720866-82b96a3d-ad2f-4eb7-b6fb-ce77d9716cec.png)

If we use z3 on that equation system we wil find a,b,c,d values and flag
