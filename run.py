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
from shutil import copyfile, rmtree

import colored
from colored import stylize

def run_test(testname, config):
    os.mkdir(os.path.join('workingdir', testname))
    copyfile(
        compiled_filename,
        os.path.join('workingdir', testname, compiled_filename)
    )
    copyfile(
        os.path.join('tests', testname, config['infile-name'] + '.in'),
        os.path.join('workingdir', testname, config['infile-name'] + '.in')
    )
    # Run program 
    argslist = [
        'java',
        config['program-name'], 
    ]
    os.chdir(os.path.join('workingdir', testname))
    executable_path = os.path.join(config['java-dir'], 'java.exe')
    test_proc = subprocess.Popen(
        argslist,
        executable=executable_path,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    stdout, stderr = test_proc.communicate()
    os.chdir('../..')
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    test_result = None
    test_summary = None 
    if len(stderr) == 0:
        with open(os.path.join(
            'tests',
            testname,
            config['infile-name'] + '.out'
        ), 'r') as targetfile, open(os.path.join(
            'workingdir',
            testname,
            config['infile-name'] + '.out'
        ), 'r') as outfile:
            target_string = targetfile.read().strip()
            out_string = outfile.read().strip()
            if target_string == out_string:
                test_result = stylize(f'{testname}: Correct.',
                                      colored.fg('green'),
                                      colored.attr('bold'))
            else:
                test_result = stylize(f'{testname}: Incorrect.',
                                      colored.fg('red'),
                                      colored.attr('bold'))
                test_summary = (
                    '  ' + stylize('Expected output:\n',
                                   colored.attr('underlined'))
                    + stylize(f'    {target_string}\n', colored.attr('bold'))
                    + '  ' + stylize('Actual output:\n',
                                     colored.attr('underlined'))
                    + stylize(f'    {out_string}\n', colored.fg('red')))
    else:
        test_result = stylize(f'{testname}: Error.', colored.fg('red'))
    return stdout, stderr, test_result, test_summary


# Read config
config = None
with open('config.json', 'r') as configfile:
    config = json.load(configfile)

# Copy file from specified location while filtering lines.
source_lines = None
with open(config['program-location'], 'r') as infile:
    source_lines = infile.read().split('\n')
with open((config['program-name'] + '.java'), 'w') as outfile:
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

source_filename = (config['program-name'] + '.java')
compiled_filename = (config['program-name'] + '.class')

# Compile the java code
argslist = [
    'javac',
    source_filename,
    '-d',
    os.path.dirname(os.path.abspath(__file__))
]
executable_path = os.path.join(config['java-dir'], 'javac.exe')
compile_proc = subprocess.Popen(argslist, executable=executable_path)
compile_proc.wait()

# Copy into all directories
if os.path.isdir('workingdir'):
    rmtree('workingdir')
    os.mkdir('workingdir')
test_dirs = os.listdir('tests')
for test_dir in test_dirs:
    stdout, stderr, test_result, test_summary = run_test(test_dir, config)
    print(test_result)
    if stdout != '':
        print(stylize('  ' + stdout.replace('\n', '\n  '), colored.fg('yellow')))
    if stderr != '':
        print(stylize(stderr, colored.fg('red')))
    if test_summary is not None:
        print(test_summary)