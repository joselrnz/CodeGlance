entity Counter is
  port (clk : in bit);
end entity;

architecture rtl of Counter is
  function increment(x : integer) return integer is
  begin
    return x + 1;
  end function;
begin
end architecture;
