---
layout: post
title: Using Gadi's software environment to build your applications
author: Dale Roberts
categories: python, fortran
---

# Using Gadi's software environment to build your applications

## Introduction

Gadi has a fairly unique software environment that can trip up some build systems. Unlike other HPC systems which may have many different installations of some software library installed corresponding to different compilers and MPI distributions, at first glance, Gadi appears to have only one installation of each library. This post describes how NCI implements a structure for libraries upon which other libraries and applications are built on Gadi. In particular, the focus of this page is in describing how otherwise incompatible libraries like those written in Fortran or built against MPI are merged on Gadi to allow transparent building of applications that depend on them. This post also includes a few steps that can be taken in order to resolve any potential build errors caused by this unique environment.

## Libraries
In this post, we refer to packages whose predominant use case is being built into other applications by the compiler/linker as '**libraries**'. This includes, but is not limited to, mathematical libraries (e.g. boost), data format libraries (e.g. netCDF) and MPI libraries. On Gadi, libraries in `/apps` are built to be compatible with every C and Fortran compiler on the system. In general, C has a consistent ABI ([Application Binary Interface](https://stackoverflow.com/questions/2171177/what-is-an-application-binary-interface-abi)), so a library built against `gcc` can be linked to an application built with the Intel Parallel Studio C and C++ compilers, Intel oneAPI C and C++ compilers or the Nvidia HPC Toolkit C and C++ compilers. This includes libraries provided on the system, but outside of `/apps`  (e.g. `libc`, `libm`, etc.). 

The Fortran standard does not specify an ABI, and as such, libraries built against the Intel Fortran compilers, the Nvidia HPC Toolkit Fortran compilers and the GNU Fortran compiler are *not compatible with each other*. On Gadi, NCI attempts to make many key libraries compatible with both the Intel oneAPI/Parallel Studio Fortran compiler and the GNU Fortran compiler. This is done by merging the Fortran components of two separate builds into a single installation tree, and invoking the compilers with custom **wrappers** that modify key environment variables transparently such that the compiler-specific libraries required are able to be found by the compiler building the target application which depends on these libraries. The [Technical Details](#technical-details) section below describes how this works, for those interested. You may be familiar with other HPC systems that use conventions such as netcdf/4.8.0-intel  to denote e.g. an Intel-compatible build, and the requirement to reload library modules when reloading the compiler modules. On Gadi, the absence of a suffix to the module version indicates that the library is able to link to an application built with either the Intel Fortran or GNU Fortran compilers without needing to reload the module. 

> ⚠️ The use of these compiler wrappers means NCI cannot guarantee this level of compatibility with user-installed libraries. 

> ⚠️ The Nvidia HPC Toolkit is not supported to the same extent as the Intel and GNU Fortran compilers, at this stage only OpenMPI has been built with an Nvidia HPC Toolkit compatible Fortran interface.

This approach can confuse some build systems that only check for the presence of a library or Fortran module file on a file system (e.g. early `Find<Package>.cmake` files used by CMake to automatically detect the presence of certain libraries), rather than attempting to link against it. Information on how to remedy this is in the [Debugging Build Failures](#debugging-build-failures) section below.

A similar approach is used for **MPI** distributions, taking advantage of MPI ABI compatibility initiatives (See e.g. the [MPICH ABI compatibility initiative](https://www.mpich.org/abi/)). Key parallel libraries are built against selected versions of OpenMPI and Intel MPI such that they can successfully link to an application built with any version of Intel MPI or OpenMPI installed in `/apps`. The MPI-enabled components of a library built by each version of MPI are merged into a single installation tree, and the correct components are selected by the compiler wrappers during build time. In the case that a library has both MPI and Fortran components, every combination of builds is structured in into a single installation tree such that the library can be linked into an application that has been built with any MPI library and Fortran compiler on Gadi. 


> ⚠️ The compiler wrappers do not support MPI installations outside of `/apps`. It is not recommended that users install their own MPI distributions, as NCI spends considerable time tuning and optimising the MPI distributions in `/apps` specifically for Gadi. 

Where a library has not been built to support all MPI modules on Gadi, NCI will generally use module conflicts to ensure that an incompatible MPI module cannot be loaded into the environment at the same time as the library.

> ⚠️ **OpenMPI v2 is deprecated on Gadi**. This means that any MPI-enabled library in `/apps` built after 30/06/2022 is not guaranteed to have an OpenMPI v2 compatible interface. OpenMPI v2 has been out of support since January 2019, and was provided on Gadi only to aid in the transition from Raijin. OpenMPI/2.1.6 will not be removed from Gadi, however, any users still using OpenMPI/2.1.6 are advised to port their applications to a more recent version of OpenMPI.

In most cases, building software on Gadi is as straight-forward as loading the appropriate modules and compiling. NCI's compiler wrapper system is generally clever enough to sort out exactly which libraries your application needs, and how to link them properly. If you're having trouble determining which modules should be loaded, check the linker error messages, e.g.
```
$ make
...
ERROR: cannot find libhdf5.so
ERROR: cannot find libhdf5_fortran.so
```
indicates that an HDF5 module should be loaded. Reviewing the installation instructions for the software you're using can also help, as they will usually contain a list of dependencies. Compare this with the output of the `module avail` command on Gadi. [Gadi has a large range of commonly used libraries installed](https://opus.nci.org.au/display/Help/Supported+Applications), and there is a good chance that your application dependencies may already be installed.

## Library Lists
### Libraries compiled with Intel and GNU Fortran interfaces
* HDF5 (all versions)
* netCDF (all versions)
* OpenMPI (all versions)
* boost (all versions)
* libint (all versions)
* libxc (all versions)
* magma (all versions)
* metis (all versions)
* petsc (all versions)
* elpa (all versions)
* arpack-ng/3.7.0
* fftw3/3.3.8
* grib_api/1.28.0
* hdf4/4.2.15
* pnetcdf/1.11.2
* silo/4.10.2
* wgrib2/2.0.8
### Libraries compiled with Nvidia HPC Toolkit Fortran interfaces
* OpenMPI (all versions)
* netCDF/4.9.0 and 4.9.0p
* hdf5/1.12.2 and 1.12.2p
### Libraries compiled with all MPI interfaces
* HDF5 (all parallel versions)
* NetCDF (all parallel versions)
* Score-P (all versions)
* parmetis (all versions)
* wannier90 (all versions)
* petsc (all versions)
* elpa (all versions)
* arpack-ng/3.7.0
* boost/1.72.0, 1.77.0, 1.79.0 and 1.80.0
* darshan/3.2.1
* fftw3/3.3.8
* ga (GlobalArrays) 5.7.2
* mpiP/3.4.1
* pnetcdf/1.12.2

## Debugging build failures
In most cases, NCI's method of supporting multiple Fortran/MPI distributions is transparent to build systems. Most popular build systems (e.g. `autotools`, `CMake`, `scons`, etc.) generally attempt to link to libraries or use  Fortran module files to determine whether or not they exist. In some cases, however, build systems like to emulate the behaviour of the compiler/linker and attempt to search for files directly. This is not ideal behaviour, as it does not take into account the fact that even though a file has the correct name and is on the correct path, it may not be a shared library or Fortran module file at all. For example, you may be building an application, and have all the correct modules loaded, but still see errors like
```
$ module load hdf5/1.12.1p
$ my_build_system_cmd
...
ERROR: cannot find libhdf5.so
ERROR: cannot find libhdf5_fortran.so
```

There are some steps that can be taken to attempt to remedy this. In this particular case, the 'parallel' version of HDF5 has been loaded (indicated by the ‘`p`’ in `hdf5/1.12.1p`). This library can only be linked when an MPI enabled compiler has been used, (i.e. `mpif90` ,or `mpifort`, or similar). In some cases, re-running the build with the Fortran compiler set to `mpifort` can resolve this issue. In other cases, switching to the 'serial' library is sufficient (i.e. the same module without the ‘p’ suffix), as the 'parallel' libraries are only required when your application uses MPI-enabled parallel features of the HDF5 library (see e.g. https://opus.nci.org.au/display/Help/HDF5).

If either of the above does not resolve your application building problem, you may need to explicitly tell the build system where the libraries are located. The method of doing this varies between build systems. In some cases, you may be able to do this by setting environment variables to the paths that contain the actual `libhdf5.so` and `libhdf5_fortran.so` files. For example:
```
$ prepend_path MY_BUILD_SYSTEM_LIBRARY_PATH "${HDF5_BASE}"/lib/omp3/GNU:"${HDF5_BASE}"/lib/omp3
```

may cause the build system to search in those directories. Alternatively, it may be a setting inside a build configuration file, e.g.
```
$ cat my_build_system.conf
...
LIB_SEARCH_PATH = /apps/hdf5/1.12.1p/lib/ompi3/GNU, /apps/hdf5/1.12.1p/lib/ompi3, /apps/hdf5/1.12.1p/lib, ...
```

Note that the above examples assume that an OpenMPI/3.x or OpenMPI/4.x module has been loaded, and an Intel Compiler module has not been loaded. If you are attempting this modification for your own build system, you will need to adapt the settings to your chosen MPI and Fortran distributions. We cannot guarantee that the above examples will work exactly this way for your build system. The general idea of adding MPI and Fortran subdirectories to library and include paths will resolve errors related to the layout of libraries in /apps , but the exact mechanism of modifying these paths will vary between build systems. If your application still does not build on Gadi after attempting these fixes, contact CLEX CMS through the #support channel on ARCCSS slack, or at cwshelp@nci.org.au  for further assistance.


## Technical Details
The top-level of a typical installation tree for a software module (either application or library) on Gadi might look like the following:
```
$ ls -l /apps/hdf5/1.12.1p/
total 16
drwxrwxr-x. 2 apps apps 4096 Jul 20 15:16 bin
drwxrwxr-x. 4 apps apps 4096 Jul 20 15:16 include
drwxrwxr-x. 5 apps apps 4096 Jul 20 15:16 lib
drwxrwxr-x. 3 apps apps 4096 Jul 20 15:16 share
```

Each directory has specific components of the installation in it, 
* the `bin` directory contains applications, 
* the `include` directory contains C/C++ headers and Fortran module files, 
* the `lib` directory contains shared libraries that contain the functionality of the library, and 
* the `share` directory generally contains documentation and/or man pages. 

Linux uses reserved **environment variables** in order to locate libraries when compiling an application (`LIBRARY_PATH` and `LD_RUN_PATH`) and libraries when *running* an application (`LD_LIBRARY_PATH`). In general, any module that provides a library will set all of these environment variables to the top level lib directory in the installation tree. In a similar manner, most compilers use reserved environment variables to find C headers (`CPATH` and `C_INCLUDE_PATH`), C++ headers (`CPLUS_INCLUDE_PATH`) and Fortran module files (`FPATH`). This is the reason that -L or -I flags (i.e. locations of shared libraries and header/module files) do not need to be specified for libraries in /apps . The linker inspects the contents of these variables to determine the location of any required libraries automatically. E.g. 
```
$ module load openmpi/4.1.2
$ module load hdf5/1.12.1p
$ echo $LIBRARY_PATH
/apps/hdf5/1.12.1p/lib:/apps/openmpi/4.1.2/lib:/apps/openmpi/4.1.2/lib/profilers
$ echo $LD_RUN_PATH
/apps/hdf5/1.12.1p/lib:/apps/openmpi/4.1.2/lib:/apps/openmpi/4.1.2/lib/profilers
$ mpif90 -o read_file_par read_file_par.f90 -lhdf5 -lhdf5_fortran
```

It is sufficient to simply load openmpi and hdf5 libraries to compile and link an MPI application against the HDF5 library on Gadi. The linker will search for the files `libhdf5.so` and `libhdf5_fortran.so` in each directory in `$LIBRARY_PATH`. Without NCI's compiler wrappers, this would fail, as those `.so` shared object files do not exist in any of those directories on Gadi.
```
$ ls /apps/hdf5/1.12.1p/lib/libhdf5.so
ls: cannot access '/apps/hdf5/1.12.1p/lib/libhdf5.so': No such file or directory
```

Instead, the libraries have been moved to subdirectories corresponding to the MPI distributions and Fortran compilers they were built against. NCI's compiler wrappers detect the Fortran compiler and MPI distribution in use at compile time, and transparently add those subdirectories to every entry in `$LIBRARY_PATH` before invoking the real compiler. An adventurous user can see this happening in real time by setting the environment variable `WRAPPER_DEBUG=y`. 
Setting `WRAPPER_DEBUG=y` writes a copious amount of information to `stdout`, and can cause builds to fail. Once you've satisfied your curiosity, it is best to unset `WRAPPER_DEBUG` 

```
$ export WRAPPER_DEBUG=y
$ mpif90 -o read_file_par read_file_par.f90 -lhdf5 -lhdf5_fortran
...
adjust_path_var: var=LIBRARY_PATH suffix=MPI fs_suffix=ompi3
vals="/apps/hdf5/1.12.1p/lib /apps/openmpi/4.1.2/lib /apps/openmpi/4.1.2/lib/profilers"
i="/apps/hdf5/1.12.1p/lib"
adjust_path_var: i=/apps/hdf5/1.12.1p/lib basename=/apps/hdf5/1.12.1p dirname=lib
adjust_path_var: found /apps/hdf5/1.12.1p/lib/ompi3
i="/apps/openmpi/4.1.2/lib"
adjust_path_var: i=/apps/openmpi/4.1.2/lib basename=/apps/openmpi/4.1.2 dirname=lib
i="/apps/openmpi/4.1.2/lib/profilers"
adjust_path_var: i=/apps/openmpi/4.1.2/lib/profilers basename=/apps/openmpi/4.1.2/lib dirname=profilers
LIBRARY_PATH="/apps/hdf5/1.12.1p/lib/ompi3:/apps/hdf5/1.12.1p/lib:/apps/openmpi/4.1.2/lib:/apps/openmpi/4.1.2/lib/profilers"
...
adjust_path_var: var=LIBRARY_PATH suffix=GNU fs_suffix=GNU
vals="/apps/hdf5/1.12.1p/lib/ompi3 /apps/hdf5/1.12.1p/lib /apps/openmpi/4.1.2/lib /apps/openmpi/4.1.2/lib/profilers"
i="/apps/hdf5/1.12.1p/lib/ompi3"
adjust_path_var: i=/apps/hdf5/1.12.1p/lib/ompi3 basename=/apps/hdf5/1.12.1p/lib dirname=ompi3
adjust_path_var: found /apps/hdf5/1.12.1p/lib/ompi3/GNU
i="/apps/hdf5/1.12.1p/lib"
...
LIBRARY_PATH="/apps/hdf5/1.12.1p/lib/ompi3/GNU:/apps/hdf5/1.12.1p/lib/ompi3:/apps/hdf5/1.12.1p/lib:/apps/openmpi/4.1.2/lib/GNU:/apps/openmpi/4.1.2/lib:/apps/openmpi/4.1.2/lib/profilers"
```


Note here that even though the `openmpi/4.1.2`  module is loaded, the wrappers have selected the `ompi3` subdirectory in the HDF5 library. This is because OpenMPI v3 and OpenMPI v4 have compatible ABIs. By inspecting the directories added to `$LIBRARY_PATH`, we can see that the linker will now be able to find the appropriate `libhdf5.so` and `libhdf5_fortran.so`.
```
$ ls /apps/hdf5/1.12.1p/lib/ompi3/libhdf5.so
/apps/hdf5/1.12.1p/lib/ompi3/libhdf5.so
$ ls /apps/hdf5/1.12.1p/lib/ompi3/GNU/libhdf5_fortran.so
/apps/hdf5/1.12.1p/lib/ompi3/GNU/libhdf5_fortran.so
```

> ⚠️ These modifications to the environment do not persist once the wrapper has exited, meaning that any changes to the environment do not persist beyond the invocation of the compiler.

MPI or compiler modules can be swapped at any point, and the correct MPI/Fortran-specific subdirectory will be added to the environment at compile time.

Inspecting the libraries actually linked using `ldd` shows the following:
```
$ ldd read_file_par
        linux-vdso.so.1 (0x00007fff75556000)
        libhdf5_ompi3.so.200 => /apps/hdf5/1.12.1p/lib/libhdf5_ompi3.so.200 (0x00007f7f41074000)
        libhdf5_fortran_ompi3_GNU.so.200 => /apps/hdf5/1.12.1p/lib/libhdf5_fortran_ompi3_GNU.so.200 (0x00007f7f40e07000)
        ...
```

The actual `hdf5` libraries linked into the application have different names to those specified on the compiler command line. This is due to the fact that the linker does not record filenames when linking libraries, instead it records the "`SONAME"` (for “shared object name”) . In Gadi's multiple Fortran/MPI installations, each library has an `SONAME` tagged with its Fortran/MPI version. This way, the `$LD_LIBRARY_PATH` environment variable cannot be used to accidentally load a library of the same name, but built against an incompatible Fortran/MPI distribution. The libraries on those paths are symlinks to the actual libraries in the MPI/Fortran specific subdirectories.
```
$ ls -l /apps/hdf5/1.12.1p/lib/libhdf5_ompi3.so
lrwxrwxrwx. 1 apps z30 16 Jul 20 15:16 /apps/hdf5/1.12.1p/lib/libhdf5_ompi3.so -> ompi3/libhdf5.so
$ ls -l /apps/hdf5/1.12.1p/lib/libhdf5_fortran_ompi3_GNU.so
lrwxrwxrwx. 1 apps z30 28 Jul 20 15:16 /apps/hdf5/1.12.1p/lib/libhdf5_fortran_ompi3_GNU.so -> ompi3/GNU/libhdf5_fortran.so
```
