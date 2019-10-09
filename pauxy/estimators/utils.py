import h5py

class H5EstimatorHelper(object):
    """Helper class for pushing data to hdf5 dataset of fixed length.

    Parameters
    ----------
    h5f : :class:`h5py.File`
        Output file object.
    name : string
        Dataset name.
    shape : tuple
        Shape of output data.
    dtype : type
        Output data type.

    Attributes
    ----------
    store : :class:`h5py.File.DataSet`
        Dataset object.
    index : int
        Counter for incrementing data.
    """
    def __init__(self, filename, base):
        # self.store = h5f.create_dataset(name, shape, dtype=dtype)
        self.filename = filename
        self.base = base
        self.index = 0
        self.nzero = 9

    def push(self, data, name):
        """Push data to dataset.

        Parameters
        ----------
        data : :class:`numpy.ndarray`
            Data to push.
        """
        ix = str(self.index)
        # To ensure string indices are sorted properly.
        padded = '0'*(self.nzero-len(ix)) + ix
        dset = self.base + '/' + name + '/' + padded
        with h5py.File(self.filename, 'a') as fh5:
            fh5[dset] = data

    def increment(self):
        self.index = self.index + 1

    def reset(self):
        self.index = 0
