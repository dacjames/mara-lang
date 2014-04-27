{
  venture: mara
  author: dac@dac.io
  flag: review
}

## Scoping

Mara has lexical scoping, with shadowing for nexted scopes.  A variable defined at any point within a block must be defined at all points in the block.  As a consequence of the previous, a program cannot alter the *identity* of a variable, only it`s *value*.

## Equality

Two datums must be considered **equal** (==) iff all of their fields are equal and in the same order.  Native types are equal iff their values are exactly identical.

    datum Point (x Int, y Int)
    datum Pair (x Int, y Int)

    assert Point(0, 0) == Pair(0, 0)
    assert Point(0, 1) != Point(0, 0)
    assert Point(1, 0) != Point(0, 1)
    assert (p0 == p1)

    x = 0.Int64
    y = 0.Int64

    assert x == y

Two datums must be considered **equivalent** (===) iff they are equal and of the same type.  Native types are equivalent iff they are equal.

    datum Point (x Int, y Int)
    datum Pair (x Int, y Int)

    assert Point(0, 0) === Point(0, 0)
    assert Point(0, 0) !== Pair(0, 0)

## Precedence

KEYWORD > MATH > BOOLEAN > SYMBOLIC > VERBAL

KEYWORD                : left-to-right, terminating


`^`                    : left-to-right, non-terminating
`*`  | `/` | `//` | `%`: left-to-right, non-terminating
`+`  | `-`             : left-to-right, non-terminating

`&&` | `||`            : left-to-right, non-terminating
`!`                    : right-to-left, non-terminating


SYMBOLIC: left to right, non-terminating
VERBAL: left to right, terminating

## Truth-ness

Only `false`, `null`, and `No` are treated as false in Mara.  Other values, such as empty strings and lists, must be converted to boolean using the `?` "truthy" operator.  The following values are converted to `false`, everything else is `true`.

  - `0`
  - `0.0`
  - `[]`
  - `{}`
  - `()`
  - `""`, `''`


