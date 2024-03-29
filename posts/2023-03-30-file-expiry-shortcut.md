---
layout: post
title: Quick tip - Feed `nci-file-expiry` output back into itself
author: Dale Roberts
categories: storage, disk
---

# Quick tip - Feed `nci-file-expiry` output back into itself

Quite often, you may need to recover many files from quarantine on Gadi that match a particular pattern. Unfortunately, this is not simple as the output of `nci-file-expiry list-quarantine` looks like this:
```
8a17868a-25ec-40bf-a41d-264eb3505da8  2023-03-17 00:22:38  v45     528.0K  /scratch/v45/dr4292/tmp/tmpsuh6nuuu
994065d8-1e09-488f-aa1a-90ca1457609a  2023-03-17 00:22:38  v45       4.0K  /scratch/v45/dr4292/tmp/tmpfg8_ecs4
2fb7c18c-d415-47d5-a127-690a6a02d929  2023-03-17 00:22:38  v45       4.0K  /scratch/v45/dr4292/tmp/tmpgqno3ul4
ca649efd-ecbb-4225-b5cd-0432d916f280  2023-03-17 00:22:38  v45       4.0K  /scratch/v45/dr4292/tmp/tmp2qa21xk1
856bf663-8a4c-44bd-a1cf-8aeed3bbf639  2023-03-17 00:22:38  v45     512.0K  /scratch/v45/dr4292/tmp/tmp7mt1e23p
...
```
and `nci-file-expiry recover` expects this:
```
$ nci-file-expiry recover 856bf663-8a4c-44bd-a1cf-8aeed3bbf639 /scratch/v45/dr4292/tmp/tmp7mt1e23p
```
and `nci-file-expiry batch-recover` expects a file.

Fortunately, with a bit of `bash` trickery, it is possible to feed the output of one command to another _as if it were a file_. In this case, we can feed `nci-file-expiry list-quarantine` output back in to `nci-file-expiry batch-recover`. Let's imagine we're looking for files that match the pattern `*.ice_daily.nc`. Here is the command that does this:
```
$ nci-file-expiry batch-recover <( nci-file-expiry list-quarantined | grep .ice_daily.nc | while read uuid a b c d path; do echo $uuid $path; done )
```
It's fairly complicated, so let's break it down, starting with the commands in brackets:
```
nci-file-expiry list-quarantined | grep .ice_daily.nc | while read uuid a b c d path; do echo $uuid $path; done
```
The piping output to `grep` part is pretty standard, but what is less common is piping the results into a loop afterwards. `bash` considers the entire loop construct as a single command, so you can pipe command output or redirect files into one as you would any other command. The loop itself:
```
while read uuid a b c d path; do echo $uuid $path; done
```
`list-quarantined` output has 6 columns, but `batch-recover` is expecting a file with 2 columns, which correspond to the first and last columns of the `list-quarantined` output. This loop reads in the `grep`'d `list-quarantined` output line-by-line, saves each column into a different variable, and `echo`'s the ones we need. The rest are discarded. So running those commands connected with pipes gives us this:
```
$ nci-file-expiry list-quarantined | grep .ice_daily.nc | while read uuid a b c d path; do echo $uuid $path; done
813ff7b2-381b-430b-a423-f32b449bf710 /scratch/v45/dr4292/20200222.ice_daily.nc
9aa317e3-7763-4af5-a19b-d07a7d6c2d90 /scratch/v45/dr4292/20200223.ice_daily.nc
28b0d00c-e9fc-4e5e-adae-39a817d0fb51 /scratch/v45/dr4292/20200224.ice_daily.nc
8a17868a-25ec-40bf-a41d-264eb3505da8 /scratch/v45/dr4292/20200225.ice_daily.nc
...
```
```{note}
There are many ways to organise columnated data in `bash`. The `while read echo` variant above is my preference. If you prefer piping to `awk` or `cut`, substitute that instead. As long as the output looks like the output above, the next bit will work.
```
To turn this into a "file" that `batch-recover` is happy to deal with, we can take advantage of [process substitution](https://en.wikipedia.org/wiki/Process_substitution). This tricks `batch-recover` into treating the output of the above command as if it were a file, even though nothing is ever written to disk. So by wrapping the above command in `<( ... )`, its output becomes, for all intents and purposes, the contents of a file.

Process substitution enables a few neat tricks. For instance, if you need to `diff` the output of two commands, you do not need to write the output to temporary files first, you can simply run:
```
$ diff <( command_1 ) <( command_2 )
```
You can also add an additional `<` operator to redirect this output to `stdin`. The original version of this command posted on slack and the ACCESS-Hive used this to get the output of `list-quarantine` into the loop.
```
while read uuid a b c d path; do echo $uuid $path; done < <( nci-file-expiry list-quarantined | grep .ice_daily.nc )
```
However, there are restrictions on using process substitution. The `seek` instruction cannot be used on these "files", meaning that they can't be used in place of structured data (e.g. netCDF). For simple things like this though, that isn't relevant.

This is a lot to remember, so we recommend placing the following in your `~/.bashrc` file:
```
function recover_pattern () {
    nci-file-expiry batch-recover <( nci-file-expiry list-quarantined | grep "${1}" | while read uuid a b c d path; do echo $uuid $path; done )
}
```
And when you log into Gadi again you'll be able to run:
```
$ recover_pattern .ice_daily.nc
```
for the same effect. As the function argument is passed straight to `grep`, regular expressions can be used to search for files, e.g. recover all `.ice_daily.nc` files starting with 2020, 2021 and 2022
```
$ recover_pattern "202[012].\+ice_daily.nc"
```
note the pattern must be wrapped in quotes in this case. It can also be used to recover files on a specific path. For instance, to recover files in your current directory:
```
$ recover_pattern "${PWD}"
```
