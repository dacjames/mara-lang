@start: value ;

?value : object | array | string | number | boolean | null ;

string : '".*?(?<!\\)(\\\\)*?"' ;
number : '-?([1-9]\d*|\d)(\.\d+)?([eE][+-]?\d+)?' ;
pair : string ':' value ;
object : '\{' ( pair ( ',' pair )* )? ','? '\}' ;
array : '\[' ( value ( ',' value ) * ','? )? '\]' ;
boolean : 'true' | 'false' ;
null : 'null' ;

WS: '[ \t\n]+' (%ignore) (%newline);
