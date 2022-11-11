# Data Quarantine

Your data in /scratch/ can be deleted if it haven't been accessed/modified for 100 days. NCI introduced this in May 2022 to try and help prevent the build-up of unused data. The data is first moved from project directories on /scratch/ into a quarantine space where you will have 14 days to recover it if needed.

See these websites for more info:

http://climate-cms.wikis.unsw.edu.au/Scratch_file_expiry

https://opus.nci.org.au/pages/viewpage.action?pageId=156434436

Dealing with data that has been moved to quarantine is actually quite simple and if you need to recover it then there are just a few steps to follow.

## Viewing Data Expiry Date:
----------------------------------------------------------------

To list all of your data in a specific project (i.e. w40) and see what is at risk of being moved to quarantine or deleted: 

```bash
nci-file-expiry list-warnings -p <project> > expiry_warning_<project>.txt
```

This will save the output to a txt file (expiry_warning_w40.txt if you used <project>=w40) that you can open. In this txt file you will find information for all your at risk data under the following headers:

- EXPIRES AT: This will give you the date when your file will move into quarantine.
- GROUP: The project your file belopngs to, i.e. w40.
- SIZE: How big your file is, i.e. 10GB
- PATH: Where your file is located.

If you would like to look specifically at data that you already know is in quearantine:

```bash
nci-file-expiry list-quarantined -p <project> > expiry_quarantine_<project>.txt
```

In the outputted expiry_quarantine_<project>.txt you will find the same information as previously but also including:

- EXPIRED AT: This time it will tell you when your file was moved into quarantine. You will have 14 days from this date before it is permanently deleted.
- ID: Each file that has entered quaratine is given a unique ID, you will be this in the next step to save your file. 

## Saving Data from Quarantine:
----------------------------------------------------------------

To recover specific data from quarantine you will need 2 pieces of information:

1. ID - quarantine record to recover
2. path - where to put the data

Once you have these you can submit a request to retrive this data in the command-line:

```bash
nci-file-expiry recover ID PATH
```

Once you've requested the recovery of a file, it will go into a queue to be processed at some point in the future. You can check the status of a request
using:

```bash
usage: nci-file-expiry status [--id ID | --between TIMESTAMP TIMESTAMP | --days N]
```
For more information on these commands:  https://nci.org.au/sites/default/files/documents/2022-04/GadiSystem-GadiScratchFileExpiryCommands-200422-1629-37.pdf

## More Info:
----------------------------------------------------------------

If there is data that you need to keep long term then there are a couple of things that need to be considered. You can publish your data if you have processed a lot of raw data and it doesn't already exist on the NCI system or you can move data to the tape system for long-term storage. 

Please have a look at this blog: https://climate-cms.org/posts/2022-04-26-storage-where-what-why-how.html

Data can exist for longer on gdata than on scratch but for longer term you will need to decide on a method from the above link.