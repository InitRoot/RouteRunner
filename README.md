# SourceMapping
Checks if files is accessible based on the source code. 
Useful when obtaining source code from a target and you want to check of any files is accesible without auth, or during code reviews to identify potential pages which can be reviewed first. Wrote as part of prep for OSWE.

### Usage

```
 python .\SourceMapping.py -w 'c:\source\appname' -t 'https://localhost'
 -d for debug mode which will attempt to use a proxy as well
 --wordlist to print only a wordlist of the files
 -o for output location in csv format
```
### Configurable options in code

Some of the extensions which is configurable inside the source:

```
['*.txt', '*.json', '*.xml', '*.sql', '*.conf', '*.zip', '*.php', '*.ini', '*.cs', '*.js', '*.aspx', '*.asp', '*.java', '*.dll', '*.dat']
```

Limited functionality available to "review" potential pages for inputs, these pages should be primary targets and can easily be modified on this function:

```
def analyseVuln(rqResponse):
    if "<form action" in str(rqResponse.content):
        return "InputForm"
    elif "<form name" in str(rqResponse.content):
        return "InputForm"
    elif 'type="submit"' in str(rqResponse.content):
        return "SubmitForm"
    else:
        return ""
```

### Some new features:
- Progress bar
- Output write to file in CSV format
- Threading
- Debug mode, will have verbose output on each request and use proxy if one is found

### Screenshots:
In the below example, we could either have found a backup file on blackbox engagement, or we are doing an whitebox engagement with the source.
We've used the ATutor example from the OSWE coursework. The script will automatically check which pages is accessible based on response, then check for potential form inputs on the pages that is accessible. This will allow us to target pages instead of sifting through large volumes.

![image](https://user-images.githubusercontent.com/954507/136694737-74a18c1f-5e43-4c24-b78e-289be2a52b26.png)
![image](https://user-images.githubusercontent.com/954507/136694756-87b7bbeb-983b-4c8e-97d5-48a1cae1c9e1.png)

