# SourceMapping
Checks if files is accessible based on the source code. 
Useful when obtaining source code from a target and you want to check of any files is accesible without auth.
Wrote as part of prep for OSWE. 


```
 python .\SourceMapping.py -w 'c:\source\appname' -t 'https://localhost'
 -d for debug mode which will attempt to use a proxy as well
 --wordlist to print only a wordlist of the files
```

It will check for the following extensions which is configurable inside the source:

```
['*.txt', '*.json', '*.xml', '*.sql', '*.conf', '*.zip', '*.php', '*.ini', '*.cs', '*.js', '*.aspx', '*.asp', '*.java', '*.dll', '*.dat']
```

In the below example, we could either have found a backup file on blackbox engagement, or we are doing an whitebox engagement with the source.
We've used the ATutor example from the OSWE coursework. The script will automatically check which pages is accessible based on response, then check for potential form inputs on the pages that is accessible. This will allow us to target pages instead of sifting through large volumes.

![image](https://user-images.githubusercontent.com/954507/136694737-74a18c1f-5e43-4c24-b78e-289be2a52b26.png)
![image](https://user-images.githubusercontent.com/954507/136694756-87b7bbeb-983b-4c8e-97d5-48a1cae1c9e1.png)

