"""
Created on Tue May 22 17:16:41 2018
@author: Laila Al-Madhagi 
email: fy11lham@leeds.ac.uk 
This is a python code for peak fitting with some ideas from 
Matlab code published in: Journal of Physics: Conference Series 712 (2016) 012070  
"""

import timeit
start = timeit.default_timer()
import datetime
import os
import numpy as np
import scipy.signal
#import matplotlib 
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from collections import OrderedDict
import pandas as pd
import argparse
import sys
import socket
#import shutil

#import pillow

# functions used for fitting
# from lmfit.models import StepModel, PseudoVoigtModel, GaussianModel
from lmfit.models import GaussianModel, StepModel



# handle the input flags
description='E2: Experimental spectra peak fitting'
parser = argparse.ArgumentParser(description)


parser.add_argument('in_spectra',
    type=argparse.FileType('r'),
    help="The experimental spectra file to be read in.",
    default=sys.stdin, 
    metavar="FILE")

parser.add_argument("column_energy",  
                    type=int, 
                    help="The column in spectra file that holds the energy, 0 is the lowest value.")

parser.add_argument("column_intensity",  
                    type=int, 
                    help="The column in spectra file that holds the intensity, 0 is the lowest value.")

parser.add_argument("n_columns",  
                    type=int, 
                    help="The number of columns in spectra file.")
"""
parser.add_argument('-ft',
    '--file_type',
    default='Athena',
    choices=['Athena', 'user_defined'],
#    required=False,
    help="Select the default set of orca parameters for particular chemical states.")
"""
parser.add_argument("-offset", 
                    dest="offset",
                    type=int,
                    required=False,
                    help="The number of lines in the input spectra file that are to be skipped before the data is read in.")

parser.add_argument("-path_out",
                    dest="LE2_path_out",
                    type=str,
                    required=False,
                    help="directory where output is written")

args = parser.parse_args()

#print(args)

path_exp, file_exp = os.path.split(args.in_spectra.name)

index_of_dot = file_exp.index(".") 
filename_without_extension = file_exp[:index_of_dot]

LE2_date_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
resultsdir = r"LE2_"+filename_without_extension+r"_"+LE2_date_time
#resultsdir = r"E2_"+filename_without_extension

working_dir=os.getcwd()
path_in=working_dir

if args.n_columns -1 < args.column_energy:
    sys.exit("ERROR; There are not enough colums in the data for the energy column to exist.")
    
if args.n_columns -1 < args.column_intensity:
    sys.exit("ERROR; There are not enough colums in the data for the intensity column to exist.")

if args.offset is not None:
    skip = int(args.offset)
if args.offset is None:
    sys.exit("ERROR; User defined files need to have an offset value provided.")
        
if args.LE2_path_out is not None:
    path_out=args.LE2_path_out+r'//'+resultsdir
if args.LE2_path_out is None:
    path_out=path_exp+r'//'+resultsdir


os.makedirs(path_out)
log_file_name = path_out+r"//log.txt"
log_file=open(log_file_name, "w") 



log_file.write(description+"\n\n")
#host=socket.gethostbyaddr(socket.gethostname())[0]
#log_file.write(r"This program ran at "+LE2_date_time+r" on the "+host+r" host system.")
log_file.write(r"This program ran at "+LE2_date_time+r" on the host system.")
log_file.write("\n\n")

print(description)
print("\n~ Experimental spectra file details: {}".format(args.in_spectra))
log_file.write("\n\n~ Experimental spectra file details: {}".format(args.in_spectra))

print("\n~ Column with energy values: {}".format(args.column_energy))
log_file.write("\n\n~ Column with energy values: {}".format(args.column_energy))

print("\n~ Column with intensity values: {}".format(args.column_intensity))
log_file.write("\n\n~ Column with intensity values: {}".format(args.column_intensity))

print("\n~ Number of columns: {}".format(args.n_columns))
log_file.write("\n\n~ Number of columns: {}".format(args.n_columns))
"""
print("\n~ File type of spectral file : {}".format(args.file_type))
log_file.write("\n\n~ File type of spectral file : {}".format(args.file_type))
"""

print("\n~ Offset, number of lines to skip to get to the data: {}".format(args.offset))
log_file.write("\n\n~ Offset, number of lines to skip to get to the data: {}".format(args.offset))
"""
ftype ="{}".format(args.file_type)


# the value 38 is the default number of lines to skip in the Athena file in 2018
skip = 38

if "{}".format(args.file_type) == 'Athena':
    print("You are using an Athena spectrum file.\n")
    log_file.write("\n\nYou are using an Athena spectrum file.\n")
if "{}".format(args.file_type) == 'user_defined':
    print("You are not using an Athena spectrum file, it is user defined.\n")
    log_file.write("\nYou are not using an Athena spectrum file, it is user defined.\n")
"""

log_file.flush()

edge_data_table=working_dir+r"//..//edge_data.txt"

spectra_file=path_exp+r'//'+file_exp
fitted_peak=path_out+r"//%s_fitted_peaks.txt" %filename_without_extension
peak_params=path_out+r"//%s_peak_params.txt" %filename_without_extension


edge_data=np.array([])
data=np.array([])


with open(edge_data_table,"r") as edge_data_table:
    next (edge_data_table)
    next (edge_data_table)
    for line in edge_data_table:
        line=line.split()
        edge_data=np.append(edge_data,line)
    edge_data=edge_data.reshape(int(len(edge_data)/5),5)
edge_data_table.close()

with open (spectra_file) as spectra_file:
    lines_after_heading=spectra_file.readlines()[skip:]# skip is provided through the command line
    for line in lines_after_heading:
        line=line.split()
        data=np.append(data,line)
    data=data.reshape(int(len(data)/args.n_columns),args.n_columns)# number of columns is provided through the command line 
spectra_file.close()

# xdata (energy) and ydata (intensity)
ycol=args.column_intensity
#xdata=data[:,args.column_energy].astype(float)
xdata_row=data[:,args.column_energy]
xdata=np.array([])
for x in xdata_row:
    xdata=np.append(xdata,float(x.replace(",",""))) # xdata is energy and is always the first column in Athena files in 2018
#ydata=data[:,ycol].astype(float) # ask user for the column where the intensity data, ydata as this is not always in the same place 
ydata_row=data[:,ycol]
ydata=np.array([])
for y in ydata_row:
    ydata=np.append(ydata,float(y.replace(",","")))
    
# determine e0 
dif1=np.diff(ydata)/np.diff(xdata)
e0_pos=np.where(dif1==np.nanmax(dif1[dif1!=np.inf]))[0][0]
e0=xdata[e0_pos]
e_edge=abs(edge_data[:,4].astype(float)-e0)
e1_pos=np.where(e_edge==min(e_edge))[0][0]
element=edge_data[e1_pos][0]

# determine fitting range
fit_range=[5,8]
fit_pos_i_ls=abs(xdata-e0+fit_range[0])
fit_pos_i=np.where(fit_pos_i_ls==min(fit_pos_i_ls))[0][0]
fit_pos_f_ls=abs(xdata-e0-fit_range[1])
fit_pos_f=np.where(fit_pos_f_ls==min(fit_pos_f_ls))[0][0]
fit_xdata=xdata[fit_pos_i:fit_pos_f].astype(float)
fit_ydata=ydata[fit_pos_i:fit_pos_f].astype(float)

# determination of number of gaussian and their initial position guesses + fitting
dif2=np.diff(fit_ydata)/np.diff(fit_xdata)
e0_pos2=np.where(dif2==max(dif2))[0][0]
posit=np.array((np.where((dif2[1:]<0)*(dif2[0:-1]>0))),dtype='int')+1
posit=np.unique(np.sort(np.append(posit,np.array((np.where((dif2[1:]>0)*(dif2[0:-1]<0))),dtype='int'))))
posit=posit[posit>e0_pos2]
funccenter=fit_xdata[posit]
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
## First fitting attempt 
gaussnum=len(funccenter)
funcnum=gaussnum
# initial guess x0F, lower bound lb, upper bound up
x0f=np.zeros((funcnum,4))
lb=np.zeros((funcnum,4))
ub=np.zeros((funcnum,4))
# initial guess for error function
step1=StepModel(form='arctan', prefix='step1_')
# pars.update(step2.guess(y,x=x))
pars=step1.make_params()
pars['step1_center'].set(e0+6, min=e0+3, max=e0+8)
pars['step1_amplitude'].set(0.5, min=0.1, max=1)
pars['step1_sigma'].set(0.5, min=0.3, max=0.8)
mod=step1
# initial guess for gaussian
x0f [:funcnum,2]=funccenter[:]
for n0 in range (0,funcnum):
    x0f[n0,0:2]=[0.5,0.5]
    lb[n0,:]=[0.2,0.2,x0f[n0,2]-1,0]
    ub[n0,:]=[3,0.7,x0f[n0,2]+1,0.1]
    gauss=GaussianModel(prefix='g%s_'%int(n0+1))
    pars.update(gauss.make_params())
    pars['g%s_amplitude'%int(n0+1)].set(x0f[n0][0], min=lb[n0][0],max=ub[n0][0])
    pars['g%s_sigma'%int(n0+1)].set(x0f[n0][1], min=lb[n0][1],max=ub[n0][1])
    pars['g%s_center'%int(n0+1)].set(x0f[n0][2], min=lb[n0][2],max=ub[n0][2])
    mod+=gauss  
# fitting the functions
init = mod.eval(pars, x=fit_xdata)
out = mod.fit(fit_ydata, pars, x=fit_xdata)
Y_fitted=out.best_fit
R_sqr=1 - out.residual.var() / np.var(fit_ydata)
# reading fitted peaks parameters from first fitting attempt
v=[]
for param in out.params.values():
    v.append("%s:  %f" % (param.name, param.value))
    #param_values.append("%s:  %f +/- %f (init = %f)" % (param.name, param.value, param.stderr, param.init_value))
param_keywords=["amplitude","sigma","center","fwhm","height"]
param_values=[]
for m in param_keywords:
    for item in v:
        if m in item:
            param_values.append(item.split(":"))
function_keywords=["step"]
d=OrderedDict([("step",[])])
for i in range(1,funcnum+1):
    function_keywords.append("g%s"%i)
    d["g%s"%i]=[]
for n in function_keywords:
    for c in range (0,len(param_values)):
        if n == param_values[c][0].split('_')[0]:
            d[n].append(param_values[c][1])
        c+=1
funccenter_new=np.array([])
func_diff=[]
for n in range(1,gaussnum):
    func_diff.append(abs(float(d['g%s'%str(n+1)][2])-float(d['g%s'%str(n)][2])))
    if abs(float(d['g%s'%str(n+1)][2])-float(d['g%s'%str(n)][2])) >0.5:
        #funccenter_new=np.append(funccenter_new,float(d['g%s'%str(n+1)][2]))
        funccenter_new=np.append(funccenter_new,float(d['g%s'%str(n)][2]))
        funccenter_new=np.unique(np.sort(funccenter_new))
if any(t<0.5 for t in func_diff):
    # second fitting attempt, after peaks with same energy position removed
    gaussnum=len(funccenter_new)
    funcnum=gaussnum
    # initial guess x0F, lower bound lb, upper bound up
    x0f=np.zeros((funcnum,4))
    lb=np.zeros((funcnum,4))
    ub=np.zeros((funcnum,4))
    #initial guess for error function
    step1=StepModel(form='arctan', prefix='step1_')
    # pars.update(step2.guess(y,x=x))
    pars=step1.make_params()
    pars['step1_center'].set(e0+4, min=e0+3, max=e0+6)
    pars['step1_amplitude'].set(0.5, min=0.1, max=1)
    pars['step1_sigma'].set(0.5, min=0.3, max=0.8)
    mod=step1
    # initial guess for gaussian
    x0f [:funcnum,2]=funccenter_new[:]
    for n0 in range (0,funcnum):
        x0f[n0,0:2]=[0.5,0.5]
        lb[n0,:]=[0.2,0.2,x0f[n0,2]-1,0]
        ub[n0,:]=[3,0.7,x0f[n0,2]+1,0.1]
        gauss=GaussianModel(prefix='g%s_'%int(n0+1))
        pars.update(gauss.make_params())
        pars['g%s_amplitude'%int(n0+1)].set(x0f[n0][0], min=lb[n0][0],max=ub[n0][0])
        pars['g%s_sigma'%int(n0+1)].set(x0f[n0][1], min=lb[n0][1],max=ub[n0][1])
        pars['g%s_center'%int(n0+1)].set(x0f[n0][2], min=lb[n0][2],max=ub[n0][2])
        mod+=gauss          
    # fitting the functions
    init = mod.eval(pars, x=fit_xdata)
    out = mod.fit(fit_ydata, pars, x=fit_xdata)
    Y_fitted=out.best_fit
    R_sqr=1 - out.residual.var() / np.var(fit_ydata)


# determination of number of gaussian and their initial position guesses + fitting using smooth Y-data
smooth_ydata=scipy.signal.savgol_filter(fit_ydata,11,2)
dif2_smooth=np.diff(smooth_ydata)/np.diff(fit_xdata)
e0_pos2_smooth=np.where(dif2_smooth==max(dif2_smooth))[0][0]
posit_smooth=np.array((np.where((dif2_smooth[1:]<0)*(dif2_smooth[0:-1]>0))),dtype='int')+1
posit_smooth=np.unique(np.sort(np.append(posit_smooth,np.array((np.where((dif2_smooth[1:]>0)*(dif2_smooth[0:-1]<0))),dtype='int'))))
posit_smooth=posit_smooth[posit_smooth>e0_pos2_smooth]
funccenter_smooth=fit_xdata[posit_smooth]
# remove extraneous peaks
b_smooth=[]
b_new_smooth=[]
for i in range(0,len(funccenter_smooth)-1):
    if funccenter_smooth[i+1]-funccenter_smooth[i]>0.5:
        b_smooth.append(i)
        b_smooth.append(i+1)
for j in b_smooth:
    if j not in b_new_smooth:
        b_new_smooth.append(j)
funccenter_smooth=funccenter_smooth[b_new_smooth]
## First fitting attempt 
gaussnum_smooth=len(funccenter_smooth)
funcnum_smooth=gaussnum_smooth
# initial guess x0F, lower bound lb, upper bound up
x0f_smooth=np.zeros((funcnum_smooth,4))
lb_smooth=np.zeros((funcnum_smooth,4))
ub_smooth=np.zeros((funcnum_smooth,4))
# initial guess for error function
step1_smooth=StepModel(form='arctan', prefix='step1_')
# pars.update(step2.guess(y,x=x))
pars_smooth=step1_smooth.make_params()
pars_smooth['step1_center'].set(e0+6, min=e0+3, max=e0+8)
pars_smooth['step1_amplitude'].set(0.5, min=0.1, max=1)
pars_smooth['step1_sigma'].set(0.5, min=0.3, max=0.8)
mod_smooth=step1_smooth

# initial guess for gaussian
x0f_smooth [:funcnum_smooth,2]=funccenter_smooth[:]
for n0 in range (0,funcnum_smooth):
    x0f_smooth[n0,0:2]=[0.5,0.5]
    lb_smooth[n0,:]=[0.2,0.2,x0f_smooth[n0,2]-1,0]
    ub_smooth[n0,:]=[3,0.7,x0f_smooth[n0,2]+1,0.1]
    gauss_smooth=GaussianModel(prefix='g%s_'%int(n0+1))
    pars_smooth.update(gauss_smooth.make_params())
    pars_smooth['g%s_amplitude'%int(n0+1)].set(x0f_smooth[n0][0], min=lb_smooth[n0][0],max=ub_smooth[n0][0])
    pars_smooth['g%s_sigma'%int(n0+1)].set(x0f_smooth[n0][1], min=lb_smooth[n0][1],max=ub_smooth[n0][1])
    pars_smooth['g%s_center'%int(n0+1)].set(x0f_smooth[n0][2], min=lb_smooth[n0][2],max=ub_smooth[n0][2])
    mod_smooth+=gauss_smooth  
        
# fitting the functions
init_smooth = mod_smooth.eval(pars_smooth, x=fit_xdata)
out_smooth = mod_smooth.fit(fit_ydata, pars_smooth, x=fit_xdata)
Y_fitted_smooth=out_smooth.best_fit
R_sqr_smooth=1 - out_smooth.residual.var() / np.var(fit_ydata)
# reading fitted peaks parameters from first fitting attempt
v_smooth=[]
for param_smooth in out_smooth.params.values():
    v_smooth.append("%s:  %f" % (param_smooth.name, param_smooth.value))
    #param_values.append("%s:  %f +/- %f (init = %f)" % (param.name, param.value, param.stderr, param.init_value))
param_keywords=["amplitude","sigma","center","fwhm","height"]
param_values_smooth=[]
for m in param_keywords:
    for item in v_smooth:
        if m in item:
            param_values_smooth.append(item.split(":"))
function_keywords=["step"]
d_smooth=OrderedDict([("step",[])])
for i in range(1,funcnum_smooth+1):
    function_keywords.append("g%s"%i)
    d_smooth["g%s"%i]=[]
for n in function_keywords:
    for c in range (0,len(param_values_smooth)):
        if n == param_values_smooth[c][0].split('_')[0]:
            d_smooth[n].append(param_values_smooth[c][1])
        c+=1
funccenter_new_smooth=np.array([])
func_diff_smooth=[]
for n in range(1,gaussnum_smooth):
    func_diff_smooth.append(abs(float(d_smooth['g%s'%str(n+1)][2])-float(d_smooth['g%s'%str(n)][2])))
    if abs(float(d_smooth['g%s'%str(n+1)][2])-float(d_smooth['g%s'%str(n)][2])) >0.5:
        #funccenter_new_smooth=np.append(funccenter_new_smooth,float(d['g%s'%str(n+1)][2]))
        funccenter_new_smooth=np.append(funccenter_new_smooth,float(d_smooth['g%s'%str(n)][2]))
        funccenter_new_smooth=np.unique(np.sort(funccenter_new_smooth))
        
if any(t<0.5 for t in func_diff_smooth):
    # second fitting attempt, after peaks with same energy position removed
    gaussnum_smooth=len(funccenter_new_smooth)
    funcnum_smooth=gaussnum_smooth
    # initial guess x0F, lower bound lb, upper bound up
    x0f_smooth=np.zeros((funcnum_smooth,4))
    lb_smooth=np.zeros((funcnum_smooth,4))
    ub_smooth=np.zeros((funcnum_smooth,4))
    #initial guess for error function
    step1_smooth=StepModel(form='arctan', prefix='step1_')
    # pars.update(step2.guess(y,x=x))
    pars_smooth=step1_smooth.make_params()
    pars_smooth['step1_center'].set(e0+4, min=e0+3, max=e0+6)
    pars_smooth['step1_amplitude'].set(0.5, min=0.1, max=1)
    pars_smooth['step1_sigma'].set(0.5, min=0.3, max=0.8)
    mod_smooth=step1_smooth
    # initial guess for gaussian
    x0f_smooth [:funcnum_smooth,2]=funccenter_new_smooth[:]
    for n0 in range (0,funcnum_smooth):
        x0f_smooth[n0,0:2]=[0.5,0.5]
        lb_smooth[n0,:]=[0.2,0.2,x0f_smooth[n0,2]-1,0]
        ub_smooth[n0,:]=[3,0.7,x0f_smooth[n0,2]+1,0.1]
        gauss_smooth=GaussianModel(prefix='g%s_'%int(n0+1))
        pars_smooth.update(gauss_smooth.make_params())
        pars_smooth['g%s_amplitude'%int(n0+1)].set(x0f_smooth[n0][0], min=lb_smooth[n0][0],max=ub_smooth[n0][0])
        pars_smooth['g%s_sigma'%int(n0+1)].set(x0f_smooth[n0][1], min=lb_smooth[n0][1],max=ub_smooth[n0][1])
        pars_smooth['g%s_center'%int(n0+1)].set(x0f_smooth[n0][2], min=lb_smooth[n0][2],max=ub_smooth[n0][2])
        mod_smooth+=gauss_smooth          
    # fitting the functions
    init_smooth = mod_smooth.eval(pars_smooth, x=fit_xdata)
    out_smooth = mod_smooth.fit(fit_ydata, pars_smooth, x=fit_xdata)
    Y_fitted_smooth=out_smooth.best_fit
    R_sqr_smooth=1 - out_smooth.residual.var() / np.var(fit_ydata)

if R_sqr_smooth>R_sqr:
    # reading fitted peaks parameters from second fitting attempt
    v_smooth=[]
    for param_smooth in out_smooth.params.values():
        v_smooth.append("%s:  %f" % (param_smooth.name, param_smooth.value))
        #param_values.append("%s:  %f +/- %f (init = %f)" % (param.name, param.value, param.stderr, param.init_value))
    param_keywords=["amplitude","sigma","center","fwhm","height"]
    param_values_smooth=[]
    for m in param_keywords:
        for item in v_smooth:
            if m in item:
                param_values_smooth.append(item.split(":"))
    function_keywords=["step"]
    d_smooth=OrderedDict([("step",[])])
    for i in range(1,funcnum_smooth+1):
        function_keywords.append("g%s"%i)
        d_smooth["g%s"%i]=[]
    for n in function_keywords:
        for c in range (0,len(param_values_smooth)):
            if n in param_values_smooth[c][0]:
                d_smooth[n].append(param_values_smooth[c][1])
            c+=1
    #plot results
    fig=plt.figure(num=None, figsize=(10, 8), dpi=600, facecolor='w', edgecolor='k') 
    plot_components = True
    
    plt.plot(xdata, ydata, 'b',label='Experimental Data')
    #plt.plot(fit_xdata, init, 'k--') #plot with initial guess
    plt.plot(fit_xdata, out_smooth.best_fit, 'r-', label='Fitted data')
    
    if plot_components:
        comps = out_smooth.eval_components(x=fit_xdata)
        plt.plot(fit_xdata,comps['step1_'], 'k--',label='Step Function')
        for x in range (1,gaussnum_smooth+1):
            plt.plot(fit_xdata, comps['g%s_'%x], 'k--',label='Gaussian%s Function'%x)
    plt.legend(loc='upper left')
    ax = plt.gca()
    ax.set_xlim([fit_xdata[0],fit_xdata[-1]+1])
    ax.set_ylim([0,max(fit_ydata)+0.5])
    plt.xlabel('Energy/ eV')
    plt.ylabel('Intensity')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.show()
    fig_filename = path_out+"//%s_fitted_peaks.png"%filename_without_extension
    fig.savefig(fig_filename,bbox_inches='tight')
    
    
    print("Goodness of fit (R-squared) is: %s" %R_sqr_smooth)
    
    log_file.write("\nGoodness of fit (R-sqaured) is: %s" %R_sqr_smooth)
    
    log_file.flush()
    
    # write fitted peaks to output file 
    fitted_peaks=pd.concat([pd.DataFrame({'energy': fit_xdata}), pd.DataFrame(comps)], axis=1)
    fitted_peaks.to_csv(fitted_peak, index=False, sep='\t', header=True)
    
    # Write fitted params to output file 
    fitted_peaks_param=pd.concat([pd.DataFrame({'parameter': param_keywords}),pd.DataFrame(dict([(k,pd.Series(v)) for k,v in d_smooth.items()]))], 
axis=1)
    fitted_peaks_param.to_csv(peak_params,index=False, sep='\t', header=True)
    
    
    stop = timeit.default_timer()
    running_time=(stop-start)/60
    print ("\nRunning time is: "+ str(round(running_time,3)) + "minutes") 
    
    log_file.write("\n\nEND:\nRunning time is: "+ str(round(running_time,3)) + " minutes")
    
    log_file.close()
else:
    # reading fitted peaks parameters from second fitting attempt
    v=[]
    for param in out.params.values():
        v.append("%s:  %f" % (param.name, param.value))
        #param_values.append("%s:  %f +/- %f (init = %f)" % (param.name, param.value, param.stderr, param.init_value))
    param_keywords=["amplitude","sigma","center","fwhm","height"]
    param_values=[]
    for m in param_keywords:
        for item in v:
            if m in item:
                param_values.append(item.split(":"))
    function_keywords=["step"]
    d=OrderedDict([("step",[])])
    for i in range(1,funcnum+1):
        function_keywords.append("g%s"%i)
        d["g%s"%i]=[]
    for n in function_keywords:
        for c in range (0,len(param_values)):
            if n in param_values[c][0]:
                d[n].append(param_values[c][1])
            c+=1
    #plot results
    fig=plt.figure(num=None, figsize=(10, 8), dpi=600, facecolor='w', edgecolor='k') 
    plot_components = True
    
    plt.plot(xdata, ydata, 'b',label='Experimental Data')
    #plt.plot(fit_xdata, init, 'k--') #plot with initial guess
    plt.plot(fit_xdata, out.best_fit, 'r-', label='Fitted data')
    
    if plot_components:
        comps = out.eval_components(x=fit_xdata)
        plt.plot(fit_xdata,comps['step1_'], 'k--',label='Step Function')
        for x in range (1,gaussnum+1):
            plt.plot(fit_xdata, comps['g%s_'%x], 'k--',label='Gaussian%s Function'%x)
    plt.legend(loc='upper left')
    ax = plt.gca()
    ax.set_xlim([fit_xdata[0],fit_xdata[-1]+1])
    ax.set_ylim([0,max(fit_ydata)+0.5])
    plt.xlabel('Energy/ eV')
    plt.ylabel('Intensity')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.show()
    fig_filename = path_out+"//%s_fitted_peaks.png"%filename_without_extension
    fig.savefig(fig_filename,bbox_inches='tight')
    
    
    print("Goodness of fit (R-sqaured) is: %s" %R_sqr)
    
    log_file.write("\nGoodness of fit (R-sqaured) is: %s" %R_sqr)
    
    log_file.flush()
    
    # write fitted peaks to output file 
    fitted_peaks=pd.concat([pd.DataFrame({'energy': fit_xdata}), pd.DataFrame(comps)], axis=1)
    fitted_peaks.to_csv(fitted_peak, index=False, sep='\t', header=True)
    

    # Write fitted params to output file 
    fitted_peaks_param=pd.concat([pd.DataFrame({'parameter': param_keywords}),pd.DataFrame(dict([(k,pd.Series(v)) for k,v in d.items()]))], axis=1)
    fitted_peaks_param.to_csv(peak_params,index=False, sep='\t', header=True)
    
    
    stop = timeit.default_timer()
    running_time=(stop-start)/60
    print ("\nRunning time is: "+ str(round(running_time,3)) + "minutes") 
    log_file.write("\n\nEND:\nRunning time is: "+ str(round(running_time,3)) + " minutes")
    log_file.close()
    
    print("\nLE2 outputs are in \n%s"%path_out)