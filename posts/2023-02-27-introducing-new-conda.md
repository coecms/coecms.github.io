---
layout: post
title: Introducing the new hh5 conda environment
categories: python
---
# Introducing the new hh5 conda environment

## Background
The hh5 python/conda environment has grown vastly in scope since it was first installed many years ago. What started as a place to put important python packages missing from NCI's installations has since become an agile, community-driven, monolithic installation serving almost 600 researchers. Currently, there are 261 packages listed in the file used to construct and update the environment. Once all of the dependencies of these packages are factored in, there are 1,015 total python packages installed in the current `analysis3-unstable` environment. As a result of the work put in by my predecessors at CLEX CMS, an update to the `analysis3-unstable` environment, from a researcher requesting a package through cws_help@nci.org.au to integration and testing of that package, can be completed in under 1 hour.

That being said, there are issues that had to be addressed going forward.

 * The size of the environment;

     At 1,015 packages, the current `analysis3-unstable` environment contains 289,524 files, directories and symlinks. At approximately 10GB in size, this corresponds to an average file size of around 36kB, which is not suitable for the lustre file systems that the conda environments are installed on.
 * The lack of integration with NCI systems;

    As conda is designed to create integrated environments on single-user systems, it installs packages like MPI and SSH, which are not configured correctly for NCI's systems, causing issues such as MPI not working across multiple nodes, or ssh host-based authentication failing.

The new hh5 conda environment, herein referred to as `conda_concept` is our attempt to address these issues while retaining the all the strengths of the current `conda/analysis3` environments. It is a combination of container and [squashfs](https://en.wikipedia.org/wiki/SquashFS)-based solution, though use of a container is only a byproduct of Singularity's ability to manage `squashfs` filesystems.  It combines ideas from [Singularity Registry HPC](https://singularity-hpc.readthedocs.io/en/latest/), [Rioux et al. *PEARC '20: Practice and Experience in Advanced Research Computing, July 2020, Pages 72–76*](https://doi.org/10.1145/3311790.3401776) and the current `analysis3` environments.

## In short

* Same packages as current `analysis3` environments
* Addresses issues with the installation and maintenance of current `analysis3` environment.
* Will be maintained in parallel with standard hh5 conda for at least 3 months.
* Will retain `analysis3-stable/unstable` structure and (roughly) quarterly update time
* New module name - `conda_concept` - to use on Gadi e.g.
```
$ module use /g/data/hh5/public/modules
$ module load conda_concept/analysis3-unstable
$ python3
```
* `analysis3/22.07`, `analysis3/22.10` and `analysis3/23.01` environments are available - they are exact duplicates of the corresponding existing `analysis3` environments.
* Some catches:
    * Can't use direct path to interpreter, must use path to the 'scripts' directory instead if a full path is needed (e.g. in `#!/g/data/hh5/.../python3` shbang lines in scripts)
    * `conda activate` does not work, must load the module.
* Any problems or questions, contact cws_help@nci.org.au, or leave an issue on the [github page](https://github.com/coecms/cms-conda-singularity/issues).

## Usage
Usage of the new `conda_concept/analysis3` environments is very similar to the current `conda/analysis3` environments. On the Gadi command line, or in PBS scripts, run
```
$ module use /g/data/hh5/public/modules
$ module load conda_concept/analysis3
```
The version naming scheme is not changing. The `analysis3-unstable` environment will always be an alias for the most recent environment and will continue to be updated at roughly 3 monthly intervals. `analysis3` will remain the most recent "stable" environment.
```
$ module load conda_concept
```
will load the "stable" environment. Specific versions can also be loaded with e.g.
```
$ module load conda_concept/analysis3-23.01
```
The typical `analysis3` workflow comprising python scripts or jupyter notebooks should seamlessly carry over to the new `conda_concept` environments. If your workflow does not, please contact cws_help@nci.org.au or leave an issue on the [github page](https://github.com/coecms/cms-conda-singularity/issues).

## Key differences between `conda_concept` and `conda`
The key difference of the approach used by the `conda_concept` environments is the use of singularity's ability to manage squashfs file systems. A squashfs can be thought of a something like a tar file that can be accessed as if it were an entirely new file system. The obvious advantage of placing a conda environment in a squashfs is that it reduces the file count of the entire environment on `/g/data` to one.

The drawback of using singularity to manage the squashfs is that containers have a number of restrictions placed on them for security reasons, (e.g. the `newgrp`, `switchproj` and `qcat` commands cannot be run from inside a container). Because of this, once the module is loaded, the user is kept out of the containerised environment unless a command that exists inside the container is run. This is accomplished by the use of a 'launcher' script that runs `singularity` and executes the command from within the container. For more details on this, see the [CMS Wiki page](https://climate-cms.org/cms-wiki/resources/resources-conda-setup.html). This leads to known issues with the environment.

### Known Issues
 * The path to the python executable within a conda environment cannot be used as the shbang (e.g. `#!/g/data/hh5/public/apps/cms_conda/envs/analysis3/bin/python3` on the first line of script) as the executable does not exist outside of the container. Instead, use the launcher script symlink: `#!/g/data/hh5/public/apps/cms_conda_scripts/analysis3.d/bin/python3`, which launches the container and runs the script from inside of it.
 * `conda env` commands do not work. This is because the `conda` command runs outside of Singularity and does not have any visibility into the environments.
 * `conda activate` does not work. Loading the module is equivalent to running `conda activate` for a given environment, however, `conda deactivate` and `conda activate` to load a different environment after loading the module will not work. 
 * Very occasionally, a package may fail to import with `IOError`. This is an issue with the underlying file system. To aid in diagnosis, please submit the PBS jobid and/or node you were working on and the time at which the import failed.

 If you encounter any problem not listed here that is fixed when you revert to the standard `conda/analysis3-unstable` environment, please contact cws_help@nci.org.au, or leave an issue on the [github page](https://github.com/coecms/cms-conda-singularity/issues).
