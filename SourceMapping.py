#!/usr/bin/python3

#python3 -m pip install requests, tabulate, tqdm
import argparse
import requests
import sys
import glob
import concurrent
import concurrent.futures
from tqdm import tqdm
from itertools import repeat
import csv
from random import randint
from time import sleep
import re
from tabulate import tabulate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Interface class to display terminal messages
class Interface():
    def __init__(self):
        self.red = '\033[91m'
        self.green = '\033[92m'
        self.white = '\033[37m'
        self.yellow = '\033[93m'
        self.bold = '\033[1m'
        self.end = '\033[0m'

    def header(self):
        print(f"\n {self.bold}*************** Source Code Mapping ***************{self.end}")
        print(f"@initroot \n")

    def info(self, message):
        print(f"[{self.white}*{self.end}] {message}")

    def warning(self, message):
        print(f"[{self.yellow}!{self.end}] {message}")

    def error(self, message):
        print(f"[{self.red}x{self.end}] {message}")

    def success(self, message):
        print(f"[{self.green}✓{self.end}] {self.bold}{message}{self.end}")


def sendGet(url, debug):
    #debug = False;
    session = requests.Session()
    session.max_redirects = 5
    sleep(randint(2,15))
    try:
        if debug is True:
            proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
            r = session.get(url, proxies = proxies,verify=False)
            pot = analyseVuln(r)
            output.info([url,r.url, r.status_code,len(r.content),pot])
        else:
            r = session.get(url,verify=False)
            pot = analyseVuln(r)
    except requests.exceptions.ProxyError:                 
        r = session.get(url,verify=False)
        pot = analyseVuln(r)
        output.info([url,r.url, r.status_code,len(r.content),pot])
        return [url,r.url, r.status_code,len(r.content),pot]
    except requests.exceptions.TooManyRedirects as exc:
        r = exc.response
        pot = analyseVuln(r)
        output.info([url,r.url, r.status_code,len(r.content),pot])

    return [url,r.url, r.status_code,len(r.content),pot]

#Used to analyse the returns for potential areas to highlight, can be extended easily
def analyseVuln(rqResponse):
    if "<form action" in str(rqResponse.content):
        return "InputForm"
    elif "<form name" in str(rqResponse.content):
        return "InputForm"
    elif 'type="submit"' in str(rqResponse.content):
        return "SubmitForm"
    else:
        return ""

#extracts possible routes from source code .cs files --> controllers --> actions
#setuyp extract from the global as well
#improve action result regexes for multiples
def findnetMVCRoutes(path,debug,paramsreq):
    controllerpattern = re.compile(r"\b(public|private|internal|protected)\s*s*(class)\s(?P<ControllerName>[A-Za-z_][A-Za-z_0-9]*)*\s*[:]\s\b(BaseController|ApiController|Controller)")
    actionpattern1 = re.compile(r"\b(ActionResult|IActionResult).\s*\b(?P<ActionNames>[A-Za-z_][A-Za-z_0-9]*)")
    functionnames = re.compile(r"\b(public|private|internal|protected)(\s+(static|async))?\s+[\w]+(?:<[\w\s,<>]+>)?\s+(?P<FunctionNames>[A-Za-z_][A-Za-z_0-9]*)\s*\(")
    nullablefunctionnames = re.compile(r"\b(public|private|internal|protected)(\s+(static|async))?\s+[\w<>,\s]+\??\s+(?P<FunctionNames>[A-Za-z_][A-Za-z_0-9]*)\s*\(")
    codedroutes = re.compile(r'\[Route\("(?P<routes>[^"]+)"\)\]')
    codedroutesprefix = re.compile(r'\.*RoutePrefix\("(?P<routes>[^"]+)"\)\]')
    #method names (?<type>[^\s]+)\s(?<name>[^\s]+)(?=\s\{get;)
    curRoutes = []
    paramRoutes = []
    with open (path, encoding='utf8') as infile:
        curController = None
        for num, line in enumerate(infile, 1):
            #print(str(num) + ":" + line)
            #Controller check first
            if ('RoutePrefix' in line):
                results =   codedroutesprefix.findall(line)[0]
                #print(results)
                #print(results[-1]) 
                curController = results    
            elif ('BaseController' in line or 'APIController' in line or 'Controller' in line)and isBlank(curController):
                try:
                    mvcpath = ''
                    #print(str(num) + ":" + line)
                    #extracts the groups from the match. the full line as follow:
                    #('public', 'class', 'CompeteController', 'BaseController') data could be used for in depth analysis
                    results = controllerpattern.findall(line)[0]
                    mvcpath = results[2]
                    mvcpath = mvcpath.replace('Controller','')
                    #print(mvcpath)     #ddebug
                    if isNotBlank(mvcpath):
                        #print(line)     #ddebug
                        if ('ApiController' in line):
                            curController = "api/" + mvcpath
                        else:
                            curController = mvcpath
                        
                    #print(curController)
                                                  
                #except Exception as e: print(e)
                except: None
                #output.error("Regex controller error on following:")
                #output.info(path  + "-->"  + line + " \t \n")
                            
                #Check if includes actionresult for actions  
                #print(line)  
            elif ('[Route' in line) and isNotBlank(curController):
                try:
                    mvcpath = ''
                    params = ''
                    #print(line)
                    #attempts to extract data based on several possible regexes.
                    results = codedroutes.findall(line)[0]  
                    mvcpath = results[-1]
                    params = extractParameters(line)
                    if isNotBlank(params):
                        params = " | (" + params + ")"
                    if isNotBlank(mvcpath):
                                mvcpath = "/" + mvcpath
                                mvcpath = mvcpath.strip() 
                                curRoutes.append(mvcpath)
                                paramRoutes.append(mvcpath + params)
                except:
                    None 
            elif ('ActionResult' in line) and isNotBlank(curController):
                #print(line)
                try:
                    mvcpath = ''
                    params = ''
                    #attempts to extract data based on several possible regexes.
                    results = actionpattern1.findall(line)[0]  
                    mvcpath = results[1]
                    #print(mvcpath)
                    params = extractParameters(line)
                    if isNotBlank(params):
                        params = params
                    if isNotBlank(mvcpath):
                                mvcpath = "/" + curController + "/" + mvcpath
                                #print(mvcpath)
                                mvcpath = mvcpath.strip() 
                                curRoutes.append(mvcpath)
                                paramRoutes.append(mvcpath + params)
                except Exception as e: print(e)
               

                #Check if includes access modifiers for functions and then does a function parse               
            elif ('public' in line or 'private' in line or 'static' in line or 'internal' in line or 'protected' in line) and isNotBlank(curController):
                #print(line)
                try:
                    mvcpath = ''
                    params = ''
                    #attempts to extract data based on several possible regexes.
                    results = functionnames.findall(line)[0]
                    #print(results)  
                    mvcpath = results[-1]
                    params = extractParameters(line)
                    if isNotBlank(params):
                        params = params
                    if isNotBlank(mvcpath):
                                mvcpath = "/" + curController + "/" + mvcpath 
                                curRoutes.append(mvcpath)
                                paramRoutes.append(mvcpath + params)
                except:
                    None                                                      
            elif ('public' in line or 'private' in line or 'static' in line or 'internal' in line or 'protected' in line) and isNotBlank(curController):
                #print(line)
                try:
                    mvcpath = ''
                    params = ''
                    #attempts to extract data based on several possible regexes.
                    results = nullablefunctionnames.findall(line)[0]
                    #print(results)  
                    mvcpath = results[-1]
                    params = extractParameters(line)
                    if isNotBlank(params):
                        params = params
                    if isNotBlank(mvcpath):
                                mvcpath = "/" + curController + "/" + mvcpath 
                                curRoutes.append(mvcpath)
                                paramRoutes.append(mvcpath + params)
                except:
                    None             
            
            else:
                continue
 #print("Pre return none finished func")
    if paramsreq:
        #output.info('Output including parameters selected.')

        return paramRoutes
    else:
        return curRoutes

def extractParameters(line):
    #print("Extracting paramters from: " + line)
    findParams = re.compile(r'\(\s*(?P<parameters>(?:\[\w+(?:\(\))?\]\s*)*[\w<>,\s]+\s+\w+(?:\s*,\s*(?:\[\w+(?:\(\))?\]\s*)*[\w<>,\s]+\s+\w+)*)\s*\)')
    param_pattern = re.compile(r'(\w+)\s+(\w+)')
    foundparams = ''
    urlParams = ''
    fullurlParams = []
    try:
        foundparams = findParams.findall(line)[0]
        #print(foundparams) 
        matches = param_pattern.findall(foundparams)
        for match in matches:
            # Each match is a tuple (type, name)
            if ('tring' in match[0]):
                urlParams = match[1] + "=" + match[1]
            elif ('int' in match[0]):
                urlParams = match[1] + "=123456"
            elif ('oolean' in match[0]):
                urlParams = match[1] + "=true"
            elif ('ime' in match[0]):
                urlParams = match[1] + "=22/07/2021"
            else:
                urlParams = match[1] + "=" + match[1]
                print("Can't parse: " + match[0] + "..." +match[1])
            
            fullurlParams.append(urlParams)
            


        
        return "?" + "&".join(fullurlParams)

    except IndexError:
        return ''  # Return an empty string if no matches are found



def isBlank (myString):
    return not (myString and myString.strip())

def isNotBlank (myString):
    return bool(myString and myString.strip())

#removes duplicates from list and cleans nulls
def remDuplicates(x):
    res = list(filter(None, x))
    return list(dict.fromkeys(res))


def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def main():
    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--dir',	 help='Root directory holding the source code', required=True)
    parser.add_argument('-t', '--target', help='Target web application URL e.g. http://localhost', required=True)
    parser.add_argument('-d', '--debug', help='Instruct our web requests to use our defined proxy', action='store_true', required=False)
    parser.add_argument('--wordlist', help='Only creates the wordlist based on source files',action='store_true')
    parser.add_argument('-f', '--framework', help='Routing framework e.g. netmvc, zend, spring, nodejs', required=False)
    parser.add_argument('-o', '--output', help='Write results to output file', required=False)
    parser.add_argument('--parameters', help='Output parameters found',action='store_true')
    args = parser.parse_args()

    # Instantiate our interface class
    global output
    output = Interface()

    # Banner
    output.header()

    # Debugging
    if args.debug:
        for k,v in sorted(vars(args).items()):
            if k == 'debug':
                output.warning(f"Debugging Mode: {v}")
            else:
                output.info(f"{k}: {v}")

    #Let's get a list of all files in the dir
    exts = ['*.txt', '*.json', '*.xml', '*.config', '*.svc','*.asmx', '*.sql', '*.conf', '*.zip', '*.php', '*.ini', '*.cs', '*.js', '*.aspx', '*.asp', '*.java', '*.dat', '*.ascx', '*.html', '*.cshtml']
    files = [f for ext in exts 
         for f in glob.glob(args.dir + '/**/' + ext, recursive=True)]
    output.info('List of files generated with success!')
    potUrls = [] #general holder for all our URLS
    #Lets check if a framework is being forced
    framewk = args.framework
    params = args.parameters
    #print(params)
    #MVC
    if 'netmvc' in framewk:
        output.info('Framework selected, analysing as .net MVC application.')
        extm = re.compile(".*\.cs$")
        csfiles = list(filter(extm.match, files))           
        with concurrent.futures.ThreadPoolExecutor(5) as executor:
            mvcPaths = list(tqdm(executor.map(findnetMVCRoutes, csfiles, repeat(args.debug), repeat(params)), total=len(csfiles)))
            mvcPaths = [t for t in mvcPaths if t] #strips all empty tuples
            mvcPaths = flatten(mvcPaths)
            mvcPaths = remDuplicates(mvcPaths) 
            #print(*mvcPaths, sep="\n")
            potUrls = mvcPaths
            potUrls = [(args.target + url) for url in potUrls]
            output.info('All MVC routes identified.')


    else:
        #Basic functionality which takes the dirs and supplements them with the targets no routing taken into account
        potUrls = [file.replace(args.dir,args.target) for file in files]
        potUrls = [url.replace('\\','/') for url in potUrls]


    #if wordlist arg is checked, we don't check access, we just output the results
    if args.wordlist:
        print(*potUrls, sep="\n")
        output.success('Done!')
    #Check access for identified endpoints, if not wordlist only
    else:
        output.info('Now checking access to ' + str(len(potUrls)) + ' endpoints, please wait:\n')
        with concurrent.futures.ThreadPoolExecutor(10) as executor:
            #accessible = executor.map(sendGet, potUrls, repeat(args.debug))
            accessible = list(tqdm(executor.map(sendGet, potUrls, repeat(args.debug)), total=len(potUrls)))        
            output.info(tabulate(accessible))
            if args.output:
                output_file = args.output             
                with open(output_file, 'w') as file:
                    write = csv.writer(file) 
                    write.writerows(accessible)
        output.success('Done!') 
    
if __name__ == '__main__':
    main()
