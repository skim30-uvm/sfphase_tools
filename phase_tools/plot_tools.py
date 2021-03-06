#! /usr/bin/env python3
summary = """plot_tools.py

Description:
  Module for plot various concepts in a built dataframe with dframe_tools.py

Prerequisite:
  numpy
  pandas
  matplotlib

Optional files:
  include/notebook.mplstyle
  include/aps.mplstyle
"""

# phase_tool.py
# Sang Wook Kim
# 10.22.2021

import numpy as np
from numpy import pi as π
import math
import pandas as pd
import matplotlib.pyplot as plt
import os

if os.path.exists('include/notebook.mplstyle') and os.path.exists('include/aps.mplstyle'):
    # plot style
    plot_style = {'notebook':'include/notebook.mplstyle','aps':'include/aps.mplstyle'}
    plt.style.reload_library()
    plt.style.use(plot_style['aps'])
    figsize = plt.rcParams['figure.figsize']
    plt.rcParams['text.latex.preamble'] = f'\input{{{os.getcwd()}/include/texheader}}'

    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    print("plot style is loaded")
else:
    print("plot style don't exist")

# -----------------------------------------------------------------------------
def Σ(σ,q):
    '''Compute the Σ function needed for linear fits.'''
    return np.sum(q/σ**2)
# -----------------------------------------------------------------------------
def get_a(x,y,σ):
    '''Get the χ^2 best fit value of a0 and a1.'''

    # Get the individual Σ values
    Σy,Σx,Σx2,Σ1,Σxy = Σ(σ,y),Σ(σ,x),Σ(σ,x**2),Σ(σ,np.ones(x.size)),Σ(σ,x*y)

    # the denominator
    D = Σ1*Σx2 - Σx**2

    # compute the best fit coefficients
    a = np.array([Σy*Σx2 - Σx*Σxy,Σ1*Σxy - Σx*Σy])/D

    # Compute the error in a
    aErr = np.array([np.sqrt(Σx2/D),np.sqrt(Σ1/D)])

    return a,aErr
# -----------------------------------------------------------------------------
def linear(x,a):
    '''Return a polynomial of order'''
    return a[0] + a[1]*x
# -----------------------------------------------------------------------------
def datadic(df):
    '''Make subset dataframes for each strain value and chemical potential'''
    sliced_dict = {}

    for strain in df['strain'].unique():
        for mu in df['mu'].unique():
            subset = df[(df['strain'] == strain)&(df['mu'] == mu)]
            if subset.empty:
                continue
            subset = subset.sort_values('T', ascending=False)
            sliced_dict[str(strain)+','+str(mu)] = subset
    
    print(sliced_dict.keys())
    return sliced_dict
# -----------------------------------------------------------------------------
def esti_array(subdf):
    '''Put dataframe and return dictionary of features below'''
    '''Features list:
        'Tset': list of unique temperature values
        'totN': total number of adsorption sites based on graphene
        'n': number of particles
        'nerr': standard error of n
        'yarray': superfluid fraction
        'yerrarray': maximum error of binning error analysis
        'rhosarray': superfluid density (fraction*n/area)
        'rhoserrarray': yerrarray*n/area
    '''
    result = {}
    Tsets = sorted(list(set(subdf['T'])))
    yarray = []
    yerrarray = []
    narray = []
    nerrarray = []
    Narray = []
    for Ti in Tsets:
        sublst = subdf[subdf['T'] == Ti].sort_values('totN',ascending=False)
        yarray.append(sublst['rhos'])
        yerrarray.append(sublst['rhoserr'])
        narray.append(sublst['n'])
        nerrarray.append(sublst['nerr'])
        Narray.append(sublst['totN'])
    yarray = np.asarray(yarray)
    yerrarray = np.asarray(yerrarray)
    narray = np.asarray(narray)
    nerrarray = np.asarray(nerrarray)
    Narray = np.asarray(Narray)

    rhoarray = narray/Narray/(math.sqrt(3)/4*6*1.42)*10*6.7 # 10^15 (cm^-2) * 10^-24 (g) = 10* 10^(-10)
    rhosarray = yarray*rhoarray
    rhoserrarray = yerrarray*rhoarray
    
    result['Tset'] = Tsets
    result['totN'] = Narray
    result['n'] = narray
    result['nerr'] = nerrarray
    result['yarray'] = yarray
    result['yerrarray'] = yerrarray
    result['rhosarray'] = rhosarray
    result['rhoserrarray'] = rhoserrarray
    
    return result
# -----------------------------------------------------------------------------
def esti_array_multi(subdf):
    '''same with esti_array, but choose mean value for estimator and max value for error
    when we have more than one data row with the same configurations'''
    result = {}
    Tsets = sorted(list(set(subdf['T'])))
    yarray = []
    yerrarray = []
    narray = []
    nerrarray = []
    Narray = []
    for Ti in Tsets:
        sublst = subdf[subdf['T'] == Ti].sort_values('totN',ascending=False)
        yarray.append(sublst.groupby('totN')['rhos'].mean())
        yerrarray.append(sublst.groupby('totN')['rhoserr'].max())
        narray.append(sublst.groupby('totN')['n'].mean())
        nerrarray.append(sublst.groupby('totN')['nerr'].max())
        Narray.append(sublst.groupby('totN')['totN'].mean())
        
    yarray = np.asarray(yarray)
    yerrarray = np.asarray(yerrarray)
    narray = np.asarray(narray)
    nerrarray = np.asarray(nerrarray)
    Narray = np.asarray(Narray)

    rhoarray = narray/Narray/(math.sqrt(3)/4*6*1.42)*10*6.7 # 10^15 (cm^-2) * 10^-24 (g) = 10* 10^(-10)
    rhosarray = yarray*rhoarray
    rhoserrarray = yerrarray*rhoarray
    
    result['Tset'] = Tsets
    result['totN'] = Narray
    result['n'] = narray
    result['nerr'] = nerrarray
    result['yarray'] = yarray
    result['yerrarray'] = yerrarray
    result['rhosarray'] = rhosarray
    result['rhoserrarray'] = rhoserrarray
    
    return result
# -----------------------------------------------------------------------------
def nparallel(subdf):
    '''return number of copies with same configurations in the subset dataframes
    if the total # of data is n times total # of (T, totN) combination.
    return None if it's something else'''
    Tsets = subdf['T'].unique()
    Nsets = subdf['totN'].unique()
    intg = len(subdf)/(len(Tsets)*len(Nsets))
#     return intg
    if intg.is_integer():
        return int(intg)
    else:
        return None
# -----------------------------------------------------------------------------
def plot_frac(result):
    '''using result of esti_array, plot n/totN vs totN for each temperature'''
    '''also returns mean of it and maximum of error'''
    x = result['totN'][0]
    x = np.asarray([1/(item) for item in x])
#     x = np.asarray([item for item in x])
#     x = np.asarray([1/np.sqrt(item) for item in x])
#     alist = []
#     aerrlist = []
    ylist = []
    yerrlst = []
    nfig = len(result['Tset'])
    nrow = (nfig+1)//2
    fitplot, axs = plt.subplots(nrows=nrow, ncols=2, 
                                sharex=False, figsize = [9,2*nrow])
    
    # Defining custom 'xlim' and 'ylim' values.
    custom_xlim = (0, max(x)*1.1)
    custom_ylim = (0, np.amax(result['n']/result['totN'])*1.1)

    # Setting the values for all axes.
    plt.setp(axs, xlim=custom_xlim, ylim=custom_ylim)
    
    if len(result['Tset'])<=2:
        
        for i in range(len(result['Tset'])):
            tag = str(result['Tset'][i])
            x = result['totN'][i]
            x = np.asarray([1/(item) for item in x])
            y = result['n'][i]/result['totN'][i]
            σ = result['nerr'][i]
            # peform the fits
            a1,a1_err = get_a(x,y,σ)
            
            # plot the data
            axs[i].errorbar(x, y, yerr = σ, fmt='--o',label=f'T={tag}')

            # plot the fit results
            fx = np.linspace(0,max(x)*1.1,20)
            axs[i].plot(fx,a1[0]+a1[1]*fx, color=colors[0], linewidth=1.5, zorder=0, label=f'T={tag} fit')
            
            axs[i].set_title(f'T={tag}')
            axs[i].set_xlabel('1/N')
            axs[i].set_ylabel('filling')

#             ylist.append(y)
#             yerrlst.append(σ)

            ylist.append(a1)
            yerrlst.append(a1_err)
        
    else:

        for i in range(len(result['Tset'])):
            tag = str(result['Tset'][i])
            x = result['totN'][i]
            x = np.asarray([1/(item) for item in x])
            y = result['n'][i]/result['totN'][i]
            σ = result['nerr'][i]
            # peform the fits
            a1,a1_err = get_a(x,y,σ)
            
            # plot the data
            axs[i//2,i%2].errorbar(x, y, yerr = σ, fmt='--o',label=f'T={tag}')

            #plot the fit results
            fx = np.linspace(0,max(x)*1.1,20)
            axs[i//2,i%2].plot(fx,a1[0]+a1[1]*fx, color=colors[0], linewidth=1.5, zorder=0, label=f'T={tag} fit')
    
            axs[i//2,i%2].set_title(f'T={tag}')
            axs[i//2,i%2].set_xlabel('1/N')
            axs[i//2,i%2].set_ylabel('filling')

#             ylist.append(y)
#             yerrlst.append(σ)

            ylist.append(a1)
            yerrlst.append(a1_err)

    fitplot.tight_layout()
    
#     return np.mean(ylist), np.amax(yerrlst)
    return ylist, yerrlst
# -----------------------------------------------------------------------------
def plot_superfrac(result):
    '''using result of esti_array, plot sf fraction vs 1/sqrt(totN) for each temperature'''
    '''also returns fitting parameters'''
    x = result['totN'][0]
    x = np.asarray([1/np.sqrt(item) for item in x])
    alist = []
    aerrlist = []
    nfig = len(result['Tset'])
    nrow = (nfig+1)//2
    fitplot, axs = plt.subplots(nrows=nrow, ncols=2, 
                                sharex=False, figsize = [9,2*nrow])
    
    # Defining custom 'xlim' and 'ylim' values.
    custom_xlim = (0, max(x)*1.1)
    custom_ylim = (0, np.amax(result['yarray'])*1.1)

    # Setting the values for all axes.
    plt.setp(axs, xlim=custom_xlim, ylim=custom_ylim)
    
    if len(result['Tset'])<=2:
        
        for i in range(len(result['Tset'])):
            tag = str(result['Tset'][i])
            x = result['totN'][i]
            x = np.asarray([1/np.sqrt(item) for item in x])
            y = result['yarray'][i]
            σ = result['yerrarray'][i]

            # peform the fits
            a1,a1_err = get_a(x,y,σ)

            # plot the data
            axs[i].errorbar(x,y,yerr = σ,color=colors[0], fmt='--o',label=f'T={tag}')

            # plot the fit results
            fx = np.linspace(0,max(x)*1.1,20)

            axs[i].plot(fx,a1[0]+a1[1]*fx, color=colors[0], linewidth=1.5, zorder=0, label=f'T={tag} fit')
            axs[i].set_title(f'T={tag}')
            axs[i].set_xlabel('sqrt(1/N)')
            axs[i].set_ylabel('SF fraction')

            alist.append(a1)
            aerrlist.append(a1_err)
        
    else:

        for i in range(len(result['Tset'])):
            tag = str(result['Tset'][i])
            x = result['totN'][i]
            x = np.asarray([1/np.sqrt(item) for item in x])
            y = result['yarray'][i]
            σ = result['yerrarray'][i]

            # peform the fits
            a1,a1_err = get_a(x,y,σ)

            # plot the data
            axs[i//2,i%2].errorbar(x,y,yerr = σ,color=colors[0], fmt='--o',label=f'T={tag}')

            # plot the fit results
            fx = np.linspace(0,max(x)*1.1,20)

            axs[i//2,i%2].plot(fx,a1[0]+a1[1]*fx, color=colors[0], linewidth=1.5, zorder=0, label=f'T={tag} fit')
            axs[i//2,i%2].set_title(f'T={tag}')
            axs[i//2,i%2].set_xlabel('sqrt(1/N)')
            axs[i//2,i%2].set_ylabel('SF fraction')

            alist.append(a1)
            aerrlist.append(a1_err)

    fitplot.tight_layout()
    
    return alist, aerrlist
# -----------------------------------------------------------------------------
def plot_superdens(result):
    '''using result of esti_array, plot sf density vs 1/sqrt(totN) for each temperature'''
    '''also returns fitting parameters'''
    x = result['totN'][0]
    x = np.asarray([1/np.sqrt(item) for item in x])
    alist = []
    aerrlist = []
    nfig = len(result['Tset'])
    nrow = (nfig+1)//2
    fitplot, axs = plt.subplots(nrows=nrow, ncols=2, 
                                sharex=False, figsize = [9,2*nrow])
    
    # Defining custom 'xlim' and 'ylim' values.
    custom_xlim = (0, max(x)*1.1)
    custom_ylim = (0, np.amax(result['rhosarray'])*1.1)

    # Setting the values for all axes.
    plt.setp(axs, xlim=custom_xlim, ylim=custom_ylim)
    
    if len(result['Tset'])<=2:
        for i in range(len(result['Tset'])):
            tag = str(result['Tset'][i])
            x = result['totN'][i]
            x = np.asarray([1/np.sqrt(item) for item in x])
            y = result['rhosarray'][i]
            σ = result['rhoserrarray'][i]

            # peform the fits
            a1,a1_err = get_a(x,y,σ)

            # plot the data
            axs[i].errorbar(x,y,yerr = σ,color=colors[0], fmt='--o',label=f'T={tag}')

            # plot the fit results
            fx = np.linspace(0,max(x)*1.1,20)

            axs[i].plot(fx,a1[0]+a1[1]*fx, color=colors[0], linewidth=1.5, zorder=0, label=f'T={tag} fit')
            axs[i].set_title(f'T={tag}')
            axs[i].set_xlabel('sqrt(1/N)')
            axs[i].set_ylabel(r'SF density$\times 10^{9} \,$ ($\text{g cm}^{-2}$)')

            alist.append(a1)
            aerrlist.append(a1_err)
        
    else:

        for i in range(len(result['Tset'])):
            tag = str(result['Tset'][i])
            x = result['totN'][i]
            x = np.asarray([1/np.sqrt(item) for item in x])
            y = result['rhosarray'][i]
            σ = result['rhoserrarray'][i]

            # peform the fits
            a1,a1_err = get_a(x,y,σ)

            # plot the data
            axs[i//2,i%2].errorbar(x,y,yerr = σ,color=colors[0], fmt='--o',label=f'T={tag}')

            # plot the fit results
            fx = np.linspace(0,max(x)*1.1,20)

            axs[i//2,i%2].plot(fx,a1[0]+a1[1]*fx, color=colors[0], linewidth=1.5, zorder=0, label=f'T={tag} fit')
            axs[i//2,i%2].set_title(f'T={tag}')
            axs[i//2,i%2].set_xlabel('sqrt(1/N)')
            axs[i//2,i%2].set_ylabel(r'SF density$\times 10^{9} \,$ ($\text{g cm}^{-2}$)')

            alist.append(a1)
            aerrlist.append(a1_err)

    fitplot.tight_layout()
    
    return alist, aerrlist

# -----------------------------------------------------------------------------
usage = '''How to use:
1. Make classified data dictionary with datadic(dataframe)
2. The dictionary values are subdf and take a look its keys
3. use esti_array_multi(subdf) to get dictionary of features, [result]
4. plot the [result] with
   mean, max = plot_frac(result)
   alist, aerrlist = plot_superfrac(result)
   alist, aerrlist = plot_superdens(result)
'''
# -----------------------------------------------------------------------------
def help():
    print(summary)
    print(usage)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("This is module")
    print(summary)
    print(usage)
