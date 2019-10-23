# efalg Task Runner

Runs tests of Java algorithms which use .in/.out files. Helper script written for tasks of a computer science course (Efficient Algorithms).

- Remove console logs and other unwanted lines.
- Output discreptancy between actual and expected output.
- Output stack trace on error.
- Specify timeout.
- Run tests in parallel.

![sample_output](https://user-images.githubusercontent.com/5418277/67145172-67ef1180-f27f-11e9-9d75-b8aac49ffe95.JPG)


---
## Quick start 

1. Drop `run.py` and `config.json` files into the directory of your project (where the `src` folder resides)
2. Run `pip install colored` if you want colors in your terminal.
3. In the `config.json` specify your Java bin path and the .in/.out filename that your program accepts.
3. Specify tests by creating a directory for each test in a `tests` directory, and putting a .in and .out (expected output) file into each.
4. run `python run.py` or `python run.py clean` if you want your source file to be cleaned of certain lines according to your specification in the `config.json` file.

Example directory structure:
```
project
├─── run.py
├─── config.json
├─── src
│    └── NonogramSolver.java
│
└─── tests 
     ├── test01 
     |   ├── test01.in
     |   └── test01.out
     |  
     └── test02 
         ├── test02.in
         └── test02.out
```

The source file with lines filtered will appear in the project directory. In `workingdir`, the raw test results will remain.


---
### Prerequisites

- Algorithm to test must consist of a Java program in a single source file.
- Program must use .in-files as input and output its result into .out files of the same name. 

### Dependencies

- colored (pip)

### Setup configuration

Setup configuration `config.json` file as follows:
- `java-dir`: bin directory of your JDK installation.
- `infile-name`: Name of the `.in` and `.out` files your program works with.
- `program-location` (optional): Absolute path of directory where the source file of your program resides. May be omitted if your source file resides in the `src` folder of the script directory.
- `program-name` (optional): Class and filename of your program. May be omitted if you hava only one Java file in the search directory.
- `timeout`: Maximum run time of any single test in ms.
- `ignore-match`: Array of strings for cleaning up log statements. Any lines of your source file that have these as a substring will be removed before compilation IF the script is run with the argument `clean`.


Example config.json:
```
{
    "java-dir": "C:\\Program Files\\Java\\jdk-11.0.2\\bin",
    "program-location": "C:\\Users\\fjodo\\Documents\\repos\\efalg_uebung_1\\src",
    "program-name": "NonogramSolver",
    "infile-name": "nonogram",
    "timeout": "1000",
    "ignore-match": [
        "  System.out.println(",
        "  log("
    ]
}
```

