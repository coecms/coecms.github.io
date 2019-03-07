---
layout: post
title: Generating print-quality plots in R
author: Danny Eisenberg
categories: plots, R, RStudio
---
Some students have mentioned that they had generated plots with R and submitted them in their theses, but were requested to redo the plots at high resolution and to change the colour palette.

## High Resolution

If you use RStudio, you can export your plots to a file in either PDF or PNG format. If you save it in PDF format, by default it is high resoultion. If, however, you wish to save it as a PNG bitmap, the default resolution will be 72 dpi (dots per inch), the standard screen resolution, far too low for high quality printing, which needs to be at least 300 dpi.

To see what I mean, let's generate a plot as an example. We are will use a sample file recording maximum temperature available from the [UK Met Office](https://www.metoffice.gov.uk/hadobs/hadghcnd/download.html): https://www.metoffice.gov.uk/hadobs/hadghcnd/data/HadGHCND_1949-2011_TXx.nc.gz

We will now plot make a contour map displaying the average maximum temperature for the month of January:
```R
library(ncdf4)
library(maps)

# load the heatwave data file
ncname <- "HadGHCND_1949-2011_TXx_1.nc"
ncin <- nc_open(ncname)

# extract lat, lon and January Tmax variables
lats <- rev(ncvar_get(ncin, "lat"))
lons <- ncvar_get(ncin, "lon")
janVals <- ncvar_get(ncin, "January")

# set up the matrix for the contour map
area <- matrix(0,nrow=dim(lons), ncol=dim(lats))
for (lat in 1:dim(lats)){
  for (lon in 1:dim(lons)){
    vals <- janVals[lon, lat,]
    vals <- vals[!is.na(vals)]
    area[lon, lat] <- mean(vals)
  }
}

filled.contour(lons,lats,area,
                   xlim = range(lons), ylim = range(lats),
                   plot.axes = {axis(1);axis(2);
                     map('world',add=TRUE, wrap=c(-180,180), interior = FALSE)})
```

When saved in PNG format, you get this (after zooming in a bit):
![Default PNG resolution (zoomed in)]({{ "/images/heatmap_bad_bitmap.PNG" | absolute_url }})

The equivalent way to save to PNG file via the code is this:
```R
png('heatMap.png', pointsize=10, width=700, height=480)
filled.contour(lons,lats,area,
                   xlim = range(lons), ylim = range(lats),
                   plot.axes = {axis(1);axis(2);
                     map('world',add=TRUE, wrap=c(-180,180), interior = FALSE)})
dev.off()
```

Increasing the resolution can be a bit tricky.
```R
png('heatMap2.png', pointsize=10, width=700, height=480, res=300)
filled.contour(lons,lats,area,
                   xlim = range(lons), ylim = range(lats),
                   plot.axes = {axis(1);axis(2);
                     map('world',add=TRUE, wrap=c(-180,180), interior = FALSE)})
dev.off()
```
![Changed resolution to 300dpm]({{ "/images/heatmap2.PNG" | absolute_url }})
Adding the `res` parameter fixes up the resolution, but it also rescales the axes and text. Therefore, you need to increase the height and the width.

```R
png('heatmap3.png', pointsize=10, width=1400, height=960, res=300)
filled.contour(lons,lats,area,
               xlim = range(lons), ylim = range(lats),
               plot.axes = {axis(1);axis(2);
                 map('world',add=TRUE, wrap=c(-180,180), interior = FALSE)})
dev.off()
```
![Doubled width and height]({{ "/images/heatmap3.PNG" | absolute_url }})

That's better.

What if we want an even higher resolution, say 600dpi. So we change the first line to:
```R
png('C:/Users/Danny/Documents/heatmap4.png', pointsize=10, width=2800, height=2000, res=600)
```
and run the plot again.
This time you might get the following error: `Error in plot.new() : figure region too large`.

What this means is that your figure doesn't fit in the default device screen that R has set. What does that mean? Well, when you run a `png()` command, you are actually telling R to set up a PNG output device on which to display your plot. That device has certain default parameters, including dimensions and margin sizes. In this case, the plot you have specified doesn't fit in the device's spatial parameters.

You may be able to solve this problem by changing the device's margin sizes. This may require a bit of fiddling to get them right. Margin sizes are measured in units of lines of text. (A plot has a specific text size.)

By adding a `par(mar=...)` command, the error went away.
```R
png('C:/Users/Danny/Documents/heatmap5.png', pointsize=10, width=2800, height=2000, res=600)
par(mar=c(5, 4, 4, 2))
filled.contour(lons,lats,area,
               xlim = range(lons), ylim = range(lats),
               plot.axes = {axis(1);axis(2);
                 map('world',add=TRUE, wrap=c(-180,180), interior = FALSE)})
dev.off()
```

You may also get an error message saying that the margins are too big. That might indicate that:
1. You have to make them smaller, or
2. You haven't set your plot dimensions to be sufficiently large, so there isn't enough space to fit the margins.

## Changing the Colour Palette

R's default choice of colours is not to everyone's taste and those submitting theses have been known to be asked to change the colour palette.

To set the colour palette for a plot, you just have to create a vector of colour names.
```R
# create a vector with 24 shades ranging between the colours mentioned
colours = colorRampPalette(c("blue", "white", "pink", "red"))(24)
png('heatmap4.png', pointsize=10, width=1400, height=960, res=300, units="px")filled.contour(lons,lats,area, col=colours,
               xlim = range(lons), ylim = range(lats),
               plot.axes = {axis(1);axis(2);
                 map('world',add=TRUE, wrap=c(-180,180), interior = FALSE)})
dev.off()
```
![Fixed up the palette]({{ "/images/heatmap4.PNG" | absolute_url }})

For a full list of colour names in R, see [here](http://www.stat.columbia.edu/~tzheng/files/Rcolor.pdf).

There are other colour tools you can use in R, such as [RColorBrewer](https://bookdown.org/rdpeng/exdata/plotting-and-color-in-r.html#rcolorbrewer-package).

Happy plotting!
