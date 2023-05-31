# Adding a new task to a rose suite

## Issue
In this example, we want to add an additional task to an ACCESS-CM2 run, to be executed before every instance of the coupler to update the sea surface temperature ancillary file.

## Step 0: Make a copy of the ACCESS-CM2 suite
Run this command on accessdev to make a copy of the **ACCESS-CM2** suite:
```bash
rosie copy u-br565
```

This command will create a copy of the original ACCESS-CM2 suite with a new suite-id that we can modify and track without interfering with the original suite.

"Suite Directory" from now on will mean the directory `${HOME}/roses/<suite-id>`.

## Step 1: Make a shell script to update the SST files:
Create a file called `update_sst.sh` and located in the directory `apps/update_sst/bin` under your rose suite directory:

```bash
#!/bin/bash

# Ensure that the relevant variables are set:

test -z ${FILE_TEMPLATE} && exit 1
test -z ${SST_FILE} && exit 2
test -z ${YEAR} && exit 3

# Obtain current model year f
export YEAR_FILE=${FILE_TEMPLATE/YEAR/${YEAR}}
echo ===============================================
echo Running script to update Sea Surface Temparatures
echo Input file: ${YEAR_FILE}
echo Output file: ${SST_FILE}
echo ===============================================

CMD="cp ${YEAR_FILE} ${SST_FILE}"
echo $CMD
$CMD || exit 4
echo ===============================================
```

Make sure that the script is executable by running the command:
`chmod +x update_sst.sh`

## Step 2: Create an option for running the task

Modify the file `rose-suite.conf` in your suite directory:
Somewhere in the section `[jinja2:suite.rc]` (which should be the only section in this file), add the line:
```jinja2
UPDATE_SST=true
```

### Step 2a: Create Metadata for the new option
Modify the file `meta/rose-meta.conf` and add this block:
```jinja2
[jinja2:suite.rc=UPDATE_SST]
compulsory=true
description=Run a script to update the SST files every run
help=
title=Update SST
ns=Build and Run
sort-key=3
type=boolean
```
More info on the metadata can be found on the [Rose Documentation on Metadata](https://metomi.github.io/rose/doc/html/api/configuration/metadata.html)

What's important is that this will add the option to switch the task on and off to the `suite conf` -> `Build and Run` window in **rose**.

## Step 3: Add the configuration for the task
Create a new subdirectory `app/update_sst` and in this directory, create the file `rose-app.conf`:
```jinja2
[command]
default=update_sst.sh
[env]
FILE_TEMPLATE=/PATH/TO/SST_FILES/sst_YEAR_something.nc
SST_FILE=work/ocean/INPUT/temp_sfc_restore.nc
```

Note that these are the default values.
There is an option to change these values in the rose editor.

### Step 3a: Add the metadata for the task
Create a new subdirectory `app/update_sst/meta`. 
In this subdirectory, create the following file `rose-meta.conf`:
```jinja2
[env=FILE_TEMPLATE]
description=All SST Files
help=Template of the files that contain the sea surface temperatures by year.
    =the term YEAR will be replaced with the actual year.
compulsory=true
pattern=^.*YEAR.*$

[env=SST_FILE]
description=SST File
help=SST file expected by model
compulsory=true
```

## Step 4: Create the environment for the new task
Edit the file `suite.rc`

Search for the entry `[[coupled]]`, create a new section directly before that called `[[update_sst]]`:
```jinja2
    [[update_sst]]
        inherit = None, NCI, SHARE
        script = rose task-run --verbose
        [[[remote]]]
            host = {{ COMPUTE_HOST }}
        [[[job]]]
            batch system = background
        [[[environment]]]
            YEAR = $(cylc cyclepoint --print-year)
```

The line `batch system = background` overwrites the setting `batch system` setting of `[[NCI]]` and makes the job run on the login node, which means it will run directly and not spend time in the queue. That's possible because it's a very short and straightforward job. 

If it were more complicated, we'd omit the `[[[job]]]` section so that it inherits the PBS settings from `[[NCI]]` and runs as a queued job.

## Step 5: Add the task into the graph.
We now need to add the `update_sst` task to the task graph, if `UPDATE_SST` is true.
The graph is described in two sections, `[[[ R1 ]]]` for the initial run, and `[[[ {RESUB} ]]]` for successive runs.

The second is easier to read, so we start there.

On line 86, we *add* the new part graph:
```jinja2
{% if UPDATE_SST %} 
filemove[-{{RESUB}}] => update_sst => coupled 
{% endif %}
```

The central location in the graph for `[[[ R1 ]]]` is harder to parse, manual folding of `if` and `endifs` is needed to deduce that the central graph for running the model is in line 72 and reads:

```jinja2
install_ancil => coupled
```

We *insert* our task in this line like this:

```jinja2
install_ancil => {{ "update_sst => " if UPDATE_SST else "" }} coupled
```

## Step 6: Check in your changes.

```bash
svn add app/update_sst
svn ci -m 'include script to update SST files'
```

