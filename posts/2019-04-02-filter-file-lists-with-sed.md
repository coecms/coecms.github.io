---
layout: post
title: Filter Lists of Files in bash Using sed
author: Aidan Heerdegen
categories: bash, sed
---
# Filter Lists of Files in bash Using sed

We had a recent query on the [Slack support channel](https://arccss.slack.com) 
asking how, when using `bash`, to programatically generate a listing of files 
when the year was part the filename, given a begin year and end year.

What do I mean by that? Well the files looked a bit like this:
```
file.0197-03.nc
```
so in this case the file is the third month of year 197.

The question was: in a script where the first and last year are stored as variables, 
how to easily make a list of files that can be looped over in `bash`?

## Fast answer

Use `eval` and brace expansion in combination with wildcard globbing, e.g.
```
$ eval ls file.*{$begin..$end}-*.nc
```
(NB: The `$` sign at the beginning of a line signifies the unix prompt, to delineate 
between a command and it's output)

If you want to know why, read on ...

## Making a test directory

First step, make a test directory to test solutions like so:
```
$ mkdir tmp
$ touch tmp/file.{0197..0202}-{01..12}.nc
$ ls tmp
```
This has created the following files:
```
$ ls tmp
file.0197-01.nc  file.0198-07.nc  file.0200-01.nc  file.0201-07.nc
file.0197-02.nc  file.0198-08.nc  file.0200-02.nc  file.0201-08.nc
file.0197-03.nc  file.0198-09.nc  file.0200-03.nc  file.0201-09.nc
file.0197-04.nc  file.0198-10.nc  file.0200-04.nc  file.0201-10.nc
file.0197-05.nc  file.0198-11.nc  file.0200-05.nc  file.0201-11.nc
file.0197-06.nc  file.0198-12.nc  file.0200-06.nc  file.0201-12.nc
file.0197-07.nc  file.0199-01.nc  file.0200-07.nc  file.0202-01.nc
file.0197-08.nc  file.0199-02.nc  file.0200-08.nc  file.0202-02.nc
file.0197-09.nc  file.0199-03.nc  file.0200-09.nc  file.0202-03.nc
file.0197-10.nc  file.0199-04.nc  file.0200-10.nc  file.0202-04.nc
file.0197-11.nc  file.0199-05.nc  file.0200-11.nc  file.0202-05.nc
file.0197-12.nc  file.0199-06.nc  file.0200-12.nc  file.0202-06.nc
file.0198-01.nc  file.0199-07.nc  file.0201-01.nc  file.0202-07.nc
file.0198-02.nc  file.0199-08.nc  file.0201-02.nc  file.0202-08.nc
file.0198-03.nc  file.0199-09.nc  file.0201-03.nc  file.0202-09.nc
file.0198-04.nc  file.0199-10.nc  file.0201-04.nc  file.0202-10.nc
file.0198-05.nc  file.0199-11.nc  file.0201-05.nc  file.0202-11.nc
file.0198-06.nc  file.0199-12.nc  file.0201-06.nc  file.0202-12.nc
```
The above command uses brace expansion, which I will explain later.

## How to list files within a given year range?

So, the question was, given a begin year and end year, say
```
begin=199
end=201
```
how can you easily obtain an ordered list of all the months in all the years between, 
and including the two years?

Well firstly, the year is encoded in the filename as a left zero-padded 
4 digit number, so the first step is to use `printf` to perform this 
transformation:
```
$ begin=$(printf "%04d" $begin)
$ end=$(printf "%04d" $end)
$ echo $begin $end
0199 0201
```
I haven't simply pre-pended a zero at the beginning of the year otherwise it will not
work for years > 999.

### Globs

Shell [`globbing`](https://www.tldp.org/LDP/abs/html/globbingref.html) uses wildcards 
and a process called "filename expansion" which is very useful and can be used to
easily match the required pattern:
```
$ ls tmp/file.0199-*.nc tmp/file.0200-*.nc tmp/file.0201-*.nc
tmp/file.0199-01.nc  tmp/file.0200-01.nc  tmp/file.0201-01.nc
tmp/file.0199-02.nc  tmp/file.0200-02.nc  tmp/file.0201-02.nc
tmp/file.0199-03.nc  tmp/file.0200-03.nc  tmp/file.0201-03.nc
tmp/file.0199-04.nc  tmp/file.0200-04.nc  tmp/file.0201-04.nc
tmp/file.0199-05.nc  tmp/file.0200-05.nc  tmp/file.0201-05.nc
tmp/file.0199-06.nc  tmp/file.0200-06.nc  tmp/file.0201-06.nc
tmp/file.0199-07.nc  tmp/file.0200-07.nc  tmp/file.0201-07.nc
tmp/file.0199-08.nc  tmp/file.0200-08.nc  tmp/file.0201-08.nc
tmp/file.0199-09.nc  tmp/file.0200-09.nc  tmp/file.0201-09.nc
tmp/file.0199-10.nc  tmp/file.0200-10.nc  tmp/file.0201-10.nc
tmp/file.0199-11.nc  tmp/file.0200-11.nc  tmp/file.0201-11.nc
tmp/file.0199-12.nc  tmp/file.0200-12.nc  tmp/file.0201-12.nc
```
but that is difficult to generate programmatically given arbitrary start and end
years. 

It can be done using `seq`:
```
$ for year in $(seq -f "%04.0f" $begin $end); do echo $year; ls tmp/*$year-*.nc; done
0199
tmp/file.0199-01.nc  tmp/file.0199-05.nc  tmp/file.0199-09.nc
tmp/file.0199-02.nc  tmp/file.0199-06.nc  tmp/file.0199-10.nc
tmp/file.0199-03.nc  tmp/file.0199-07.nc  tmp/file.0199-11.nc
tmp/file.0199-04.nc  tmp/file.0199-08.nc  tmp/file.0199-12.nc
0200
tmp/file.0200-01.nc  tmp/file.0200-05.nc  tmp/file.0200-09.nc
tmp/file.0200-02.nc  tmp/file.0200-06.nc  tmp/file.0200-10.nc
tmp/file.0200-03.nc  tmp/file.0200-07.nc  tmp/file.0200-11.nc
tmp/file.0200-04.nc  tmp/file.0200-08.nc  tmp/file.0200-12.nc
0201
tmp/file.0201-01.nc  tmp/file.0201-05.nc  tmp/file.0201-09.nc
tmp/file.0201-02.nc  tmp/file.0201-06.nc  tmp/file.0201-10.nc
tmp/file.0201-03.nc  tmp/file.0201-07.nc  tmp/file.0201-11.nc
tmp/file.0201-04.nc  tmp/file.0201-08.nc  tmp/file.0201-12.nc

````
In the command above I have used `echo` to print the value of the `$year` loop
variable to highlight this is 3 successive invocations of `ls`.

Using this approach it might also be necessary to account for cases where there is 
no match for a specific year.

If you're looping over the values of year explicitly it might just be simpler
to generate the filenames directly rather than using `ls`. 

Also, `seq` is a [commonly installed GNU utility](https://www.gnu.org/software/coreutils/manual/html_node/seq-invocation.html), not a
builtin bash command, so it can't be guaranteed to always be present.

### Brace expansion

The most concise and attractive way is [brace exapansion](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html). This is
what I used above to generate the test files initially. 

To see how it works with a range, as above:
```
$ echo {0199..0201}
0199 0200 0201
```
so why not just use the variables defined above directly in a brace expansion?
```
$ echo {$begin..$end}
{0199..0201}
```
It doesn't do the brace expansion, just variable substitution. So this won't work.

To make it work you need to use [`eval`](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
```
$ eval echo {$begin..$end}
0199 0200 0201
```
which evaluates the expression *after* the variable expansion has taken place. To 
use this to get a list of the matching files:
```
$ eval ls tmp/*{$begin..$end}-*.nc
tmp/file.0199-01.nc  tmp/file.0200-01.nc  tmp/file.0201-01.nc
tmp/file.0199-02.nc  tmp/file.0200-02.nc  tmp/file.0201-02.nc
tmp/file.0199-03.nc  tmp/file.0200-03.nc  tmp/file.0201-03.nc
tmp/file.0199-04.nc  tmp/file.0200-04.nc  tmp/file.0201-04.nc
tmp/file.0199-05.nc  tmp/file.0200-05.nc  tmp/file.0201-05.nc
tmp/file.0199-06.nc  tmp/file.0200-06.nc  tmp/file.0201-06.nc
tmp/file.0199-07.nc  tmp/file.0200-07.nc  tmp/file.0201-07.nc
tmp/file.0199-08.nc  tmp/file.0200-08.nc  tmp/file.0201-08.nc
tmp/file.0199-09.nc  tmp/file.0200-09.nc  tmp/file.0201-09.nc
tmp/file.0199-10.nc  tmp/file.0200-10.nc  tmp/file.0201-10.nc
tmp/file.0199-11.nc  tmp/file.0200-11.nc  tmp/file.0201-11.nc
tmp/file.0199-12.nc  tmp/file.0200-12.nc  tmp/file.0201-12.nc
```
Without `eval`:
```
$ ls tmp/*{$begin..$end}-*.nc
ls: cannot access tmp/*{0199..0201}-*.nc: No such file or directory
```
So you can get a list that you can iterate over using a subshell, like so:
```
$ for file in $(eval ls tmp/*{$begin..$end}-*.nc); do echo $file; done
tmp/file.0199-01.nc
tmp/file.0199-02.nc
tmp/file.0199-03.nc
tmp/file.0199-04.nc
tmp/file.0199-05.nc
tmp/file.0199-06.nc
tmp/file.0199-07.nc
tmp/file.0199-08.nc
tmp/file.0199-09.nc
tmp/file.0199-10.nc
tmp/file.0199-11.nc
tmp/file.0199-12.nc
tmp/file.0200-01.nc
tmp/file.0200-02.nc
tmp/file.0200-03.nc
tmp/file.0200-04.nc
tmp/file.0200-05.nc
tmp/file.0200-06.nc
tmp/file.0200-07.nc
tmp/file.0200-08.nc
tmp/file.0200-09.nc
tmp/file.0200-10.nc
tmp/file.0200-11.nc
tmp/file.0200-12.nc
tmp/file.0201-01.nc
tmp/file.0201-02.nc
tmp/file.0201-03.nc
tmp/file.0201-04.nc
tmp/file.0201-05.nc
tmp/file.0201-06.nc
tmp/file.0201-07.nc
tmp/file.0201-08.nc
tmp/file.0201-09.nc
tmp/file.0201-10.nc
tmp/file.0201-11.nc
tmp/file.0201-12.nc
```
Some people are [wary](https://medium.com/dot-debug/the-perils-of-bash-eval-cc5f9e309cae) 
of using `eval`. Anything that is in that statement will be executed, and they worry about 
malicious code being injected. In this case it isn't likely to be a problem, but bear this
in mind 

## sed

If `eval` worries you, or you just like the idea of doing yet another way, another option 
is to use the stream editor `sed`.

The command below is listing all the files, and then piping (`|`) the result into `sed`.
The sed script matches, and starts printing the input, when it encounters the first pattern, 
and stops after it encounters the second
```
$ ls tmp/* | sed -n "/$begin-01/,/$end-12/p"
tmp/file.0199-01.nc
tmp/file.0199-02.nc
tmp/file.0199-03.nc
tmp/file.0199-04.nc
tmp/file.0199-05.nc
tmp/file.0199-06.nc
tmp/file.0199-07.nc
tmp/file.0199-08.nc
tmp/file.0199-09.nc
tmp/file.0199-10.nc
tmp/file.0199-11.nc
tmp/file.0199-12.nc
tmp/file.0200-01.nc
tmp/file.0200-02.nc
tmp/file.0200-03.nc
tmp/file.0200-04.nc
tmp/file.0200-05.nc
tmp/file.0200-06.nc
tmp/file.0200-07.nc
tmp/file.0200-08.nc
tmp/file.0200-09.nc
tmp/file.0200-10.nc
tmp/file.0200-11.nc
tmp/file.0200-12.nc
tmp/file.0201-01.nc
tmp/file.0201-02.nc
tmp/file.0201-03.nc
tmp/file.0201-04.nc
tmp/file.0201-05.nc
tmp/file.0201-06.nc
tmp/file.0201-07.nc
tmp/file.0201-08.nc
tmp/file.0201-09.nc
tmp/file.0201-10.nc
tmp/file.0201-11.nc
tmp/file.0201-12.nc
```
As above, this can be used in a `bash` loop like so:
```
$ for file in $(ls tmp/* | sed -n "/$begin-01/,/$end-12/p"); do echo $file; done
tmp/file.0199-01.nc
tmp/file.0199-02.nc
tmp/file.0199-03.nc
tmp/file.0199-04.nc
tmp/file.0199-05.nc
tmp/file.0199-06.nc
tmp/file.0199-07.nc
tmp/file.0199-08.nc
tmp/file.0199-09.nc
tmp/file.0199-10.nc
tmp/file.0199-11.nc
tmp/file.0199-12.nc
tmp/file.0200-01.nc
tmp/file.0200-02.nc
tmp/file.0200-03.nc
tmp/file.0200-04.nc
tmp/file.0200-05.nc
tmp/file.0200-06.nc
tmp/file.0200-07.nc
tmp/file.0200-08.nc
tmp/file.0200-09.nc
tmp/file.0200-10.nc
tmp/file.0200-11.nc
tmp/file.0200-12.nc
tmp/file.0201-01.nc
tmp/file.0201-02.nc
tmp/file.0201-03.nc
tmp/file.0201-04.nc
tmp/file.0201-05.nc
tmp/file.0201-06.nc
tmp/file.0201-07.nc
tmp/file.0201-08.nc
tmp/file.0201-09.nc
tmp/file.0201-10.nc
tmp/file.0201-11.nc
tmp/file.0201-12.nc
```

## Conclusion

There are often many ways to accomplish even the simplest tasks, but sometimes
the hardest thing to know is what **not** to do.

Note also that this is very specific to `bash`. Other shells will have their own
limits and abilities.