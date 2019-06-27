import numpy
import pandas as pd
import scipy.stats
from pauxy.analysis.extraction import extract_hdf5_data_sets, set_info
from pauxy.analysis.blocking import average_ratio

def analyse_energy(files):
    data = extract_hdf5_data_sets(files)
    sims = []
    for (i, g) in enumerate(data):
        (m, norm, bp, itcf, itcfk, mixed_rdm, bp_rdm) = g
        keys = set_info(norm, m)
        nzero = numpy.nonzero(norm['Weight'].values)[0][-1]
        sims.append(norm[1:nzero+1])
    full = pd.concat(sims).groupby(keys)
    analysed = []
    for (i, g) in full:
        if g['free_projection'].values[0]:
            cols = ['ENumer', 'Nav']
            obs = ['ETotal', 'Nav']
            averaged = pd.DataFrame(index=[0])
            for (c, o) in zip(cols, obs):
                (value, error)  = average_ratio(g[c].values, g['E_denom'].values)
                averaged[o] = [value]
                averaged[o+'_error'] = [error]
            for (k, v) in zip(full.keys, i):
                averaged[k] = v
            analysed.append(averaged)
        else:
            cols = ['ETotal', 'E1Body', 'E2Body', 'Nav']
            averaged = pd.DataFrame(index=[0])
            for c in cols:
                mean = numpy.real(g[c].values).mean()
                error = scipy.stats.sem(numpy.real(g[c].values), ddof=1)
                averaged[c] = [mean]
                averaged[c+'_error'] = [error]
            for (k, v) in zip(full.keys, i):
                averaged[k] = v
            analysed.append(averaged)
    return (pd.concat(analysed).reset_index(drop=True))
