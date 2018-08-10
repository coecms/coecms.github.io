---
title: Fortran Debugging Video Series
author: Holger Wolff
layout: post
excerpt: >-
    Presentation of Fortran Debugging Video Series
---

Last year we have given a Fortran Debugging Session during a workshop.

Some people were unable to attend, and asked whether there would be a repeat.

While we are not currently planning to do that, the idea was hatched to create a YouTube Video Series on Fortran Debugging, as there are preciously few resources out there.

## Episode 1: Terminology

The first episode focuses on the understanding of what the term 'bug' actually means.

It presents a distinction, originally proposed in Andreas Zeller's book [Why Programs Fail](http://www.whyprogramsfail.com/book.php) between different aspects of a bug:

* The **Defect** being the actual error in the instructions that make up the program,
* the **Infection** being the abnormal state of the program as the possible result of a Defect, and
* the **Failure**, being the observed effect of the infection.

[![Full Video](https://img.youtube.com/vi/8qw0hXNNRFk/0.jpg)](https://www.youtube.com/watch?v=8qw0hXNNRFk)

## Episode 2: Stack Trace

The second episode highlights the output a program often leaves after a crash: The Stack Trace.

It explains what a Stack Trace is, how to add information to the Stack Trace, and how to interpret it.

[![Full Video](https://img.youtube.com/vi/-JhgdVJqOhI/0.jpg)](https://www.youtube.com/watch?v=-JhgdVJqOhI)

## Episode 3: Run Time Checks

The third episode explains how to add self-checks to the program.

Those so-called Run Time Checks monitor the health of the program and can warn much earlier if an infection occurred.

Very useful during Debugging, they have major drawbacks during normal operation, so you don't want to keep them in once your program runs fine again.

How to use the Pre-Processor to quickly enable and disable run time checks is part of the Video.

[![Full Video](https://img.youtube.com/vi/WkpDFlytOqw/0.jpg)](https://www.youtube.com/watch?v=WkpDFlytOqw)
