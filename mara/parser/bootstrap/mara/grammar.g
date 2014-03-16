@start: body ;

body  : value* ;
value : array | string | number | boolean | null | idv | idt | assign | tuple | kw;

kw      : datum ;

datum   : 'datum' ;
comma   : COMMA ;

idv     : '[_]*[a-z][a-zA-Z0-9_]*' ;
idt     : '[_]*[A-Z][a-zA-Z0-9_]*' ;

assign  : idv '=' value;

string  : '".*?(?<!\\)(\\\\)*?"' ;
number  : '-?([1-9]\d*|\d)(\.\d+)?([eE][+-]?\d+)?' ;
pair    : string ':' value ;
array   : '\[' ( value ( ',' value ) * ','? )? '\]' ;
tuple   : '\(' ( value ( ',' value ) * ','? )? '\)' ;

boolean : 'true' | 'false' ;
null    : 'null' ;

WS      : '[ \t\n]+' (%ignore) (%newline);
