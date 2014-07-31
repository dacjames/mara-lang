# Type

Mara supports 3 kinds of types: Native, Object, and Interface. 

## Native

Native types are anything that Mara can translate directly to LLVM bytecode types.  When assigned to variables or passed to functions, Natives are manipulated by *value*.  They are used to impliment higher-level types and are useful for optimizing hot paths or interfacing with external systems.  The complete list of native types is:

- `Int(n)` fixed width integers.  Supports any `n` accepted by LLVM.
- `Uint(n)` unsigned, fixed width integers.  Supports any `n` accepted by LLVM.
- `Float(n)` IEEE floating point numbers.  Support `n in [32, 64, 128]`.
- `Chunk(n, T)` fixed size region of memory, mapped directly to a LLVM array.
- `Struct(List((Symbol, Type)))`  contiguous group of fields, mapped directly to a LLVM struct.
- `Ptr(T)` pointer to a memory location.

Because they are *untagged*, native types cannot be used for dynamic dispatch.

## Object 

Object types are the most commonly used types in mara programs.  `Array`, `File`, and `CSV.Reader` are all Object types.  Conceptually, Objects consist of a *tag*, which references the object's type, and a `Chunk` containing the object's fields.  Objects are manipulated by *reference* and implemented by default as a "fat pointer" whichs stores the tag with the pointer rather than alongside the object.  Mara objects have several differences from objects in other languages.

- No methods: all object functionality is implemented externally with bound functions.
- No classes or inheritence.
- Fields in the object are ordered.
- Support direct pointers to object internal memory.

## Interface

Interface types are the unit of abstraction in Mara and behave similar to interfaces in languages like Java or C++.  They allow objects to be manipulated through an opaque reference which hides the underlying implementation.  For example, the `List` interface is implemented for `LinkedList`, `Array`, and `Deque` objects so functions defined for `List` can operate on all three objects using the same code.

Unlike traditional OO languages, Interfaces in Mara are not defined directly using an interface syntax.  Instead, interfaces are created in two ways: 1) traits define a unique interface and 2) the interface of an object is inferred by the set of functions defined for it when it is instantiated.

### Bound Function

Conceptually, a bound function is a function that is "attached" to an object.  They are defined using the bind (`::`) operator, as in `def Int::plus (other Int) Int { etc }`.  More precisely, binding methods is a shorthand for defining a function in an object's instance namespace that accepts instances of the object as the first argument and uses the object's type namesapce in the body.  The above example is equivalent to:

    namespace Int.Instance {
        This = Int
        def plus (this This, other Int) Int {
            using Int.Type
            etc
        }
    }

Bound functions are the primary method for implimenting an object's functionality.  Bound functions cannot be abstract or depend on abstract methods.

### Trait

A Trait defines a set of functions that operate on a single object, any number of which may be abstract at definition.  Traits serve two purposes: 1) define an Interface, and 2) share implementatin among related objects.  They can contain multiple methods of the same function that are abstract over different function in the trait; even mutually abstract methods are supported.

Any object that impliments all the methods in a Trait, is said to *adopt* the Trait, gaining all the dependent methods defined therein.  The traits adopted by an object are materialized into a conrete *Interace* when the object is initialized.  Objects that impliment all of the abstract methods in a Trait are said to *impliment* that trait.


### Protocol

Protocols are a generalization of Traits that also define a set of related, possibly abstract functions.  However, they do not define interfaces because the functions are not defined for a single object.  Instead, Protocols provide cross-cutting code reuse for related functionality that doesn't "belong" to any one interface.  A set of functions is said to *impliment* a Protocol when they implement all of its abstract methods.




