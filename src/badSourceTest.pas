{ unrecognizable symbols }
!
@
#
$
%
^
&
_
`
~
?
'
"
'
\
|
{ ---length errors--- }
supercalafragalisticexpialadoshus {identifier that is too long}
555555 {extra long integer}
{extra long fractional part}
{extra long exponential part}
{below shoud parse as LEXERR: extra long integer, progEnd, integer}
555555.234
{below shoud parse as LEXERR: extra long integer,}
{progEnd, integer, identifier (E), integer}
555555.234E2
12345.123456
12345.123456E2
12345.12345E123
123456.123456
123456.123456E1
12345.12345E123
{---extra tests---}
var a: real;
var b: real; 
var c: real;
var d: real;
a:=42.E4;
b :=42.0E2;
c:= -42.6E;
d := 42.0EA;