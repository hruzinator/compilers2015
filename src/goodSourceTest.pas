{This is a comment. It should be left out of the list of lexemes}
program example(input, output);
	var x: integer; y: integer;
	function gcd(a: integer; b: integer): integer;
	begin
		if b = 0 then gcd := a
		else gcd := gcd(b, a mod b)
	end;
	begin
		read(x, y);
		write(gcd(x, y))
	end.
