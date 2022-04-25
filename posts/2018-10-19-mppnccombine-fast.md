---
layout: post
title: Fast MOM collation with payu and mppnncombine-fast
author: Aidan Heerdegen
excerpt: >-
    Introducing payu support for a new program for fast collation of tiled MOM outputs (or any other FMS based model)
categories: MOM, collate, mpi
published: true
---
# Fast MOM collation with payu and mppnncombine-fast

MOM ocean outputs (and restarts) are usually tiled: the output is distributed over multiple files
because it is faster. After the model is run the tile outputs are joined back together using a
program called `mppnccombine`.
 
As model resolution has increased it has become necessary to use compressed netCDF4 outputs
in order to save space. Compressed ocean data files are typically one half to one third the 
size of the equivalent uncompressed data.

The time taken to collate ouputs with higher resolution, particularly the 0.1 degree model, has
become burdensome. In some cases collation is taking longer than the model run itself. A large
part of the time taken to collate these files is due to uncompressing and recompressing the tiled
output.

Scott Wales has written [mppnccombine-fast](https://www.github.com/coecms/mppnccombine-fast) which
collates compressed netCDF4 data using functions in the HDF5 library (upon which netCDF4 is built) 
to directly copy compressed data without the extra steps of decompression and recompression.



## Requirements

1. You will need a `mppnccombine-fast` executable. Either use one I have compiled ``/short/public/aph502/mppnccombine-fast`` or get the [the source](https://www.github.com/coecms/mppnccombine-fast) and compile your own version

2. Place the executable in ``/short/$PROJECT/$model/bin`` or specify full path in ``config.yaml``

3. You must use a version of ``payu`` of ``0.10`` or greater (``module load payu/0.10`` on ``raijin``)

4. Updated ``config.yaml`` syntax


### Old Syntax

```yaml
collate: true
collate_mem: 16GB
collate_queue: express
collate_ncpus: 4
collate_flags: -n4 -r
```

### New syntax

Replaces ``collate_`` options with dictionary

```yaml
collate:
    enable: true
    queue: express
    memory: 4GB
    walltime: 00:30:00
    mpi: true
    ncpus: 4
    threads: 2
    # flags: -v
    # exe: /full/path/to/mppnccombine-fast
```

You *must* specify `mpi` to use `mppnccombine-fast`. Minimum of 2 cpus, so you can't use `copyq`. The number of cpus per thread is `ncpus / nthreads`. 

`nthreads` defaults to 1. `ncpus` defaults to 2 and `enable` defaults to `true`.

Don't *have* to specify `flags`, `enable` or `exe` unless you need to specify values other than the default. 

There are fewer `flags`, as `mppnccombine-fast` has fewer command options than `mppnccombine`
   
## Resource requirements

Memory use should only depend on chunksize in the compressed file, not on the overall size of the file being written. Unfortunately a memory leak bug in the underlying ``HDF5`` library means memory use will go up with the number of times data is written to a collated file. It is difficult to predict, but 2-4GB per thread has been the upper limit observed so far.

Walltime should be minutes. There is no speed-up for low resolution outputs (MPI overhead swamps fast run times). Also no speed advantage for uncompressed files, especially if `io_layout` is not specified, and there are hundreds or thousands of tiles.

There is a minimum of 2 cpus. Speed improvements up to 8 cpus in some cases has been observed, but experimentation is required to optimise this for any particular configuration, as the size and number of diagnostics can vary a great deal.


## Layout affects efficiency

Chunk sizes are chosen automatically by netCDF4 and depend on tile size. Inconsistent tile sizes leads to inconsistent chunk sizes. Inconsistent chunk sizes makes `mppnccombine-fast` slow as it has to do the uncompress/compress step for tiles which are not the same as the first

To ensure maximum speed make processor `layout` and `io_layout`, an integer divisor of grid. 

### Example

Quarter degree MOM-SIS model: 1440 x 1080. 
```fortran
layout = 64, 30
io_layout = 8, 6
```
* 1920 CPUs
* Tiles are 22 x 36 and 23 x 36
* IO tiles are 184 x 180, and 176 x 180
* Slow for collating normal data and slow for untiled data (restarts and regional output) 


### Improved Layout

Quarter degree MOM-SIS model: 1440 x 1080. 
```fortran
layout = 60, 36
io_layout = 10, 6
```

* 2160 CPUs
* Tiles are 24 x 10
* IO tile is 144 x 180
* Fast for collating tiled and untiled output