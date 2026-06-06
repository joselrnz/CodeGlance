module mathmod
contains
  subroutine greet()
    print *, "hi"
  end subroutine greet

  function square(x) result(y)
    integer :: x, y
    y = x * x
  end function square
end module mathmod
