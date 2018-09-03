---
layout: post
title: Storage: where, what why and how?
author: Aidan Heerdegen
excerpt: >-
    Where is my stuff? What even is it? Why is it taking up so much space and how can I fix it?
categories: visualisation, R, Shiny
---

Simulations, analysis, modelling, use and/or create data.

Space is limited, need to optimise storage. 

**Where** is the largest disk usage
**What** is using up the disk space
**Why** it is there (data triage: maybe you no longer need it) 
**How** you can reduce your usage to make room for MORE!


# Where

Find your disk storage quotas and usage in one hit
```
lquota
```
More detail for a single project is available using the `nci_account` command
```
nci_account -P project_id
```
To query usage for an on-disk file system NCI provides commands which report on daily crawls of the filesystem. On NCI systems it is the group of a file that determines how it is accounted for, not where it resides on the filesystem
```
short_files_report -G project_id
gdata1_files_report -G project_id
```

For Centre of Excellence projects (and a few others) can track usage over time using `ncimonitor`. To access this command:
```
module use /g/data3/hh5/public/modules
module load conda
```
```
ncimonitor -P project_id --short --gdata --showtotal
```
Show only your usage
```
ncimonitor -P project_id --short --gdata -u $USER
ncimonitor -P project_id --short --inodes -u $USER
```
Look at the change in your short file usage since the beginning of the quarter
```
ncimonitor -P project_id --short -u $USER --delta
```

# What?

When you know where to look, need to find out what is using all the disk space. Can use `ls`, `du` and `find`
```
ls -lSrh dir
du -shc dir/* | sort -h
for d in dir/*; do echo $(find $d | wc -l) $d; done | sort -n
```
But there is a better tool: `ncdu`
```
ncdu directory_name
```

Once you've found the files taking the space, need to find out what are they?
```
file filename
```
What is inside a UM history file, netCDF file, grib file (as some examples of common data file types)
```
xconv history_file
ncdump -hs netcdf_file
grib_ls grib_file
```

# Why?

Why do I have these in the first place? If you're running a model: check the diagnostics (output variables) you 
output. Do you need them all? Before starting a run check you will have enough space to store it all

Analysing data: does your workflow involve:

* making copies of locally accessible data?
* creating transformed intermediate copies of data?

Explore other approaches! You may be needlessly making multiple copies of data when a different approach could eliminate this.

How?
----------

How can I use less disk space? Data triage: Why am I storing these files?

Archive if:

* no longer require fast access, e.g. for analysis

Delete if:

* not required
* duplicates of data available with similar access time (on disk, readable) or with a longer access time (mass data, off-site) if no longer require fast access
* intermediate data for analysis (keep scripts to regenerate (version control))

How can I use less disk space for the files/fields I must keep? Compression!

netCDF4 has lossless internal compression (transparent to user) ½ to ¼ size of uncompressed 

Output compressed netCDF4 directly from models/analysis where possible.

Otherwise use compression tools.

nccompress can be used to batch compress netcdf files
```
	nccompress -r -o -p -b 500 directory_name
```

You can reduce the precision of netCDF data: known as packing.

The CF conventions have standard attributes that CF compliant tools support: variable attributes `scale_factor` and `add_offset` are used to reduce the precision of the variable. Generally halves size of file. 

Useful when data is produced: problems can be corrected and data regenerated. We don't recommend packing existing data: it is lossy and there is high potential for corruption, but if you must `nco` (`module load nco`) has a tool for packing
```
ncpdq -L 5 infile.nc outfile.nc
```

UM history files can be compressed with tools like gzip, but this can be time consuming and the file must be uncompressed before using.
Alternatively convert to compressed netCDF4.
```
~access/bin/um2netcdf.py -i um_file -o um_file.nc -k 4 -d 5
```

Text files (and binary files) generally compress well, a lot of redundant information. This is lossless compression
```
gzip textfile
```
Will create textfile.gz and delete the original file.

To uncompress
```
gunzip textfile.gz
```

There is a limit on inodes (number of files). If you are close to this limit you need to reduce the number of files you are storing.

IOne solution if you have a large number of netCDF files is to aggregate them. 

Some models produce large numbers of files, e.g. one per time step. Dimensional information and metadata is repeated, so it is redundant, so this approach saves on space as well.

Use `nco` (`module load nco`)
```
ncecat *.nc -O merged.nc
```

If you have a large number of text files (logs etc) you can use `tar`:
```
tar zcvf tarfile.tar.gz directory_name
```
This will put all the files in a single tape archive file and compress everything on the fly 

To see the contents of a tar file:
```
tar ztvf tarfile.tar.gz
```
and to uncompress and restore all files
```
tar xvf tarfile.tar.gz
```

Move data to up the storage hierarchy. 
```
short	<	gdata 	< 	massdata
```
In general the higher up the hierarchy the greater the available storage, but files should be larger as inode reduces for same storage.

Have a data workflow that moves data from short to gdata to massdata in a planned manner. 

If inode quota is already tight on short, files must be aggregated when moving up the hierarchy. massdata is faster with larger file sizes due to physical limits of tape.


To move data up the storage hierarcy, need to copy data from one on-disk filesystem to another. Can use `cp`
```
cp -r origin destination
```
Use rsync for large operations, if it times out, can run the same command and restart
```
rsync -va origin destination
```

In some cases it is important to not enforce group ownership, so don't use `-a` but option spaghetti `-rltoD`
```
rsync --ignore-existing -vrltoD --safe-links origin destination
```

But but but …

    "Massdata is a big black hole where data goes to die"

Well, sort of …

NCI supported methods:
```
netcp -P project_id -t archivename.tar localdir $USER/remotedir
mdss -P project_id put -r localdir $USER/remotedir
mdss -P project_id get -r localdir $USER/remotedir
```

You can put large amounts of data with netmv / netcp. Makes tar file of directory, can be slow and increase disk usage in short term. Data must be retrieved in large quanta. Using mdss to transfer as-is will generally time out before all data is transferred.

CMS has written a tool (`mdssdiff`) to help with this.
Show difference between local directory and remote copy on `mdss`:
```
mdssdiff localdir -p $USER/path_to_localdir_on_mdss
```

Sync local directory to mdss (recursively) with `--copyremote/-cr` option
```
mdssdiff -cr -r localdir -p $USER/remotedir
```

Sync remote directory from mdss (recursively) with `--copylocal/-cl` option
```
	mdssdiff -cl -r localdir -p $USER/remotedir
```

As above, but specify project
```
	mdssdiff -P project_id -cl -r localdir -p $USER/remotedir
```

# How? In the future

Future plans to make it easier and more attractive to transfer files to massdata:

`mdssprep` - traverse a directory structure, archiving as required, and recording a manifest describing all files

`mdssfind` - find files that have been transferred to massdata and optionally call mdssdiff to copy them back to a local directory