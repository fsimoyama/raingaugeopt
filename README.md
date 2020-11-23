# raingaugeopt
These scripts can be used to optimize a rain gauge network according to the objective function of the Maximal Covering Location Problem (MCLP), as stated by Church and Revelle (1974) https://link.springer.com/article/10.1007/BF01942293

## usage

First you need to have a set of points with coordinates (X,Y) and their respective parameters a (e.g. population) and w (e.g. any other information from the point)

Script 1 (Python) generates 'n' normal or uniform distributed perturbations to the initial positions 

Script 2 (Ampl) solves the 'n' maximal covering problems in batch by using Cplex and save their solutions in 'out' files

Script 3 (Python) collects data from the out files and summarizes them in a spreadsheet
