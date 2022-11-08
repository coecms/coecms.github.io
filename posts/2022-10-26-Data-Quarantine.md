# Data Quarantine

Your data in /scratch/ can be deleted if it haven't been accessed/modified for a certain length of time. NCI introduced this in May 2022 to try and help prevent the build-up of unused data. 

 
 
 
Files older than 100 days are moved from project directories on /scratch into a quarantine space. See these websites for info:

http://climate-cms.wikis.unsw.edu.au/Scratch_file_expiry

https://opus.nci.org.au/pages/viewpage.action?pageId=156434436


After 14 days in quarantine, the data is then permanently deleted. You can run 

```bash
“nci-file-expiry list-warnings -p <project> > expiry_warning_<project>.txt”
```

to list all of your data in a specific project (k10 in your case) and see what data is at risk of being moved to quarantine or deleted. 

If you need to recover any of your data from quarantine please follow the steps here: https://nci.org.au/sites/default/files/documents/2022-04/GadiSystem-GadiScratchFileExpiryCommands-200422-1629-37.pdf

If there is data that you need to keep long term then there are a couple of things that need to be considered. You can publish your data if you have processed a lot of raw data and it doesn't already exist on the NCI system. You can move data to the tape system for long-term storage. 

Please have a look at this blog: https://climate-cms.org/posts/2022-04-26-storage-where-what-why-how.html

Data can exist for longer on gdata than on scratch but for longer term you will need to decide on a method from the above link.