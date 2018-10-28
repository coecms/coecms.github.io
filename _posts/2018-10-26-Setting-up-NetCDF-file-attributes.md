---
layout: post
title: Setting up NetCDF file attributes
author: Danny Eisenberg
excerpt: >-
    How to set up NetCDF global and variable attributes according to CF conventions
published: true
---

In a recent blog post we discussed how to make a NetCDF file. Now that we know how to make one, the next step is to find out what attributes should be included in the file moving forward.

# Why is this important?
There are 3 reasons why it’s necessary to set up the attributes correctly:
1. **Personal reference:** You need to be able to keep track of all the files you produce.
2. **Software operation:** Various NetCDF software utilities (e.g. CDO, NCO) expect a certain format and will not be able to properly process your file otherwise.
3. **File sharing:** Files which are intended to be shared with others, whether with colleagues, or in publications, need to follow accepted standards.

The two kinds of attributes you need to set are **global** and **variable** attributes. There are **Climate and Forecast (CF) conventions** for setting the attributes of NetCDF files.

# Setting the global attributes

Global attributes allow you and others know what this file is for. Of these, there are three levels of importance as set by the CF conventions:
1. Highly recommended
2. Recommended
3. Optional - i.e. not necessarily recommended.

Here is an excerpt from a random CMIP5 file I found on Raijin. (You can find it at `/g/data/rr3/publications/CMIP5/output1/UNSW/CSIRO-Mk3L-1-2/1pctCO2/mon/land/Lmon/r1i1p1/v20170728/mrro/mrro_Lmon_CSIRO-Mk3L-1-2_1pctCO2_r1i1p1_000101-014012.nc`):

```
// global attributes:
                :institution = "UNSW (University of New South Wales, Sydney, Australia)" ;
                :institute_id = "UNSW" ;
                :experiment_id = "1pctCO2" ;
                :source = "CSIRO-Mk3L-1-2 2009 atmosphere: R21 L18; ocean: 2.8x1.6 L21" ;
                :model_id = "CSIRO-Mk3L-1-2" ;
                :forcing = "GHG (GHG includes only CO2)" ;
                :parent_experiment_id = "piControl" ;
                :parent_experiment_rip = "r1i1p1" ;
                :branch_time = 0. ;
                :contact = "Steven Phipps (s.phipps@unsw.edu.au)" ;
                :history = "Data extracted from years 00201-00340 of experiment spi48 by Steven Phipps. 2013-07-27T05:06:01Z CMOR rewrote data to comply with CF standards and CMIP5 requirements." ;
                :comment = "Atmosphere and ocean models spun up independently for 100 and 7000 years respectively. Coupled model then spun up for 200 years before beginning this experiment. Flux adjustments applied to the fluxes of heat, freshwater and momentum." ;
                :references = "CSIRO Mk3L climate system model version 1.0 described and evaluated by Phipps, S. J., L. D. Rotstayn, H. B. Gordon, J. L. Roberts, A. C. Hirst and W. F. Budd (2011), The CSIRO Mk3L climate system model version 1.0 - Part 1: Description and evaluation, Geoscientific Model Development, 4(2), 483-509, doi:10.5194/gmd-4-483-2011. Version 1.2 described by Phipps, S. J. (2010), The CSIRO Mk3L climate system model v1.2, Technical Report No. 4, Antarctic Climate & Ecosystems CRC, Hobart, Tasmania, Australia, 122pp., ISBN 978-1-921197-04-8." ;
                :initialization_method = 1 ;
                :physics_version = 1 ;
                :tracking_id = "da13f69d-6501-4ffc-bda0-98945a8d8912" ;
                :product = "output" ;
                :experiment = "1 percent per year CO2" ;
                :frequency = "mon" ;
                :creation_date = "2013-07-27T05:06:01Z" ;
                :Conventions = "CF-1.4" ;
                :project_id = "CMIP5" ;
                :table_id = "Table Lmon (17 July 2013) 3f17a25f6a4bcd4bb2ac6986db9359fc" ;
                :title = "CSIRO-Mk3L-1-2 model output prepared for CMIP5 1 percent per year CO2" ;
                :parent_experiment = "pre-industrial control" ;
                :modeling_realm = "land" ;
                :realization = 1 ;
                :cmor_version = "2.8.3" ;
}
```

The highly recommended fields are those which will be necessary for you to identify your file. They are:
* `title`
* `summary`
* `keywords`
* `Conventions` - identifying the CF version number, and potentially other conventions that may be used, such as `ACDD`, as in the above example.

Note that the above example doesn’t contain summary or keywords. This would be acceptable practice if the title conveys sufficient information to potential readers.

The recommended fields listed above (in order of appearance) are: `institution`, `source`, `history` and `date_created` (called `creation_date` above).

The `history` attribute need not be added by you. Software utilities like cdo and nco will do that for you. Sometimes this field can become quite detailed (e.g. this file was added, this file was removed, etc). You want to make sure that it remains relevant and to the point, detailing which transformations were done on the data, for example.

The `source` attribute is there to provide a high-level description of how you generated your data.

What should normally happen is that you would provide the highly recommended global attributes when you first create the file and add more recommended fields gradually as you refine your file or seek to publish.

For a full list of *highly recommended*, *recommended* and *optional* attributes, see the [CF Attribute Convention document](http://wiki.esipfed.org/index.php/Attribute_Convention_for_Data_Discovery_1-3).

# Variable Attributes

Here are the variable attributes from the same file:

```
variables:
        double time(time) ;
                time:bounds = "time_bnds" ;
                time:units = "days since 0001-1-1" ;
                time:calendar = "365_day" ;
                time:axis = "T" ;
                time:long_name = "time" ;
                time:standard_name = "time" ;
        double time_bnds(time, bnds) ;
        double lat(lat) ;
                lat:bounds = "lat_bnds" ;
                lat:units = "degrees_north" ;
                lat:axis = "Y" ;
                lat:long_name = "latitude" ;
                lat:standard_name = "latitude" ;
        double lat_bnds(lat, bnds) ;
        double lon(lon) ;
                lon:bounds = "lon_bnds" ;
                lon:units = "degrees_east" ;
                lon:axis = "X" ;
                lon:long_name = "longitude" ;
                lon:standard_name = "longitude" ;
        double lon_bnds(lon, bnds) ;
        float mrro(time, lat, lon) ;
                mrro:standard_name = "runoff_flux" ;
                mrro:long_name = "Total Runoff" ;
                mrro:comment = "\"the total runoff (including \"\"drainage\"\" through the base of the soil model) leaving the land portion of the grid cell.\"" ;
                mrro:units = "kg m-2 s-1" ;
                mrro:original_name = "run" ;
                mrro:history = "Converted from volume flux per unit area (mm day-1) to mass flux per unit area (kg m-2 s-1) using density of 1000 kg m-3." ;
                mrro:cell_methods = "time: mean (interval: 20 minutes) area: mean where land" ;
                mrro:cell_measures = "area: areacella" ;
                mrro:associated_files = "baseURL: http://cmip-pcmdi.llnl.gov/CMIP5/dataLocation gridspecFile: gridspec_land_fx_CSIRO-Mk3L-1-2_1pctCO2_r0i0p0.nc areacella: areacella_fx_CSIRO-Mk3L-1-2_1pctCO2_r0i0p0.nc" ;
```

While global attributes usually won’t require tremendous precision, the same is not the case with variable attributes. The reason for this is that software utilities will expect certain standards to be adhered to completely and will not tolerate deviations.

The highly recommended attributes are the `long_name`, the `standard_name` and the `units`. The `long_name` is what you call the variable, while the `standard_name` is the official name found in the [CF Standard Name Table](http://cfconventions.org/Data/cf-standard-names/59/build/cf-standard-name-table.html). Software utilities will look for the latter in the file, and will expect to find `standard_names` for `latitude`, `longitude` and `time`. Furthermore, if you are using a search facility to search for a files with a particular variable type, it will likely look for the standard_name. The only reason not to include the standard_name for a variable is if it doesn’t have one.

## Units

Units are absolutely essential to include. Without them, they may be useless to use with software utilities; and even if not, the data will be difficult to use by anyone else. Sometimes one can guess (e.g. whether a temperature is in Kelvin or degrees Celsius), but it’s not always obvious.

The units provided will have to *essentially* match the CF standard’s units found in the table for the particular standard_name. I say “essentially”, because the units only need to be of the same general format. For example, the standard units for air density are `kg m-3`. If your file’s units for air density are units `g cm-3` that should also work, since it is still a unit of mass / volume.

If something is dimensionless, such as a %, ratio or mask, the unit should be recorded as “1”.

Time variable units can be a bit tricky to define. It is always recommended to specify which calendar is being used, but if you are not using a standard calendar, this will be **absolutely essential**. 

## A few points about recommended variable attributes

`Cell_methods` tell you what transformations have been performed on the data (e.g. mean or standard deviation), which is important to make clear, given that the units will probably not reveal this. For example, are the values given for a time series the instantaneous value at a particular moment, or the average of the values for the last hour, or the average of the values between -30 minutes to +30 minutes?
You can find more information about cell methods [here](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch07s03.html).

In some cases, you’ll need boundary attributes for a variable, such as `time_bnds`, `lat_bnds` and `lon_bnds` in the example above. You can find more information about those [here](http://cfconventions.org/cf-conventions/cf-conventions.html#cell-boundaries).

`Original_name` is important to provide if you have changed a variable name (whether for readability or other purposes). That way you can identify the original fields provided by the data source. Sometimes projects will use certain variable names. For example, CMIP6 used `tos` to refer to `sea_surface_temperature` (CF standard name).

In contrast to global attributes, when it comes to variable attributes, all the above should be included from the beginning, so that you don’t lose track of what’s going on.

# Real-life examples of problems with variables

Here are a couple of problematic cases that we’ve come across dealing with variable attributes:

**Example 1: `z1` variable**

The UM (Unified Model) defines the vertical axis with the `z1` variable:
```
               z1:standard_name = “height” ;
               z1:units = “m” ;
               z1:direction = “up”
```

Numerous mapping services (such as *wms*, *wfs* and *wcs*) and the NetCDF subset service, which we use when publishing data, were unable to recognise this variable until the following attribute was added:
```
               z1:axis = “Z”;
```

**Example 2: LIS time variable**

In LIS model outputs, time is defined as a string, e.g. `200101010000`, as opposed to the required `days since <reference date>`. To use such a file with common software tools, you would need to redefine the time axis correctly.

# Filenames

People don’t always think about it, but naming your files appropriately is probably the most important step in effectively keeping track of them. Naming directories appropriately is equally important, although it is not enough to rely on, because you may well take your file out of that directory at some point, and then you'll lose track of all the information in the directory name.

If we look at the file path of the sample file above, we can see that the information stored in the directories is replicated in the filename as well:
`/g/data/rr3/publications/CMIP5/output1/UNSW/CSIRO-Mk3L-1-2/1pctCO2/mon/land/Lmon/r1i1p1/v20170728/mrro/mrro_Lmon_CSIRO-Mk3L-1-2_1pctCO2_r1i1p1_000101-014012.nc`

We can say the properties used in the name:
* mon - time frequency - monthly
* land - modeling realm
* Lmon - land monthly
* CSIRO - institution
* mrro - variable name (runoff)
* r1i1p1 - ensemble name
* 1pctCO2 - 1 percent CO2 - experiment name 
* v20170728 - version in format yyyymmdd

Be aware that you don’t have to have it fully worked out from the beginning. You can improve the name progressively as you go.

# CF Convention Checkers

A CF convention checker is available on Raijin. To load it and see its command-line usage, do the following:
```
module use /g/data3/hh5/public/modules
module load conda
cchecker.py -h
```
However, be aware that CF checkers are not failsafe. Files which pass the check may not work with software utilities and vice versa. More information about how to use it can be found [here](https://github.com/ioos/compliance-checker#command-line-usage).

To summarise:
-------------
* The most essential attributes are those required by software utilities.
* The next most essential attributes are those which enable you and others to understand what your file is for, how it was made and what its values mean.
* Name your files and directories with a view to long-term usefulness.
* CF convention checkers exist, but are not failsafe.

*One final comment:* Other best practices include **internal compression** and **chunking**. We plan to discuss these in another blog post.
