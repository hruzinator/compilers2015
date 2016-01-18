{This tests the factor subset of the grammar. You can }
{use it to make sure you are on the right path without }
{ putting in hours of work only to make a mistake}

{---Factor Test----}

{This tests the grammar subset that goes from production}
{ rule 13.1 (variable1) to the end of the grammar. The root}
{ of the tree is the factor production (grammar rule 18.)}

{aVar ( 17 *  not ( - bVar [23 + 17 <= 90]), dVar(54) + cVar )}

{not not (5<6.0)}

{valid subset test}
{(-8<2*7+4)}
[8]

{invalid subset test}
{(-8*not 7+4)}