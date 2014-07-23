# Mara

Mara is a new programming language designed to be fast, fun, and functional. The core features of Mara are multi-dispatch and pattern matching, with support for rich destructuring. It is a dynamic-static hybrid with a flexible type system based on structural, ad-hoc polymorphism. 

## Features

    - Multiple Dispatch
    - Pattern Matching
    - Objects (but no Classes)
    - Traits & Protocols
    - Type Inference
    - For Expressions
    - Hybrid Memory Management
    - Dependency Injection

Okay, it doesn't offer all of those features today, but it will as development progressses.  Some of the driving principles behind Mara are:

    - Code should write code.
    - Be explicit but don't repeat yourself.
    - Guesswork is the root of all evil.
    - Every symbol should have one meaning in all contexts.

## What does Mara code look like?

Below is a simple implimentation of a program like the unix `tree` utility.

    module main
    using 'core'

    argv = depend 'sys.argv'
    max_depth = depend 'tree.max_depth' { 20 }

    path_arg = argv[0] else raise "I need a file!"
    path = path_arg.Path else raise

    indent = Int.parse argv[1] else 4

    do (path: path, indent: 0, depth: 0) {
        raise "Maximum recursion depth reached" if depth > max_depth

        files, folders = FS.ls(path).partition def(f){ f.is_file }

        def String::indented { " ".repeat(indent) ++ this }

        print file.name.indented for file in files
        for folder in folders {
            print folder.name.indented
            self(folder, indent + 2)
        }
    }

    end main

## What is Mara good for?

Mara strives to be a general purpose programming language, useful for everything from utilities to web services to distributed computing frameworks.  If you're a Pythonista or Ruby hacker looking for more structure, a Java developer tired of boilerplate, or a C# programmer ready to move past inheritence, Mara might appeal to you.  If you're writing embedded code, operating systems, or high performance browser engines, you'll probably be better served by [Rust](http://www.rust-lang.org/).
