
program fullProg(xVar, yVar);
	var x: integer;
	var y: integer;
	var z: real;
	var someArray: array[1..5] of real; {inline comment}
	
	function gcd (a: integer; b : integer) : integer;
	var sol: integer;
	begin
		if b = 4 then sol:=a {ensure that gcd id is the same throughout}
		else sol := 7
	end;


	function aProc (w: integer) : integer;
		begin
			w := x div y;
			while  w > 0 do
				begin
					w := w - 1;
					if x <> 0 then x := x + 1 else z := z/2.0;
					if not((10 mod 3) <= 3) then x:=2*5 else z:=5.2;
					if 10>=3 then x:=2*5 else z:=5.2;
					if 6>5  then x:=2*5 else z:=5.2;
					if 6<5  then x:=2*5 else z:=5.2;
					if 10<=3 then x:=2*5 else z:=5.2;
					x := 4 or 5
				end
		end;
	
	begin
		x := 17;
		y :=-4;
		y := gcd(x, y);
		x := aProc(x)
	end
{this is a comment}
.
