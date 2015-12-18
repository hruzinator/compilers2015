{This is a comment. It should be left out of the list of lexemes}
program example(input, output);
	var x, y: integer;
	function gcd(a, b: integer): integer;
	begin
		if b = 0 then gcd := a
		else gcd := gcd(b, a mod b)
	end;
	begin
		var a: real; b: real; c: real; d: real;
		a:=42.E4;
		b := 42.0E2;
		c := -42.6E;
		d := 42.0EA;
		x := 17;
		y := -4;
		gcd(x, y)
	end.
