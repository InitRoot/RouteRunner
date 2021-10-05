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

In the below example, a craft.zip obtained from a backup file can be mapped back to the application using the tool.

![image](https://user-images.githubusercontent.com/954507/136034951-6a38ad7d-0626-4e75-9f52-1d14f16f4d2b.png)
