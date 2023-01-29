---
layout: post
title: How to stop temporary files filling up your `/home` directory on Gadi
author: Dale Roberts
categories: storage, disk
---
# How to stop temporary files filling up your `/home` directory on Gadi

## Background

Many applications, often those designed around a desktop environment, tend to place their caches and other temporary data in a users `/home` directory. Unfortunately, on Gadi, this is the last place it should go. No only is `/home` quota limited to 10GB, but `/home` is also the slowest global filesystem on Gadi. The use of a users `/home` directory as temporary space in desktop-oriented applications is generally motivated by the assumption that `/home` is on the largest partition of the system. Furthermore, `$TMPDIR` is not used as it is assumed that it will be cleared on every reboot, and desktops tend to have irregular reboot cycles. All of these assumptions are false on Gadi. Applications that use the `/home` directory for temporary storage tend not to allow users to configure this, so a bit more work is needed to move this temporary storage away from `/home` on Gadi. The conventional way for doing this is to create a symlink in place of the directories containing temporary files within your `/home` directory. The following sections will detail how to find those directories, and how to move them to `/scratch`.

## Finding large directories on `/home`

To check your `/home` quota on Gadi, run the following command:
```
$ quota -s
Disk quotas for user dr4292 (uid 19147):
     Filesystem   space   quota   limit   grace   files   quota   limit   grace
gadi-home-fas.gadi.nci.org.au:/home
                  4067M  10240M  10240M           87809   4295m   4295m
```
This post will use my `/home` directory as an example. To get a breakdown of the size of every file and directory within the top-level of your `/home` directory, run the following command:
```
$ du -csh $( ls -A )
4.0K    .ICEauthority
40K     .Xauthority
4.0K    .ash_history
8.0K    .astropy
...
31M     test_venv
344K    um_output
7.1M    umui_runs
0       v45_gdata
4.1G    total
```
The above options for `du` cause it to give the total size for each argument (`-s`, i.e. show totals for directories, do not show their contents), create a `total` entry for the sum of the sizes of all arguments (`-c`) and use human-readable output (`-h`). The `$( ls -A )` as the final argument for `du` tells the shell to run the `ls -A` command and use its output as the remainder of the arguments to `du`.
```{note}
It is important to use the output of `ls -A` in `du`, as running `du -csh *` will not show hidden files or directories (those starting with `.`) by default. 
```
If you have a lot of files in your home directory, it may be useful to pipe the output of `du` to `sort -h`, which is able to parse the human-readable sizes from `du`:
```
$ du -csh $( ls -A ) | sort -h
0       .pbs_qmgr_history
0       v45_gdata
4.0K    .ICEauthority
4.0K    .ash_history
...
386M    .singularity
807M    .cache
904M    mdss_test_dir
1.3G    cylc-run
4.1G    total
```
The above shows the importance of listing hidden files, as over a quarter of my `/home` usage is in hidden directories. Based on this, the `.cache` directory is a good candidate for moving to `/scratch`. It takes up a significant portion of my `/home` usage, and as it is a cache, it is unlikely to cause applications to fail if its contents are expired.

## Moving directories to different filesystems without changing their path

To migrate the `.cache` directory to `/scratch`, I will run the following (note, substitute your project and username in place of mine):
```
$ cp -a .cache /scratch/v45/dr4292/tmp
$ rm -rf .cache
$ ln -s /scratch/v45/dr4292/tmp/.cache
```
```{note}
It is best to run this while you have no PBS jobs or any other background processes running, as there is a chance that a cache directory could be recreated in the time between the `rm` command and `ln` command.
```
This command makes a copy of `.cache` in your `/scratch` directory (every NCI user has a `tmp` directory created in their `/scratch/$PROJECT/$USER` directory for their default login project). The `.cache` directory is then removed from `/home` and a symlink is put in its place with the same name. 
```{note}
Use `cp -a` to preserve all permissions on the directory and its contents being copied. In general, `/scratch` directories are configured to be more permissive than `/home` directories. Using `cp -a` ensures that any more restrictive permissions inherited from `/home` are retained when the directory is copied
```
This means that every application that attempts to write to or read from `/home/563/dr4292/.cache` will actually be accessing `/scratch/v45/dr4292/tmp/.cache` (Note the trailing `/` in the second `ls` command to list the directory contents instead of symlink info):
```
$ ls -l .cache
lrwxrwxrwx 1 dr4292 v45 30 Jan 27 14:59 .cache -> /scratch/v45/dr4292/tmp/.cache
$ ls -l .cache/
total 32
drwxr-sr-x  3 dr4292 v45 4096 Nov  1 10:46 conda
drwxr-sr-x  2 dr4292 v45 4096 Dec  1 16:12 fontconfig
drwxr-sr-x  3 dr4292 v45 4096 Nov  8 11:41 jedi
drwxr-sr-x  2 dr4292 v45 4096 Oct 13 14:39 matplotlib
drwxr-sr-x 54 dr4292 v45 4096 Jan 25 17:27 numba
drwx--S---  5 dr4292 v45 4096 Oct 31 17:08 pip
drwxr-sr-x  3 dr4292 v45 4096 Nov  9 13:42 scikit-image
drwxr-sr-x  3 dr4292 v45 4096 Nov  3 13:02 yarn
```
After this, my `/home` quota and disk usage looks like this:
```
$ quota -s
Disk quotas for user dr4292 (uid 19147):
     Filesystem   space   quota   limit   grace   files   quota   limit   grace
gadi-home-fas.gadi.nci.org.au:/home
                  3299M  10240M  10240M           32051   4295m   4295m
$ du -csh $( ls -A ) | sort -h
0       .cache
0       .pbs_qmgr_history
0       v45_gdata
4.0K    .ICEauthority
...
386M    .singularity
904M    mdss_test_dir
1.3G    cylc-run
3.3G    total
```

## `/home` quota and ARE

If your `/home` quota is filled up for any reason, ARE jobs and jupyter notebooks will not be able to start, and will show the following error:
```
"Disk quota exceeded @ dir_s_mkdir - /home/.../ondemand/data/sys/dashboard/batch_connect/sys/jupyter/ncigadi/output/b8f7d971-9b27-4701-b97a-d418e5d2f0d8"
```
This is because the `ondemand` directory where ARE places the temporary files it uses to run jobs is always placed in a users `/home` directory. Unfortunately, it is not possible to use this method to move the `ondemand` directory, as the ARE head-node does not reside on Gadi, and therefore does not have access to `/scratch` or `/g/data`. The only way to restore access to ARE jobs is to clean other files and directories out of your `/home` directory.