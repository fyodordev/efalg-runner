"""
In the config file, specify
    * java-dir: Java program file location
    * program-name: Class name of the Java program
    * infile-name: Name of the test files
    * timeout: Timeout duration in ms.
    * ignore-match: Array of substrings.
                  Lines with these will be commented out or deleted.
    * java-dir: Java bin path.

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
from time import sleep

import colored
from colored import stylize


def popen_timeout(argslist, executable_path, timeout):
    p = subprocess.Popen(argslist,
                         executable=executable_path,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    for t in range(timeout):
        sleep(0.001)
        if p.poll() is not None:
            return (*p.communicate(), t)
    p.kill()
    return False


def run_test(testname, config):
    # Create test directory and copy files in there.
    os.mkdir(os.path.join('workingdir', testname))
    compiled_filename = config['program-name'] + '.class'
    copyfile(
        compiled_filename,
        os.path.join('workingdir', testname, compiled_filename)
    )
    copyfile(
        os.path.join('tests', testname, config['infile-name'] + '.in'),
        os.path.join('workingdir', testname, config['infile-name'] + '.in')
    )
    # Run program and retrieve result.
    stdout = ''
    stderr = ''
    exec_time = ''
    argslist = [
        'java',
        config['program-name'],
    ]
    os.chdir(os.path.join('workingdir', testname))
    executable_path = os.path.join(config['java-dir'], 'java.exe')
    communication = popen_timeout(argslist,
                                  executable_path,
                                  int(config['timeout']))
    if not communication:
        stderr = f'Timeout after {config["timeout"]} ms.\n'
    else:
        stdout, stderr, exec_time = communication
        stdout = stdout.decode('utf-8').strip().replace('\n', '\n  ')
        stderr = stderr.decode('utf-8').strip().replace('\n', '\n  ')
    # Compare with specified out file and format result.
    os.chdir('../..')
    test_result = '' 
    test_summary = '' 
    if len(stdout) != 0:
        stdout = stylize('\n  ' + stdout, colored.fg('yellow'))
    if len(stderr) == 0:
        stderr = '  ' + stylize(stderr, colored.fg('red')) + '\n'
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
                test_result = stylize(f'{testname}: Correct ({exec_time} ms).',
                                      colored.fg('green'),
                                      colored.attr('bold'))
            else:
                test_result = stylize(f'{testname}: Incorrect '
                                      f'({exec_time} ms).',
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
    return test_result + stdout + stderr + test_summary


# Read config
config = None
with open('config.json', 'r') as configfile:
    config = json.load(configfile)
# Copy source file from specified location while filtering lines.
source_lines = None
with open(config['program-location'], 'r') as infile:
    source_lines = infile.read().split('\n')
with open((config['program-name'] + '.java'), 'w') as outfile:
    log_removed = [
        line
        for line
        in source_lines
        if not any([config_ignore in line
                    for config_ignore
                    in config['ignore-match']])
    ]
    res_string = '\n'.join(log_removed)
    outfile.write(res_string)
# Compile the java code
source_filename = config['program-name'] + '.java'
argslist = [
    'javac',
    source_filename,
    '-d',
    os.path.dirname(os.path.abspath(__file__))
]
executable_path = os.path.join(config['java-dir'], 'javac.exe')
compile_proc = subprocess.Popen(argslist, executable=executable_path)
compile_proc.wait()
# Reset directory. 
if os.path.isdir('workingdir'):
    rmtree('workingdir')
    os.mkdir('workingdir')
# Test.
test_dirs = os.listdir('tests')
for test_dir in test_dirs:
    # Iterate through all defined tests.
    print(run_test(test_dir, config))
