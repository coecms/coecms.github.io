
We created a database that contains information on the CMIP5 data available on raijin. We then created a python module **ARCCSSive** to help users accessing and interrogating the database. You might have used already one of our custom scripts that allows you to search for the files location directly from the command line, like *search_replica* .
Let's have a look now on how to search the database interactively so you can perform a search and work with the results directly from your python script.

First of all we need to load the conda/analysis27 environment, available both on raijin and the VDI, so we can use ARCCSSive.
&nbsp;&nbsp;&nbsp;&nbsp;module use /g/data/hh5/public/modules
&nbsp;&nbsp;&nbsp;&nbsp;module load conda/analysis27

The current version of ARCCSSive only works with python2, we are working on a new version in preparation for CMIP6, ARCCSSive2 will be available in conda/analysis3 .

We will also import numpy to do some simple calculation and netCDF4 function MFDataset( ) to open multiple netcdf files at once.


```python
from ARCCSSive import CMIP5
import numpy as np
from netCDF4 import MFDataset
```

After having imported the module **CMIP5** from ARCCSSive, we create a connection to the database.


```python
# step1: connect to the database
db=CMIP5.connect()
```

Then we use the **outputs( )** function to search the database. outputs( ) gets the *experiment, model, mip, ensemble* and *variable* as arguments. Any of these can be left out, so if we want to find all the models that have a r1i1p1 ensemble of historical monthly data for surface temperature, we pass all the corresponding arguments except *model*.


```python
# step2: search database without specifying the model
outs=db.outputs(experiment='historical',mip='Amon',ensemble='r1i1p1', variable='tasmax')
# we can see how many results were returned by the search
print("Search found %s results" % outs.count())
```

    Search found 45 results


Let's have a look at one of the results


```python
outs[0]
```




    <ARCCSSive.CMIP5.Model.Instance at 0x7f4040b48fd0>



It is a special object called **Instance** which represent a row from the database Instance table.
Each instance is defined by the arguments we listed above and can have one or more versions.
It is the **Version** table that contains the directory path the we need to access the files.


```python
print(outs[5].versions)
print(outs[5].versions[0].path)
```

    [<ARCCSSive.CMIP5.Model.Version object at 0x7f4040c25ed0>, <ARCCSSive.CMIP5.Model.Version object at 0x7f4040c25f90>]
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-3/historical/mon/atmos/Amon/r1i1p1/v20120413/tasmax


Most of the time we are interested only in the latest available version, we can use the *latest( )* function to do so.


```python
print(outs[5].latest())
print(outs[5].latest()[0].path)
```

    [<ARCCSSive.CMIP5.Model.Version object at 0x7f4040b7e8d0>]
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-3/historical/mon/atmos/Amon/r1i1p1/v20130325/tasmax


Unfortunately the CMIP5 replica directory often contains one or more copies of the same version. This is why *latest( )* always return a list and not only one version. So we need to use the "0" index to select one version.
NB. NCI is in the process of creating a new cleaner copy of CMIP5 which will eventually solve all these issues.

Let's now define a simple function which will get tasmax as input an return a mean value: 


```python
from glob import glob
def var_mean(var,path):
    ''' calculate max value for variable '''
    # open ensemble files as one aggregated file using MFDataset
    # Glob is required here in order to expand the path if using python 2, for python 3 is not needed
    #
    # using path+"/*.nc" should be sufficient, unfortunately GISS models break conventions and they put all variables in one directory
    #  so I'm using "/"+var+"_*.nc" just in case
    #
    expanded_path = glob(path+"/" + var + "_*.nc")
    nc=MFDataset(expanded_path,'r')
    data = nc.variables[var][:]
    return np.mean(data)
```

Now that we have defined a function let's pass the search results path to it, in this way we can calculate the mean on all the tasmax ensembles we found.

Let's now run the function for the results returned by the search, we used only the first 6 instances in this example. We simply have to pass the *path* attribute to the function. Rememebr path is defined in the Version table, along with the *version* label, while the *model* name is a  field on the Instance table.


```python
# step3: retrieve path for each version returned by search and pass it to function.
# I'm limiting this to the first 6 results

for o in outs[:5]:
    var = o.variable
    model = o.model
    for v in o.versions:
        varmean=var_mean(var,v.path)
        print('Mean value for variable %s, model %s , version %s is %s' %(var, model, v.version, varmean))
```

    Mean value for variable tasmax, model HadCM3 , version v20110823 is 278.319
    Mean value for variable tasmax, model MIROC4h , version v20110729 is 280.866
    Mean value for variable tasmax, model MIROC4h , version v20120628 is 280.866
    Mean value for variable tasmax, model CNRM-CM5-2 , version v20130401 is 279.091
    Mean value for variable tasmax, model CMCC-CM , version v20121008 is 279.159
    Mean value for variable tasmax, model MPI-ESM-MR , version v20120503 is 279.87


There are ways to execute more complex searches and/or filtering of the results returned by the *outputs( )* function. 
If you think this could be useful for you a more detailed explanations and examples of filters is 
available in the [**ARCCSSive training**](https://training.nci.org.au/mod/lesson/view.php?id=372) .


As for other NCI online trainings you need to use your NCI account to login. The ARCCSSive training is part of a CMIP5 induction. If you are new to CMIP5 then it is a good idea to check the entire training.
