from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import jax.numpy as np
from jax.config import config
config.update("jax_enable_x64", True)

from jax.test_util import check_grads, check_jvp
from jax import custom_transforms, ad

from jaxde.odeint import odeint
from jaxde.ode_jvp import jvp_odeint

def test_odeint_jvp_z():
    D = 10
    t0 = 0.1
    t1 = 0.2
    y0 = np.linspace(0.1, 0.9, D)
    arg = np.zeros((0,))
    def f(y, t, args):
        return -np.sqrt(t) - y

    @custom_transforms
    def onearg_odeint(y0):
        return odeint(f, y0, np.array([t0, t1]), atol=1e-8, rtol=1e-8)[1]

    def onearg_jvp((y0, arg), (tangent_all,)):
        return jvp_odeint(tangent_all, f, y0, t0, t1, arg)
    ad.defjvp(onearg_odeint.primitive, onearg_jvp)

    check_jvp(onearg_odeint, onearg_jvp, (y0, arg))


def test_odeint_jvp_all():
    D = 10
    t0 = 0.1
    t1 = 0.2
    y0 = np.linspace(0.1, 0.9, D)
    fargs = (0.1, 0.2)
    def f(y, t, arg1, arg2):
        return -np.sqrt(t) - y + arg1 - np.mean((y + arg2)**2)

    @custom_transforms
    def twoarg_odeint(y0, args):
        return odeint(f, y0, np.array([t0, t1]), args=args, atol=1e-8, rtol=1e-8)[1]

    def twoarg_jvp((y0, args), tangent_all):
        return jvp_odeint(tangent_all, f, y0, t0, t1, args)
    ad.defjvp(twoarg_odeint.primitive, twoarg_jvp)

    check_jvp(twoarg_odeint, twoarg_jvp, (y0, fargs))



test_odeint_jvp_all()

def test_odeint_allgrads():
    D = 10
    t0 = 0.1
    t1 = 0.2
    y0 = np.linspace(0.1, 0.9, D)
    fargs = (0.1, 0.2)
    def f(y, t): #, arg1, arg2):
        return -np.sqrt(t) - y# + arg1 - np.mean((y + arg2)**2)

    @custom_transforms
    def onearg_odeint(y0):
        return odeint(f, y0, np.array([t0, t1]), atol=1e-8, rtol=1e-8)[1]

    def onearg_jvp(y0, tangent_y0):
        return jvp_odeint(tangent_y0, f, y0, t0, t1)
    ad.defjvp(onearg_odeint.primitive, onearg_jvp)

    check_grads(onearg_odeint, (y0, ), order=2)
