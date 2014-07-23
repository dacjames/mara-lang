# Type

Mara supports 3 kinds of types: Native, Object, and Trait. 

## Native

Native types are anything that Mara can translate directly to LLVM bytecode types.  When assigned to variables or passed to functions, Natives are manipulated by *value*.  They are used to impliment higher-level types and are useful for optimizing hot paths or interfacing with external systems.  The complete list of native types is:

- `Int(n)` fixed width integers.  Supports any `n` accepted by LLVM.
- `Uint(n)` unsigned, fixed width integers.  Supports any `n` accepted by LLVM.
- `Float(n)` IEEE floating point numbers.  Support `n in [32, 64, 128]`.
- `Block(n, T)` fixed size region of memory, mapped directly to a LLVM array.
- `Struct`  contiguous group of fields, mapped directly to a LLVM struct.
- `Ptr` pointer to a memory location.

Because they are *untagged*, native types cannot be used for dynamic dispatch.

## Object 

Object types are the most commonly used types in mara programs.  `Array`, `File`, and `CSV.Reader` are all Object types.  Objects are *tagged* reference and thus support dynamic dispatch.  Mara objects have several differences from objects in other languages.

- No classes or inheritence.
- Fields in the object are ordered.
- Support untagging and direct pointers to object internal memory.

Mara exposes the object tag directly to the programmer and supports fast retagging of exisitng objects by storing the tag in a "fat" pointer.


## Trait

Trait types are the unit of abstraction in Mara for both defining and using objects.  A Trait defines a set of functions that operate on a single object, any number of which may be abstract at definition.  In Mara, traits can contain multiple methods of the same function that are abstract over different function in the trait; even mutually abstract methods are supported.

Any object that impliments all the methods in a Trait, is said to *adopt* the Trait, gaining all the dependent methods defined therein.  The traits adopted by an object are materialized into a conrete type called an *Interace* when the object is initialized.  Thus, Traits are *structural* and *ad-hoc*.


## Protocol

Protocols are a generalization of Traits that also define a set of related, possibly abstract functions.  However, they do not define types because the functions are not defined for a single object.  Instead, Protocols provide cross-cutting code reuse for related functionality that doesn't "belong" to any one object.  Methods are said to *impliment* a Protocol when they complete all of its abstract methods.




