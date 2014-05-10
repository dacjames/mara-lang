# Mara

Mara is a new programming language designed to be fast, fun, and functional.

## Features

    - Datums
    - Traits
    - Multiple Dispatch
    - Pattern Matching
    - Type Inference
    - For Expressions
    - Hybrid Memory Management
    - Dependency Injection

Okay, it doesn't offer all of those features today, but it will as development progressses.  Some of the driving principles behind Mara are:

    - Pragmatism over ideaology.
    - Customizable means configurable with good defaults -- be customizable.
    - Be explicit but never repeat yourself.
    - Guesswork is the root of all evil.
    - Every symbol should have one meaning in all contexts.

## What does Mara code look like?

Below is a simple implimentation of a program like the unix `tree` utility.

    module main
    using 'core'
    depend 'sys/argv'

    path_arg = argv[0] else raise "I need a file!"
    path = path_arg.Path else raise

    indent = Int argv[1] else 4
    max_depth = 20

    do (path = path, indent = 0, depth = 0) {
        raise "Maximum recursion depth reached" if depth > 10

        files, folders = partition(fs.ls path) (f){ f.is_file }

        String::indented = " ".repeat(indent) ++ this

        print file.name.indented for file in files
        for folder in folders {
            print folder.name.indented
            self(folder, indent + 2)
        }
    }

    end main

## What is Mara good for?

Mara strives to be a general purpose programming language, useful for everything from utilities to web services to distributed computing frameworks.  If you're a Python or Ruby hacker looking for more structure, a Java developer looking to write less boilerplate, or a C# programmer ready to move past inheritence, Mara might appeal to you.  If you're writing embedded code, operating systems, or games, you'll probably be better served by [Rust]() or [Nimrod]().
