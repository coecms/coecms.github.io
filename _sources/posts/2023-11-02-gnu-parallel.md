# Using GNU Parallel in bash scripts to optimize python processes

When it comes to data processing and computing intensive tasks, optimising your Python scripts to run in parallel can drastically improve performance. However, the mechanics of managing multiple Python processes ([`multiprocessing` module](https://docs.python.org/3/library/multiprocessing.html)) can be complex to achieve and limited in functionality. Thankfully, the [GNU parallel](https://www.gnu.org/software/parallel/) utility offers a simple and effective solution, allowing you to spread the workload of your scripts over multiple processors or cores.

In Python, a common use case scenario is when you have a list of inputs, and you want to process each item in the list independently. In this blog post, we’re going to use bash shell scripting along with PBS to schedule and manage the jobs for our Python script, which is set to run in parallel using GNU parallel on Gadi.

We'll use this Python script, `test.py`, for demonstrating purposes:

```python
import sys

def main(arg1, arg2, arg3):
    print(f'Argument 1: {arg1}')
    print(f'Argument 2: {arg2}')
    print(f'Argument 3: {arg3}')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f'Usage: python {sys.argv[0]} arg1 arg2 arg3')
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
```

The script prints three argument values passed to it via command line. It's designed to fail if not exactly three arguments are provided.

Our inputs for this python file are going to be loaded from an input file, `inputs.txt`:

```text
1 2 3
one two three
path/to/files 7 option
file.nc out.cn 2023
```

Note that for this example I have `inputs.txt` and `test.py` located in my `$HOME` directory.

## Job.sh script with options for different scenarios

We're running our bash script on Gadi where our jobs' resources like walltime, memory, and CPU are allocated using PBS directives and the job script is submitted into the PBS queue. We also need to load up the necessary modules using `module load` to have access to programs that aren't installed by default in our `PATH`.

```bash
#!/bin/bash

#PBS -q normal
#PBS -P v45
#PBS -l ncpus=4
#PBS -l walltime=0:05:00
#PBS -l mem=2gb
#PBS -l jobfs=2GB
#PBS -l wd
#PBS -l storage=gdata/hh5+gdata/v45
#PBS -j oe

module load parallel
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
```

### Read contents of `inputs.txt`:

First we create a variable with `inputs.txt` and its directory location. Then we declare an array to save its contents to.

```bash
INPUTS=~/inputs.txt 

declare -a array
```

#### Option 1:

```bash
while IFS= read -r line
do
    array+=("$line")
done < "$INPUTS"
```

A `while` loop reads from the file, storing each line as an element in the bash array.  `IFS=` prevents leading/trailing whitespace from being trimmed in each line, i.e. a space between columns. `-r` prevents backslash escapes from being interpreted, i.e. if we have a path as an input.


#### Option 2:

```bash
array=$(cat ~/inputs.txt)
```

The `cat` command in Linux is used to read and concatenate files to the standard output. Here we capture the output of the `cat` command and save it into our array.


### GNU Parallel command:

#### Applying Option 1 or 2:

```bash
printf "%s\n" "${array[@]}" | parallel -j ${PBS_NCPUS} --colsep ' ' python ~/test.py "{}"
```

The `printf` command is used to print each element of the array on a new line and we use `|` to pipe the elements of the array to `{}`. 

The `-j` flag indicates the number of jobs that should run concurrently, in our case, we set it to the number of CPUs (`ncpus=4`) allocated to our job. 

`--colsep` flag defines the space `' '` as column separator in the input. Note that our `inputs.txt` file has columns separated by spaces.


#### Applying a new Option:

You mightn't need to assign the contents of `inputs.txt` to an array at all. You could use `-a $INPUTS` to pass its contents straight to your python script.

```bash
parallel -j ${PBS_NCPUS} --colsep ' ' -a ~/inputs.txt python ~/test2.py
```


### Extra options:

There are endless variations to get this script to work for your specific needs, here are a few extra things.

#### Using `|`:

Any sort of loop or sequence can be placed to the left of the `|`, for example if you only need to run something with 1 changing input:

```bash
seq 100 | parallel -j ${PBS_NCPUS} python ~/test.py "{}"
```

This counts from 1 to 100 and uses those numbers as inputs into {}

#### Using arguments created within Job.sh:
Maybe you need to get some arguments from the text file and 1 from the script, i.e. a variable name.

```bash
var="tasmin"

parallel -j ${PBS_NCPUS} --colsep ' ' -a ~/inputs.txt python ~/test2.py ::: $var
```

In this case the contents of `~/inputs.txt` are passed as the first arguments and the `$var` is the final argument. If you have multiple values for var then you can combine this with a pipe (`|`) command to loop through them. 

#### Debugging:

Of course things aren't going to work first time so it's good to have a way to figure out the problem. Including `--verbose` in the parallel command prints out what parallel is trying to run. This helps to show whether your arguments are working correctly.


## Wrap-up

That's it! It’s a simple but powerful way to run Python scripts in parallel. By distributing the workload among the available cpus, you can greatly improve your script’s efficiency. It’s an example of how to utilize the capability of bash scripting and powerful utilities like parallel to optimize Python workloads. Finally, the practical application of this can be extended by adjusting the bash and Python scripts to fit your actual needs.