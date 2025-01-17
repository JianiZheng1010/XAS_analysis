XAS_analysis: E2 code

GENERAL INFORMATION ON THIS PROJECT
This is created by Laila Al-Madhagi (fy11lham@leeds.ac.uk) for her PhD project on the 2018/05/23. Joanna Leng (j.leng@leeds.ac.uk) from the University of Leeds contributed to the development. The code license should be CC-BY-NC. GitHub does not support this license type and it will be added later. 

This program was developed with Python 3.5.2 with modules: numpy(version 1.13.1), scipy(version 0.19.1), matplotlib(version 2.0.2) and lmfit(version 0.9.10).It was developed on a windows system using Anaconda

to install lmfit, follow the instructions on this web page:

https://anaconda.org/conda-forge/lmfit 


FILES INCLUDED

1,) README.md					This currently holds all the documentation for
								this repository

2,)E2.py						Python source code for peak fitting 
								
3,)N1s_Imidazole_ISEELS.txt 	A text file containing experimental nitrogen K-edge data of imidazole in the gas phase. The file is used for testing and development 
								(data published in Apen et al, J. Phys. Chem. 1993, 97, 6859-6866 and available from:Gas Phase Core Excitation Database: http://unicorn.mcmaster.ca/corex/name-list.html
								
4,)template.html				The html template for the report that lists the most important outputs from E2.
	
INFORMATION ON THE E2 (EXPERIMENTAL PEAK FITTING) CODE	

usage:  


E2.py [-h] [-offset OFFSET] [-path_out] FILE column_energy column_intensity n_columns

											 
E2: Experimental spectra peak fitting
											 									 
positional arguments:

  FILE                  The experimental spectra file to be read in;
                        filename must include its path and it is best not to be in the directory structure for this code
  
  column_energy         The column in spectra file that holds the energy, 0 is
                        the lowest value.
						
  column_intensity      The column in spectra file that holds the intensity, 0
                        is the lowest value.
						
  n_columns             The number of columns in spectra file.

  
optional arguments:

  -h, --help            show this help message and exit
  
						
  -offset OFFSET        The number of lines in the input spectra file that are
                        to be skipped before the data is read in.
  
  -path_out				The directory where the results directory will be written
  
EXAMPLE USAGE

1, minimal needed to run (defaults assume it is a gas):

E2.py  C:\Users\userid\Desktop\data\Imidazole\N1s_Imidazole_ISEELS.txt 0 2 6 -offset 38

BACKGROUND

This program is the E2 part of the experimental pipeline or workflow, which is described in the README file in the top level directory for the project.
