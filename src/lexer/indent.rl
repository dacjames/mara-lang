%%{
  machine dent;

  action dent_space {}
  action dent_tab {}
  action dent_init {}
  action dent_end {}

  indent =
  start: (
    '\n' -> start |
    '\t' @dent_tab -> tab |
    ' ' @dent_space -> space |
    [^ \t\n] -> final
  ),
  space: (
    ' ' @dent_space -> space |
    [^ \t] -> final
  ),
  tab: (
    '\t' @dent_tab -> tab |
    [^ \t] -> final
  );

  line = indent %dent_end <: (any - '\n')* . '\n';

  main := line*;

}%%
