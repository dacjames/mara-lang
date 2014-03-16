{
  venture: mara
  author: dac@dac.io
  flag: review
}

## Scoping

Mara has lexical scoping, with shadowing for nexted scopes.  A variable defined at any point within a block must be defined at all points in the block.  As a consequence of the previous, a program cannot alter the *identity* of a variable, only it`s *value*.

## Equality

Two datums must be considered equal iff all of their fields are equal and in the same order.  Native types are equal iff their values are exactly identical.

{todo: provide example}

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

## Built In Functions

