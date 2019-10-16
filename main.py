"""
In the config file, specify
    Java program file location
    Timeout duration
    Array of substrings. Lines with these will be commented out or deleted.
    java bin path.

Upon running this main file:
    1. Replace strings as per rule (Remove system.out.println and the like)
    2. In working dir, create folder for each test.
    3. Compile java file and put result in to each test folder,
        as well as the corresponding input file for the test
    4. Run the program. On timeout, terminate and produce timeout error.
        On error, print full stack trace.
    5. On finish without errors, compare result to out file, print either
        success or error with received and expected output written down.
    6. Do this in parallel for all tests.
"""
import json
import subprocess
import os

config = None
with open('config.json', 'r') as configfile:
    config = json.load(configfile)

source_lines = None
with open(config['program-location'], 'r') as infile:
    source_lines = infile.read().split('\n')

with open('program.java', 'w') as outfile:
    log_removed = [
        line
        for line
        in source_lines
        if not any([ config_ignore in line
                 for config_ignore 
                 in config['ignore-match'] ])
    ]
    res_string = '\n'.join(log_removed)
    outfile.write(res_string)

argslist = [
    'javac',
    config['program-location'],
    '-d',
    os.path.dirname(os.path.abspath(__file__))
]
executable_path = config['java-dir'] + '\\javac.exe'
print(argslist)
subprocess.Popen(argslist, executable=executable_path)
