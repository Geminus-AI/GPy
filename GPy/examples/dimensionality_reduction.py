# Copyright (c) 2012, GPy authors (see AUTHORS.txt).
# Licensed under the BSD 3-clause license (see LICENSE.txt)

import numpy as np
import pylab as pb
from matplotlib import pyplot as plt, pyplot

import GPy

default_seed = np.random.seed(123344)

def BGPLVM(seed=default_seed):
    N = 10
    M = 3
    Q = 2
    D = 4
    # generate GPLVM-like data
    X = np.random.rand(N, Q)
    k = GPy.kern.rbf(Q) + GPy.kern.white(Q, 0.00001)
    K = k.K(X)
    Y = np.random.multivariate_normal(np.zeros(N), K, D).T

    k = GPy.kern.linear(Q, ARD=True) + GPy.kern.white(Q)
    # k = GPy.kern.rbf(Q) + GPy.kern.rbf(Q) + GPy.kern.white(Q)
    # k = GPy.kern.rbf(Q) + GPy.kern.bias(Q) + GPy.kern.white(Q, 0.00001)
    # k = GPy.kern.rbf(Q, ARD = False)  + GPy.kern.white(Q, 0.00001)

    m = GPy.models.Bayesian_GPLVM(Y, Q, kernel=k, M=M)
    m.constrain_positive('(rbf|bias|noise|white|S)')
    # m.constrain_fixed('S', 1)

    # pb.figure()
    # m.plot()
    # pb.title('PCA initialisation')
    # pb.figure()
    # m.optimize(messages = 1)
    # m.plot()
    # pb.title('After optimisation')
    m.ensure_default_constraints()
    m.randomize()
    m.checkgrad(verbose=1)

    return m

def GPLVM_oil_100(optimize=True, M=15):
    data = GPy.util.datasets.oil_100()

    # create simple GP model
    kernel = GPy.kern.rbf(6, ARD=True) + GPy.kern.bias(6)
    m = GPy.models.GPLVM(data['X'], 6, kernel=kernel, M=M)
    m.data_labels = data['Y'].argmax(axis=1)

    # optimize
    m.ensure_default_constraints()
    if optimize:
        m.optimize('scg', messages=1)

    # plot
    print(m)
    m.plot_latent(labels=m.data_labels)
    return m

def BGPLVM_oil(optimize=True, N=100, Q=10, M=15, max_f_eval=300):
    data = GPy.util.datasets.oil()

    # create simple GP model
    kernel = GPy.kern.rbf(Q, ARD=True) + GPy.kern.bias(Q) + GPy.kern.white(Q, 0.001)
    m = GPy.models.Bayesian_GPLVM(data['X'][:N], Q, kernel=kernel, M=M)
    m.data_labels = data['Y'][:N].argmax(axis=1)

    # optimize
    if optimize:
        m.constrain_fixed('noise', 0.05)
        m.ensure_default_constraints()
        m.optimize('scg', messages=1, max_f_eval=max(80, max_f_eval))
        m.unconstrain('noise')
        m.constrain_positive('noise')
        m.optimize('scg', messages=1, max_f_eval=max(0, max_f_eval - 80))
    else:
        m.ensure_default_constraints()

    # plot
    print(m)
    m.plot_latent(labels=m.data_labels)
    pb.figure()
    pb.bar(np.arange(m.kern.D), 1. / m.input_sensitivity())
    return m

def oil_100():
    data = GPy.util.datasets.oil_100()
    m = GPy.models.GPLVM(data['X'], 2)

    # optimize
    m.ensure_default_constraints()
    m.optimize(messages=1, max_iters=2)

    # plot
    print(m)
    # m.plot_latent(labels=data['Y'].argmax(axis=1))
    return m

def mrd_simulation(plot_sim=False):
    # num = 2
#     ard1 = np.array([1., 1, 0, 0], dtype=float)
#     ard2 = np.array([0., 1, 1, 0], dtype=float)
#     ard1[ard1 == 0] = 1E-10
#     ard2[ard2 == 0] = 1E-10

#     ard1i = 1. / ard1
#     ard2i = 1. / ard2

#     k = GPy.kern.rbf(Q, ARD=True, lengthscale=ard1i) + GPy.kern.bias(Q, 0) + GPy.kern.white(Q, 0.0001)
#     Y1 = np.random.multivariate_normal(np.zeros(N), k.K(X), D1).T
#     Y1 -= Y1.mean(0)
#
#     k = GPy.kern.rbf(Q, ARD=True, lengthscale=ard2i) + GPy.kern.bias(Q, 0) + GPy.kern.white(Q, 0.0001)
#     Y2 = np.random.multivariate_normal(np.zeros(N), k.K(X), D2).T
#     Y2 -= Y2.mean(0)
#     make_params = lambda ard: np.hstack([[1], ard, [1, .3]])

    D1, D2, D3, N, M, Q = 5, 5, 5, 150, 18, 5
    x = np.linspace(0, 2 * np.pi, N)[:, None]

    s1 = np.vectorize(lambda x: np.sin(x))
    s2 = np.vectorize(lambda x: np.cos(x))
    s3 = np.vectorize(lambda x: np.cos(4 * x))
    sS = np.vectorize(lambda x: np.sin(2 * x))

    s1 = s1(x)
    s2 = s2(x)
    s3 = s3(x)
    sS = sS(x)

    s1 /= np.abs(s1).max()
    s2 /= np.abs(s2).max()
    s3 /= np.abs(s3).max()
    sS /= np.abs(sS).max()

    S1 = np.hstack([s1, sS])
    S2 = np.hstack([s2, sS])
    S3 = np.hstack([s3, sS])

    Y1 = S1.dot(np.random.randn(S1.shape[1], D1))
    Y2 = S2.dot(np.random.randn(S2.shape[1], D2))
    Y3 = S3.dot(np.random.randn(S3.shape[1], D3))

    Y1 += .041 * np.random.randn(*Y1.shape)
    Y2 += .041 * np.random.randn(*Y2.shape)
    Y3 += .041 * np.random.randn(*Y3.shape)

    Y1 -= Y1.mean(0)
    Y2 -= Y2.mean(0)
    Y3 -= Y3.mean(0)
    Y1 /= Y1.std(0)
    Y2 /= Y2.std(0)
    Y3 /= Y3.std(0)

    Slist = [s1, s2, s3, sS]
    Ylist = [Y1, Y2, Y3]

    if plot_sim:
        import pylab
        import itertools
        fig = pylab.figure("MRD Simulation", figsize=(12, 12))
        fig.clf()
        ax = fig.add_subplot(2, 1, 1)
        labls = sorted(filter(lambda x: x.startswith("s"), locals()))
        for S, lab in itertools.izip(Slist, labls):
            ax.plot(x, S, label=lab)
        ax.legend()
        for i, Y in enumerate(Ylist):
            ax = fig.add_subplot(2, len(Ylist), len(Slist) + i)
            ax.imshow(Y)
            ax.set_title("Y{}".format(i + 1))
        pylab.draw()
        pylab.tight_layout()

    from GPy.models import mrd
    from GPy import kern
    reload(mrd); reload(kern)
    k = kern.rbf(Q, ARD=True) + kern.bias(Q) + kern.white(Q)
    m = mrd.MRD(*Ylist, Q=Q, M=M, kernel=k, init="concat", _debug=False)
    m.ensure_default_constraints()

    # cstr = "noise|white|variance"
    # m.unconstrain(cstr); m.constrain_bounded(cstr, 1e-6, 1.)

    m.auto_scale_factor = True

#     fig = pyplot.figure("expected", figsize=(8, 3))
#     ax = fig.add_subplot(121)
#     ax.bar(np.arange(ard1.size) + .1, ard1)
#     ax = fig.add_subplot(122)
#     ax.bar(np.arange(ard2.size) + .1, ard2)

    return m

def mrd_silhouette():

    pass

def brendan_faces():
    data = GPy.util.datasets.brendan_faces()
    Y = data['Y'][0:-1:10, :]
    m = GPy.models.GPLVM(data['Y'], 2)

    # optimize
    m.ensure_default_constraints()
    m.optimize(messages=1, max_f_eval=10000)

    ax = m.plot_latent()
    y = m.likelihood.Y[0, :]
    data_show = GPy.util.visualize.image_show(y[None, :], dimensions=(20, 28), transpose=True, invert=False, scale=False)
    lvm_visualizer = GPy.util.visualize.lvm(m, data_show, ax)
    raw_input('Press enter to finish')
    plt.close('all')

    return m

def stick():
    data = GPy.util.datasets.stick()
    m = GPy.models.GPLVM(data['Y'], 2)

    # optimize
    m.ensure_default_constraints()
    m.optimize(messages=1, max_f_eval=10000)

    ax = m.plot_latent()
    y = m.likelihood.Y[0, :]
    data_show = GPy.util.visualize.stick_show(y[None, :], connect=data['connect'])
    lvm_visualizer = GPy.util.visualize.lvm(m, data_show, ax)
    raw_input('Press enter to finish')
    plt.close('all')

    return m

# def BGPLVM_oil():
#     data = GPy.util.datasets.oil()
#     Y, X = data['Y'], data['X']
#     X -= X.mean(axis=0)
#     X /= X.std(axis=0)
#
#     Q = 10
#     M = 30
#
#     kernel = GPy.kern.rbf(Q, ARD=True) + GPy.kern.bias(Q) + GPy.kern.white(Q)
#     m = GPy.models.Bayesian_GPLVM(X, Q, kernel=kernel, M=M)
#     # m.scale_factor = 100.0
#     m.constrain_positive('(white|noise|bias|X_variance|rbf_variance|rbf_length)')
#     from sklearn import cluster
#     km = cluster.KMeans(M, verbose=10)
#     Z = km.fit(m.X).cluster_centers_
#     # Z = GPy.util.misc.kmm_init(m.X, M)
#     m.set('iip', Z)
#     m.set('bias', 1e-4)
#     # optimize
#     # m.ensure_default_constraints()
#
#     import pdb; pdb.set_trace()
#     m.optimize('tnc', messages=1)
#     print m
#     m.plot_latent(labels=data['Y'].argmax(axis=1))
#     return m
