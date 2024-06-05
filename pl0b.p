program PL0B;
var n, x, i;
procedure prime();
var n;
begin
    n := x div 2;
    while x <> (x div n) * n do
        n := n - 1;
    if n = 1 then
        write(x)
end;
begin
    read(n);
    for i := 2 to n do
    begin
        x := i;
        prime()
    end
end.
