# -*- coding: utf-8 -*-
"""
Created on Tue May 22 17:16:41 2018
@author: Laila Al-Madhagi 
email: fy11lham@leeds.ac.uk 
This is a python code for peak fitting with some ideas from 
Matlab code published in: Journal of Physics: Conference Series 712 (2016) 012070  
"""
import timeit
start = timeit.default_timer()
import os
import numpy as np
import subprocess as sp
import matplotlib.pyplot as plt
#import scipy.signal
import datetime
import argparse
import sys
import socket


# handle the input flags
description='C1: Compares experimental spectra with theorectically calculated data.'
parser = argparse.ArgumentParser(description)

parser.add_argument('in_experiment_file',
    type=argparse.FileType('r'),
    help="Experimental spectra datafile to be read in.",
    default=sys.stdin, metavar="FILE")

parser.add_argument('in_theoretical_file',
    type=argparse.FileType('r'),
    help="Theoretically calulated spectra datafile to be read in.",
    default=sys.stdin, metavar="FILE")

parser.add_argument('in_fitted_peaks_file',
    type=argparse.FileType('r'),
    help="Peaks fitted to the experimental spectra datafile to be read in.",
    default=sys.stdin, metavar="FILE")

'''parser.add_argument('in_edge_data_file',
    type=argparse.FileType('r'),
    help="Edge data from experimental spectra datafile to be read in.",
    default=sys.stdin, metavar="FILE")'''


args = parser.parse_args()


file_exp_read=args.in_experiment_file.name

path, file_exp = os.path.split(file_exp_read)
                   
index_of_dot = file_exp.index(".") 
file_exp_without_extension = file_exp[:index_of_dot]

date_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
resultsdir = r"C1_"+file_exp_without_extension+r"_"+date_time


path_in=path
path_out=path+r"\\"+resultsdir
os.makedirs(path_out)

log_file_name = path_out+r"\\log.txt"
log_file=open(log_file_name, "w") 

log_file.write(description+"\n\n")
host=socket.gethostbyaddr(socket.gethostname())[0]
log_file.write(r"This program ran at "+date_time+r" on the "+host+r" host system.")
log_file.write("\n\n")

html_line1 =r"This program ran at "+date_time+r" on the "+host+r" host system"




print("\n~ Experimental spectra file details: {}".format(args.in_experiment_file))
log_file.write("\n\n~ Experimental spectra file details: {}".format(args.in_experiment_file))


print("\n~ Theoretical spectra file details: {}".format(args.in_theoretical_file))
log_file.write("\n\n~ Theoretical spectra file details: {}".format(args.in_theoretical_file))


print("\n~ Peaks fitted to the theoretical spectra file details: {}".format(args.in_fitted_peaks_file))
log_file.write("\n\n~ Peaks fitted to the theoretical spectra file details: {}".format(args.in_fitted_peaks_file))




#input and output files 
working_dir=os.getcwd()


#exp_data_file=path_in+r"\%s" %exp_data_filename 
exp_data_file=args.in_experiment_file.name
#edge_data_table=path_in+r"\edge_data.txt"
#edge_data_table=args.in_edge_data_file.name
edge_data_table=working_dir+r"\..\edge_data.txt"
#fitted_peaks_param=path_in+r"\%s" %fitted_peaks_param_filename
fitted_peaks_param=args.in_fitted_peaks_file.name
#theory_data_file=path_in+r"\%s.abs.dat" %theory_data_filename
file_theory_read=args.in_theoretical_file.name
path_theory, file_theory = os.path.split(file_theory_read)
theory_data_file=path_in+"\%s.abs.dat" %file_theory
theory_data_filename=r"TDDFT_N-edge.out"
tddft_output_file=path_in+r"\%s" %theory_data_filename

html_infile_name=working_dir+r"\template.html"
html_outfile_name=path_out+r"\report.html"



        
        



print("theory_data_file: ",theory_data_file)

###Extract Experimental data
#put experimental data into array
exp_data=np.array([])
with open (exp_data_file) as exp_data_file:
    lines_after_heading=exp_data_file.readlines()[38:]# 38 is default but it can change 
    for line in lines_after_heading:
        line=line.split()
        exp_data=np.append(exp_data,line)
    exp_data=exp_data.reshape(int(len(exp_data)/6),6)#6 is the number of columns and it can change 
exp_data_file.close()
#xdata and ydata
exp_ycol=2
exp_xdata=exp_data[:,0].astype(float) #xdata is always the first column
exp_ydata=exp_data[:,exp_ycol].astype(float) # ask user for the column where the ydata is 
norm_exp_ydata=(exp_ydata-min(exp_ydata))/(max(exp_ydata)-min(exp_ydata))

#put edge data into array
edge_data=np.array([])
with open(edge_data_table,"r") as edge_data_table:
    next (edge_data_table)
    next (edge_data_table)
    for line in edge_data_table:
        line=line.split()
        edge_data=np.append(edge_data,line)
    edge_data=edge_data.reshape(int(len(edge_data)/5),5)
    edge_data_table.close()
##determine fitting range to be used when plotting 
#determine e0 requried for fitting range
dif1=np.diff(exp_ydata)/np.diff(exp_xdata)
e0_pos=np.where(dif1==max(dif1))[0][0]
e0=exp_xdata[e0_pos]
e_edge=abs(edge_data[:,4].astype(float)-e0)
e1_pos=np.where(e_edge==min(e_edge))[0][0]
element=edge_data[e1_pos][0]
#determine fitting range
fit_range=[5,5]
fit_pos_i_ls=abs(exp_xdata-e0+fit_range[0])
fit_pos_i=np.where(fit_pos_i_ls==min(fit_pos_i_ls))[0][0]
fit_pos_f_ls=abs(exp_xdata-e0-fit_range[1])
fit_pos_f=np.where(fit_pos_f_ls==min(fit_pos_f_ls))[0][0]
fit_exp_xdata=exp_xdata[fit_pos_i:fit_pos_f].astype(float)
fit_exp_ydata=norm_exp_ydata[fit_pos_i:fit_pos_f].astype(float)

#read fitted peaks parameter 
peak_param=[]
with open(fitted_peaks_param) as fit_param:
    for line in fit_param:
       line=line.split()
       peak_param.append(line)
    fit_param.close()

for element in peak_param:
    if "center" in element:
        first_exp_peak_center=min(element)
###

###Extract theoretical data
#run tddft calc
p=sp.Popen(['orca_mapspc',tddft_output_file,'ABS','-eV','-x0%s'%str(int(min(fit_exp_xdata)-15)),'-x1%s'%str(int(max(fit_exp_xdata))),'-n500','-w0.6'])
p_status=p.wait()

#read orbital energy information from ouput file
#might not this information now
""" 
orbital_energies_array=np.array([])
with open(theory_data_file, 'r+') as tddft_output_file:
    copy=False
    for line in tddft_output_file:
        if line.strip()=="ORBITAL ENERGIES":
            copy=True
        elif line.strip()=="MOLECULAR ORBITALS":
            copy=False
        elif copy:
            line=line.split()
            if len(line)==4:
                orbital_energies_array=np.append(orbital_energies_array,line)
    orbital_energies_array=orbital_energies_array.reshape(int(len(orbital_energies_array)/4),4)
    orbital_energies_array=np.delete(orbital_energies_array, np.s_[0:int(len(orbital_energies_array)/2)],0)             
    unocc_orbitals=[]
    for x in range (0, int(len(orbital_energies_array)-1)):
        if orbital_energies_array[x][1]==np.str("0.0000"):
            unocc_orbitals.append(x)
        x+=1
    orbital_energies_array=np.delete(orbital_energies_array, np.s_[unocc_orbitals[0]:],0)
    tddft_output_file.close()
"""
#extract Loewdin orbital population analysis information and excited states information
Loewdin_lines=[]
states_lines=[]
with open (tddft_output_file, "r") as tddft_output_file:
    copy=False
    for line in tddft_output_file:
        if "LOEWDIN REDUCED ORBITAL POPULATIONS PER" in line.strip():
            copy=True
        elif "MAYER POPULATION ANALYSIS" in line.strip():
            copy=False
        elif copy:
            line=line.split()
            Loewdin_lines.append(line)
    tddft_output_file.seek(0)
    copy=False
    for line in tddft_output_file:
        if "EXCITED STATES" in line.strip():
            copy=True
        elif "EXCITATION SPECTRA" in line.strip():
            copy=False
        elif copy:
            line=line.split()
            states_lines.append(line)
    
    tddft_output_file.close()
#Function to split read lines into blocks
#The function was adapted from here https://codereview.stackexchange.com/questions/179530/
#split-list-of-integers-at-certain-value-efficiently
def block_split(seq,condition):
    group=[]
    for element in seq:
        if condition not in element and element!=[]:
            group.append(element)
        elif group:
            yield group
            group = []
def states_split(seq,condition):
    group=[]
    for element in seq:
        if condition in element and element!=[]:
            group.append(element)
        elif group:
            yield group
            group = []

Loewdin_lines=Loewdin_lines[2:-3]
Loewdin_blocks=list(block_split(Loewdin_lines, []))
Loewdin_population_per=[]            
for chunk in Loewdin_blocks:
    states=chunk[0]   
    for k in chunk[4:-1]:
        for j in range(0,len(states)):
            Loewdin_population_per.append([int(states[j]),str(k[0]),str(k[1]),str(k[2]),float(k[j+3])])
            Loewdin_population_per=sorted(Loewdin_population_per)
            
states_lines=states_lines[4:-1]
states=list(states_split(states_lines,'STATE'))
states_blocks=list(block_split(states_lines, 'STATE'))
excited_states_ls=[]
for state,chunk in zip(states,states_blocks):
    for i in chunk:
        excited_states_ls.append([int(state[0][1].replace(":","")),float(state[0][5]),i[0],i[2],float(i[4])])                        

#put theoretical data into array 
theory_data=np.array([])
#with open (theory_data_file) as theory_data_file:
with open (theory_data_file) as theory_data_file:
    for line in theory_data_file:
        line=line.split()
        theory_data=np.append(theory_data,line)
    theory_data=theory_data.reshape(int(len(theory_data)/5),5)#6 is the number of columns and it can change 
theory_data_file.close()
#xdata and ydata
theory_ycol=1
theory_xdata=theory_data[:,0].astype(float) 
theory_ydata=theory_data[:,theory_ycol].astype(float) 
norm_theory_ydata=(theory_ydata-min(theory_ydata))/(max(theory_ydata)-min(theory_ydata))

##this is done to determine the center of the first peak in the theoretical spectrum
#determine fitting range
fit_range=[5,5]
fit_pos_i_ls=abs(theory_xdata-(e0-12)+fit_range[0])
fit_pos_i=np.where(fit_pos_i_ls==min(fit_pos_i_ls))[0][0]
fit_pos_f_ls=abs(theory_xdata-(e0-12)-fit_range[1])
fit_pos_f=np.where(fit_pos_f_ls==min(fit_pos_f_ls))[0][0]
fit_theory_xdata=theory_xdata[fit_pos_i:fit_pos_f].astype(float)
fit_theory_ydata=norm_theory_ydata[fit_pos_i:fit_pos_f].astype(float)
#determination of number of gaussian and their initial position guesses
#smooth_ydata=scipy.signal.savgol_filter(fit_theory_ydata,11,2)
dif2=np.diff(fit_theory_ydata)/np.diff(fit_theory_xdata)
e0_pos2=np.where(dif2==max(dif2))[0][0]
posit=np.array((np.where((dif2[1:]<0)*(dif2[0:-1]>0))),dtype='int')+1
posit=np.unique(np.sort(np.append(posit,np.array((np.where((dif2[1:]>0)*(dif2[0:-1]<0))),dtype='int')+1)))
posit=posit[posit>e0_pos2]
funccenter=fit_theory_xdata[posit]
#remove extraneous peaks
b=[]
b_new=[]
for i in range(0,len(funccenter)-1):
    if funccenter[i+1]-funccenter[i]>0.5:
        b.append(i)
        b.append(i+1)
for j in b:
    if j not in b_new:
        b_new.append(j)
funccenter=funccenter[b_new]
#translate the energy scale for the theoretical data based on experimental data
trans_theory_xdata=theory_xdata+(float(first_exp_peak_center)-min(funccenter))
transform=float(first_exp_peak_center)-min(funccenter)
html_transform="%.3f" % transform

###Peak fitting
peak_assignment_ls=[]
for element in excited_states_ls:
    peak_assignment_ls.append([[],element[1],element[2],[],element[3]])

###


###plotting
fig_raw=plt.figure()
plt.plot(exp_xdata, exp_ydata, 'b',label='Experimental Spectrum')
plt.plot(theory_xdata, theory_ydata, 'g--',label='Theoretical Spectrum')
plt.legend(loc='upper right')
plt.xlabel('Energy/ eV')
plt.ylabel('Intensity')
fig_raw.savefig(path_out+r'\\ComparisonOfRawExperimentalAndTheoreticalSpectra.png')

fig_norm=plt.figure()
plt.plot(exp_xdata, norm_exp_ydata, 'b',label='Experimental Spectrum')
plt.plot(theory_xdata, norm_theory_ydata, 'g--',label='Theoretical Spectrum')
plt.legend(loc='upper right')
plt.xlabel('Energy/ eV')
plt.ylabel('Intensity')
fig_norm.savefig(path_out+r'\\ComparisonOfNormalizedExperimentalAndTheoreticalSpectra.png')

fig_trans=plt.figure()
plt.plot(exp_xdata, norm_exp_ydata, 'b',label='Experimental Spectrum')
plt.plot(trans_theory_xdata, norm_theory_ydata, 'g--',label='Theoretical Spectrum')
plt.legend(loc='upper left')
ax = plt.gca()
ax.set_xlim([fit_exp_xdata[0],fit_exp_xdata[-1]+1])
ax.set_ylim([0,max(fit_exp_ydata)+0.2])
plt.xlabel('Energy/ eV')
plt.ylabel('Intensity')
fig_trans.show()
fig_trans.savefig(path_out+r'\\ComparisonOfNormalizedAndTranslatedExperimentalAndTheoreticalSpectra.png')


stop = timeit.default_timer()
running_time=(stop-start)/60
print ("Running time is: "+ str(round(running_time,3)) + "minutes") 

log_file.write("\n\nEND:\nRunning time is: "+ str(round(running_time,3)) + " minutes")

log_file.close()

html_table_row="  <tr> <td> *0* </td> <td> *1* </td>  <td> *2* </td> <td> *3* </td> <td> *4* </td> </tr>\n"

with open(html_infile_name, "r") as html_in, open(html_outfile_name, "w") as html_out:
    n=0
    for line in html_in:
        if '***' in line and n==2:
            html_out.write(line.replace("***",html_transform))            
            n+=1
        elif '***' in line and n==1:
            html_out.write(line.replace("***",html_line1))            
            n+=1
        elif '***' in line and n==0:
            html_out.write(line.replace("***",description))
            n+=1
        else:
            html_out.write(line.strip())
            
        if '+++' in line:
            for element in peak_assignment_ls:
                s0="1"
                new_line = html_table_row.replace("*0*",s0)
                s1="%.3f" % element[1]
                print(s1)
                new_line = new_line.replace("*1*",s1 )
                new_line = new_line.replace("*2*",element[2] )
                s3="3"
                new_line = new_line.replace("*3*",s3 )
                new_line = new_line.replace("*4*",element[4] )
                print("element ",element)
                print("new_line "+new_line)
                html_out.write(new_line)

            
        


