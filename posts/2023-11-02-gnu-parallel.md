# Using GNU Parallel in bash scripts to optimize python processes

When it comes to data processing and computing intensive tasks, optimising your Python scripts to run in parallel can drastically improve performance. However, the mechanics of managing multiple Python processes ([`multiprocessing` module](https://docs.python.org/3/library/multiprocessing.html)) can be complex to achieve and limited in fucntionalitly. Thankfully, the [GNU parallel](https://www.gnu.org/software/parallel/) utility offers a simple and effective solution, allowing you to spread the workload of your scripts over multiple processors or cores.

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

We're running our bash script on Gadi where our jobs' resources like walltime, memory, and CPU are allocated using PBS directives and the job script is submitted into the PBS queue.

Here's what the `job.sh` script looks like:

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

INPUTS=~/inputs.txt 

declare -a array

while IFS= read -r line
do
    array+=("$line")
done < "$INPUTS"

printf "%s\n" "${array[@]}" | parallel -j ${PBS_NCPUS} --colsep ' ' python ~/test.py "{}"
```

Firstly, we are defining the resources our job will need, specifying them through PBS directives. Loading up the necessary modules using module load to have access to programs that aren't installed by default in our `PATH`.

A `while` loop reads from the file, storing each line as an element in the bash array.  `IFS=` prevents leading/trailing whitespace from being trimmed in each line, i.e. a space between columns. `-r` prevents backslash escapes from being interpreted, i.e. if we have a path as an input.

The `printf` command is used to print each element of the array on a new line and we use `|` to pipe the elements of the array to `{}`. Any sort of loop or sequence can be placed to the left of the `|`, for example if you only need to run something with 1 changing input:

```bash
seq 100 | parallel -j ${PBS_NCPUS} python ~/test.py "{}"
# This counts from 1 - 100 and uses those numbers as inputs into {}
```

The `-j` flag indicates the number of jobs that should run concurrently, in our case, we set it to the number of CPUs allocated to our job. 

`--colsep` flag defines the space `' '` as column separator in the input. Note that our `inputs.txt` file has columns separated by spaces.

That's it! It’s a simple but powerful way to run Python scripts in parallel. By distributing the workload among the available cpus, you can greatly improve your script’s efficiency. It’s an example of how to utilize the capability of bash scripting and powerful utilities like parallel to optimize Python workloads. Finally, the practical application of this can be extended by adjusting the bash and Python scripts to fit your actual needs.