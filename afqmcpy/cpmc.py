import sys
import json
import time
import numpy
import warnings
import afqmcpy.state
import afqmcpy.qmc
import afqmcpy.walker
import afqmcpy.estimators

def setup(options, comm=None):
    """Wrapper routine for initialising simulation

    Parameters
    ----------
    input_file : json file.
        Simulation input file.

    Returns
    -------
    state : :class:`afqmcpy.state.State`
        Simulation state.
    """

    seed = options['qmc_options'].get('rng_seed', None)
    rank = comm.Get_rank()
    nprocs = comm.Get_size()
    if seed is None:
        # only set "random" part of seed on parent processor so we can reproduce
        # results in when running in parallel.
        if rank == 0:
            seed = numpy.array([numpy.random.randint(0, 1e8)], dtype='i4')
            # Can't serialise numpy arrays
            options['qmc_options']['rng_seed'] = seed[0].item()
        else:
            seed = numpy.empty(1, dtype='i4')
        comm.Bcast(seed, root=0)
        seed = seed[0]
    seed = seed + rank
    numpy.random.seed(seed)
    if rank == 0:
        state = afqmcpy.state.State(options.get('model'),
                                    options.get('qmc_options'),
                                    options.get('estimates'),
                                    options.get('trial_wavefunction'))
    else:
        state = None
    state = comm.bcast(state, root=0)
    if state.trial.error:
        warnings.warn('Error in constructing trial wavefunction. Exiting')
        sys.exit()
    state.rank = rank
    state.nprocs = nprocs
    state.root = state.rank == 0
    # We can't serialise '_io.BufferWriter' object, so just delay initialisation
    # of estimators object to after MPI communication.
    # TODO: Do this more gracefully.
    state.qmc.nwalkers = int(state.qmc.nwalkers/nprocs)
    if state.qmc.nwalkers == 0:
        # This should occur on all processors so we don't need to worry about
        # race conditions / mpi4py hanging.
        if state.root:
            warnings.warn('Not enough walkers for selected core count. There '
                          'must be at least one walker per core set in the '
                          'input file. Exiting.')
        sys.exit()

    psi = afqmcpy.walker.Walkers(state.system, state.trial, state.qmc.nwalkers)
    # TODO: Return state and psi and run from another routine.
    return (state, psi, comm)

def run(state, psi, estimators, comm=None):
    (state, psi) = afqmcpy.qmc.do_qmc(state, psi, estimators, comm)
    return psi

def finalise(state, estimators, init_time):
    if state.root:
        print ("# End Time: %s"%time.asctime())
        print ("# Running time : %.6f seconds"%(time.time()-init_time))
        if estimators.back_propagation:
            estimators.h5f.close()
