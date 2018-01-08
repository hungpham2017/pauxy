'''Various useful routines maybe not appropriate elsewhere'''

import numpy
import scipy.linalg

def sherman_morrison(Ainv, u, vt):
    r"""Sherman-Morrison update of a matrix inverse:

    .. math::
        (A + u \otimes v)^{-1} = A^{-1} - \frac{A^{-1}u v^{T} A^{-1}}
                                               {1+v^{T}A^{-1} u}

    Parameters
    ----------
    Ainv : numpy.ndarray
        Matrix inverse of A to be updated.
    u : numpy.array
        column vector
    vt : numpy.array
        transpose of row vector

    Returns
    -------
    Ainv : numpy.ndarray
        Updated matrix inverse.
    """

    return (
        Ainv - (Ainv.dot(numpy.outer(u,vt)).dot(Ainv))/(1.0+vt.dot(Ainv).dot(u))
    )


def diagonalise_sorted(H):
    """Diagonalise Hermitian matrix H and return sorted eigenvalues and vectors.

    Eigenvalues are sorted as e_1 < e_2 < .... < e_N, where H is an NxN
    Hermitian matrix.

    Parameters
    ----------
    H : :class:`numpy.ndarray`
        Hamiltonian matrix to be diagonalised.

    Returns
    -------
    eigs : :class:`numpy.array`
        Sorted eigenvalues
    eigv :  :class:`numpy.array`
        Sorted eigenvectors (same sorting as eigenvalues).
    """

    (eigs, eigv) = scipy.linalg.eigh(H)
    idx = eigs.argsort()
    eigs = eigs[idx]
    eigv = eigv[:,idx]

    return (eigs, eigv)

def format_fixed_width_strings(strings):
    return ' '.join('{:>17}'.format(s) for s in strings)

def format_fixed_width_floats(floats):
    return ' '.join('{: .10e}'.format(f) for f in floats)

def regularise_matrix_inverse(A, cutoff=1e-10):
    """Perform inverse of singular matrix.

    First compute SVD of input matrix then add a tuneable cutoff which washes
    out elements whose singular values are close to zero.

    Parameters
    ----------
    A : class:`numpy.array`
        Input matrix.
    cutoff : float
        Cutoff parameter.

    Returns
    -------
    B : class:`numpy.array`
        Regularised matrix inverse (pseudo-inverse).
    """
    (U,D,V) = scipy.linalg.svd(A)
    D = D / (cutoff**2.0+D**2.0)
    return (V.conj().T).dot(numpy.diag(D)).dot(U.conj().T)


def fft_wavefunction(psi, nx, ny, ns, sin):
    return numpy.fft.fft2(psi.reshape(nx,ny,ns),
                          axes=(0,1)).reshape(sin)

def ifft_wavefunction(psi, nx, ny, ns, sin):
    return numpy.fft.ifft2(psi.reshape(nx,ny,ns),
                                 axes=(0,1)).reshape(sin)

def reortho(A):
    """Reorthogonalise a MxN matrix A.

    Performs a QR decomposition of A. Note that for consistency elsewhere we
    want to preserve detR > 0 which is not guaranteed. We thus factor the signs
    of the diagonal of R into Q.

    Parameters
    ----------
    A : :class:`numpy.ndarray`
        MxN matrix. On output its columns will be mutually orthogonal.

    Returns
    -------
    detR : float
        Determinant of upper triangular matrix (R) from QR decomposition.
    """
    (A, R) = scipy.linalg.qr(A, mode='economic')
    signs = numpy.diag(numpy.sign(numpy.diag(R)))
    A = A.dot(signs)
    detR = scipy.linalg.det(signs.dot(R))
    return detR

def get_git_revision_hash():
    """ Return git revision.

    Adapted from:
        http://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script

    Returns
    -------
    sha1 : string
        git hash with -dirty appended if uncommitted changes.
    """

    src = [s for s in sys.path if 'afqmcpy' in s][-1]

    sha1 = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                   cwd=src).strip()
    suffix = subprocess.check_output(['git', 'status',
                                     '--porcelain',
                                     './afqmcpy'],
                                     cwd=src).strip()
    if suffix:
        return sha1.decode('utf-8') + '-dirty'
    else:
        return sha1.decode('utf-8')
