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
import time
from shutil import copyfile, rmtree
from time import sleep
from multiprocessing import Pool
import multiprocessing

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


def run_test(testname, conf):
    stdout = ''
    stderr = ''
    exec_time = 0
    test_result = ''
    test_summary = ''
    # Get in and out filenames.
    testpath = os.path.join('tests', testname)
    all_files = [file
                 for file
                 in os.listdir(testpath)
                 if os.path.isfile(os.path.join(testpath, file))]
    in_file = [f for f in all_files if f.endswith('.in')][0]
    out_file = [f for f in all_files if f.endswith('.out')][0]
    # Create test directory and copy files in there.
    os.mkdir(os.path.join('workingdir', testname))
    compiled_filename = conf['program-name'] + '.class'
    copyfile(
        compiled_filename,
        os.path.join('workingdir', testname, compiled_filename)
    )
    copyfile(
        os.path.join('tests', testname, in_file),
        os.path.join('workingdir', testname, conf['infile-name'] + '.in')
    )
    # Run program and retrieve result.
    argslist = [
        'java',
        conf['program-name'],
    ]
    os.chdir(os.path.join('workingdir', testname))
    executable_path = os.path.join(conf['java-dir'], 'java.exe')
    communication = popen_timeout(argslist,
                                  executable_path,
                                  int(conf['timeout']))
    if not communication:
        stderr = f'Timeout after {conf["timeout"]} ms.'
    else:
        stdout, stderr, exec_time = communication
        stdout = stdout.decode('utf-8').strip().replace('\n', '\n    ')
        stderr = stderr.decode('utf-8').strip().replace('\n', '\n    ')
    # Compare with specified out file and format result.
    os.chdir('../..')
    if len(stdout) != 0:
        stdout = stylize('\n  ' + stdout, colored.fg('yellow'))
    if len(stderr) == 0:
        with open(os.path.join(
            'tests',
            testname,
            out_file
        ), 'r') as targetfile, open(os.path.join(
            'workingdir',
            testname,
            conf['infile-name'] + '.out'
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
        stderr = '\n    ' + stylize(stderr, colored.fg('red')) + '\n'
        test_result = stylize(f'{testname}: Error ({exec_time} ms).',
                              colored.fg('red'))
    return test_result + stdout + stderr + test_summary


def run_tuples(in_tuple):
    return run_test(*in_tuple)


if __name__ == '__main__':
    # Read config
    config = None
    with open('config.json', 'r') as configfile:
        config = json.load(configfile)
    # Copy source file from specified location while filtering lines.
    source_lines = None
    program_location = os.path.join('src', config['program-name'] + '.java')
    if 'program-location' in config:
        program_location = os.path.join(config['program-location'],
                                        config['program-name'] + '.java')
    with open(program_location, 'r') as infile:
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
    start = time.time()
    results = Pool().map(run_tuples, [(test_name, config)
                                      for test_name
                                      in test_dirs])
    # Output results.
    for result in results:
        print(result)
    print(f'\nFinished in {round(time.time() - start, 2)}s.')
