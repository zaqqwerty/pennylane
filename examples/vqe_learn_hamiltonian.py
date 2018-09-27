"""Variational quantum eigensolver example.
In this demo we use a fixed quantum circuit
and optimize the (classical) Hamiltonian parameters
to lower the energy expectation. """

import openqml as qm
from openqml import numpy as np
import autograd

dev1 = qm.device('default.qubit', wires=2)


def ansatz():
    qm.QubitStateVector(np.array([1,1,0,1])/np.sqrt(3), wires=[0, 1])
    qm.Rot(0.4, 0.3, 1.3, [0])
    qm.CNOT([0, 1])


@qm.qfunc(dev1)
def circuit_Z():
    """QNode"""
    ansatz()
    return qm.expectation.PauliZ(1)


@qm.qfunc(dev1)
def circuit_Y():
    """QNode"""
    ansatz()
    return qm.expectation.PauliY(1)


@qm.qfunc(dev1)
def circuit_X():
    """QNode"""
    ansatz()
    return qm.expectation.PauliX(1)


def cost(weights, batch):
    """Cost (error) function to be minimized."""

    expZ = circuit_Z()
    expX = circuit_X()
    expY = circuit_Y()

    return weights[0]*expX + weights[1]*expY - weights[2]*expZ


# initialize x with random value
x0 = np.random.randn(3)

o = qm.Optimizer(cost, x0)

# train the device
print('Initial rotation angles:', x0)
o.train(max_steps=100)
o.weights

# print the results
print('Initial rotation angles:', x0)
print('Optimized rotation angles:', o.weights)