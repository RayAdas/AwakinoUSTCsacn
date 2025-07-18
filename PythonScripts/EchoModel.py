from collections import namedtuple
import numpy as np
from math import pi

EchoInfo = namedtuple('EchoInfo', ['fc', 'tau', 'phi','alpha', 'beta', 'r', 'tanh_m'])

echo_info_min = EchoInfo(2.3e6, 0, 0, 2e12, 0, -1, 16)
echo_info_max = EchoInfo(2.7e6, 30e-6, 2*pi, 2e12, 10e-6, 1, 16)
echo_info_default = EchoInfo(2.5e6, 0, 0, 2e12, 1, 0, 16)

def echo_function(t,
                  tau,
                  beta,
                  fc = echo_info_default.fc,
                  phi = echo_info_default.phi,
                  alpha = echo_info_default.alpha,
                  r = echo_info_default.r,
                  tanh_m = echo_info_default.tanh_m):
    env = beta * np.exp(-alpha * (1 - r * np.tanh(tanh_m * (t - tau))) * (t - tau) ** 2)
    s = env * np.cos(2 * np.pi * fc * (t - tau) + phi)
    return s