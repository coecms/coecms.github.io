---
title: Climatologies with 'coarsen'
layout: notebook
notebook: 2021-07-29-coarsen_climatology.html
excerpt: >-
    A reasonably recent addition to Xarray is the 'coarsen' function, which allows you to resample a DataArray at a regular frequency. For well-behaved datasets this provides some interesting opportunities for optimisation, getting around the inefficiencies of 'groupby' from needing to work with arbitrary time spacings.
tags: xarray climatology
---
