# Copyright 2019 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=protected-access
"""
This module contains the functions for computing different types of measurement
outcomes from quantum observables - expectation values, variances of expectations,
and measurement samples.
"""
import pennylane as qml
from .operation import Observable, Sample, Variance, Expectation, Probability, Tensor
from .qnodes import QuantumFunctionError


def _remove_if_in_queue(op):
    r"""Helper function to handle removing ops from the QNode queue"""
    if op in qml._current_context.queue:
        qml._current_context.queue.remove(op)


def expval(op):
    r"""Expectation value of the supplied observable.

    **Example:**

    .. code-block:: python3

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit(x):
            qml.RX(x, wires=0)
            qml.Hadamard(wires=1)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliY(0))

    Executing this QNode:

    >>> circuit(0.5)
    -0.4794255386042029

    Args:
        op (Observable): a quantum observable object

    Raises:
        QuantumFunctionError: `op` is not an instance of :class:`~.Observable`
    """
    if not isinstance(op, Observable):
        raise QuantumFunctionError(
            "{} is not an observable: cannot be used with expval".format(op.name)
        )

    if qml._current_context is not None:
        # delete observables from QNode operation queue if needed
        if isinstance(op, Tensor):
            for o in op.obs:
                _remove_if_in_queue(o)
        else:
            _remove_if_in_queue(op)

    # set return type to be an expectation value
    op.return_type = Expectation

    if qml._current_context is not None:
        # add observable to QNode observable queue
        qml._current_context._append_op(op)

    return op


def var(op):
    r"""Variance of the supplied observable.

    **Example:**

    .. code-block:: python3

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit(x):
            qml.RX(x, wires=0)
            qml.Hadamard(wires=1)
            qml.CNOT(wires=[0, 1])
            return qml.var(qml.PauliY(0))

    Executing this QNode:

    >>> circuit(0.5)
    0.7701511529340698

    Args:
        op (Observable): a quantum observable object

    Raises:
        QuantumFunctionError: `op` is not an instance of :class:`~.Observable`
    """
    if not isinstance(op, Observable):
        raise QuantumFunctionError(
            "{} is not an observable: cannot be used with var".format(op.name)
        )

    if qml._current_context is not None:
        # delete operations from QNode queue
        if isinstance(op, Tensor):
            for o in op.obs:
                _remove_if_in_queue(o)
        else:
            _remove_if_in_queue(op)

    # set return type to be a variance
    op.return_type = Variance

    if qml._current_context is not None:
        # add observable to QNode observable queue
        qml._current_context._append_op(op)

    return op


def sample(op):
    r"""Sample from the supplied observable, with the number of shots
    determined from the ``dev.shots`` attribute of the corresponding device.

    **Example:**

    .. code-block:: python3

        dev = qml.device("default.qubit", wires=2, shots=4)

        @qml.qnode(dev)
        def circuit(x):
            qml.RX(x, wires=0)
            qml.Hadamard(wires=1)
            qml.CNOT(wires=[0, 1])
            return qml.sample(qml.PauliY(0))

    Executing this QNode:

    >>> circuit(0.5)
    array([ 1.,  1.,  1., -1.])

    Args:
        op (Observable): a quantum observable object

    Raises:
        QuantumFunctionError: `op` is not an instance of :class:`~.Observable`
    """
    if not isinstance(op, Observable):
        raise QuantumFunctionError(
            "{} is not an observable: cannot be used with sample".format(op.name)
        )

    if qml._current_context is not None:
        # delete operations from QNode queue
        if isinstance(op, Tensor):
            for o in op.obs:
                _remove_if_in_queue(o)
        else:
            _remove_if_in_queue(op)

    # set return type to be a sample
    op.return_type = Sample

    if qml._current_context is not None:
        # add observable to QNode observable queue
        qml._current_context._append_op(op)

    return op


def probs(wires):
    r"""Probability of each computational basis state.

    This measurement function accepts no observables, and instead
    instructs the QNode to return a flat array containing the
    probabilities of each quantum state.

    Marginal probabilities may also be requested by restricting
    the wires to a subset of the full system; the size of the
    returned array will be ``[2**len(wires)]``.

    **Example:**

    .. code-block:: python3

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(wires=1)
            qml.CNOT(wires=[0, 1])
            return qml.probs(wires=[0, 1])

    Executing this QNode:

    >>> circuit()
    array([0.5, 0.5, 0. , 0. ])

    The returned array is in lexicographic order, so corresponds
    to a :math:`50\%` chance of measuring either :math:`|00\rangle`
    or :math:`|01\rangle`.

    Args:
        wires (Sequence[int] or int): the wire the operation acts on
    """
    # pylint: disable=protected-access
    op = qml.Identity(wires=wires, do_queue=False)
    op.return_type = Probability

    if qml._current_context is not None:
        # add observable to QNode observable queue
        qml._current_context._append_op(op)

    return op
