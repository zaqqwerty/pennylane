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
"""
Unit tests for the :mod:`pennylane.circuit_graph` module.
"""
# pylint: disable=no-self-use,too-many-arguments,protected-access

import pytest
import numpy as np

import pennylane as qml
from pennylane.operation import Expectation
from pennylane.circuit_graph import CircuitGraph


@pytest.fixture
def queue():
    """A fixture of a complex example of operations that depend on previous operations."""
    return [
        qml.RX(0.43, wires=0),
        qml.RY(0.35, wires=1),
        qml.RZ(0.35, wires=2),
        qml.CNOT(wires=[0, 1]),
        qml.Hadamard(wires=2),
        qml.CNOT(wires=[2, 0]),
        qml.PauliX(wires=1),
    ]


@pytest.fixture
def obs():
    """A fixture of observables to go after the queue fixture."""
    return [
        qml.expval(qml.PauliX(wires=0)),
        qml.expval(qml.Hermitian(np.identity(4), wires=[1, 2])),
    ]


@pytest.fixture
def ops(queue, obs):
    """Queue of Operations followed by Observables."""
    return queue + obs


@pytest.fixture
def circuit(ops):
    """A fixture of a circuit generated based on the queue and obs fixtures above."""
    circuit = CircuitGraph(ops, {})
    return circuit


@pytest.fixture
def parameterized_circuit():
    def qfunc(a, b, c, d, e, f):
        qml.Rotation(a, wires=0),
        qml.Rotation(b, wires=1),
        qml.Rotation(c, wires=2),
        qml.Beamsplitter(d, 1, wires=[0, 1])
        qml.Rotation(1, wires=0),
        qml.Rotation(e, wires=1),
        qml.Rotation(f, wires=2),

        return [
            qml.expval(qml.ops.NumberOperator(wires=0)),
            qml.expval(qml.ops.NumberOperator(wires=1)),
            qml.expval(qml.ops.NumberOperator(wires=2)),
        ]

    return qfunc


@pytest.fixture
def parameterized_qubit_circuit():
    def qfunc(a, b, c, d, e, f):
        qml.RX(a, wires=0)
        qml.RX(b, wires=1)
        qml.PauliZ(1)
        qml.CNOT(wires=[0, 1])
        qml.CRY(b, wires=[3, 1])
        qml.RX(d, wires=0)
        qml.RX(4 * e, wires=1)
        qml.RY(17 / 9 * c, wires=2)
        qml.RZ(b, wires=3)
        qml.RX(f, wires=2)
        qml.CRY(0.3589, wires=[3, 1])
        qml.QubitUnitary(np.eye(2), wires=[2])
        qml.Toffoli(wires=[0, 2, 1])
        qml.CZ(wires=[0, 1])
        qml.CZ(wires=[0, 2])
        qml.CNOT(wires=[2, 1])
        qml.CNOT(wires=[0, 2])
        qml.SWAP(wires=[0, 2])
        qml.CNOT(wires=[1, 3])
        qml.RZ(b, wires=3)
        qml.CSWAP(wires=[4, 0, 1])

        return [
            qml.expval(qml.PauliY(0)),
            qml.var(qml.Hadamard(wires=1)),
            qml.sample(qml.PauliX(2)),
            qml.expval(qml.Hermitian(np.eye(4), wires=[3, 4])),
        ]

    return qfunc


@pytest.fixture
def parameterized_wide_qubit_circuit():
    def qfunc(a, b, c, d, e, f):
        qml.RX(a, wires=0)
        qml.RX(b, wires=1)
        [qml.CNOT(wires=[2 * i, 2 * i + 1]) for i in range(4)]
        [qml.CNOT(wires=[i, i + 4]) for i in range(4)]
        [qml.CSWAP(wires=[i + 2, i, i + 4]) for i in range(4)]
        qml.RX(a, wires=0)
        qml.RX(b, wires=1)

        return [qml.expval(qml.Hermitian(np.eye(4), wires=[i, i + 4])) for i in range(4)]

    return qfunc


@pytest.fixture
def parameterized_wide_cv_circuit():
    def qfunc(a, b, c, d, e, f):
        qml.GaussianState(
            np.array([(2 * i + 2) // 2 for i in range(16)]), 2 * np.eye(16), wires=list(range(8))
        )
        [qml.Beamsplitter(0.4, 0, wires=[2 * i, 2 * i + 1]) for i in range(4)]
        [qml.Beamsplitter(0.25475, 0.2312344, wires=[i, i + 4]) for i in range(4)]

        return [
            qml.expval(qml.FockStateProjector(np.array([1, 1]), wires=[i, i + 4])) for i in range(4)
        ]

    return qfunc


@pytest.fixture
def parameterized_cv_circuit():
    def qfunc(a, b, c, d, e, f):
        qml.ThermalState(3, wires=[1])
        qml.GaussianState(np.array([1, 1, 1, 2, 2, 3, 3, 3]), 2 * np.eye(8), wires=[0, 1, 2, 3])
        qml.Rotation(a, wires=0)
        qml.Rotation(b, wires=1)
        qml.Beamsplitter(d, 1, wires=[0, 1])
        qml.Beamsplitter(e, 1, wires=[1, 2])
        qml.Displacement(f, 0, wires=[3])
        qml.Squeezing(2.3, 0, wires=[0])
        qml.Squeezing(2.3, 0, wires=[2])
        qml.Beamsplitter(d, 1, wires=[1, 2])
        qml.Beamsplitter(e, 1, wires=[2, 3])
        qml.TwoModeSqueezing(2, 2, wires=[3, 1])
        qml.ControlledPhase(2.3, wires=[2, 1])
        qml.ControlledAddition(2, wires=[0, 3])
        qml.QuadraticPhase(4, wires=[0])
        # qml.Kerr(2, wires=[1])
        # qml.CubicPhase(2, wires=[2])
        # qml.CrossKerr(2, wires=[3, 1])

        return [
            qml.expval(qml.ops.PolyXP(np.array([0, 1, 2]), wires=0)),
            qml.expval(qml.ops.QuadOperator(4, wires=1)),
            qml.expval(qml.ops.FockStateProjector(np.array([1, 5]), wires=[2, 3])),
        ]

    return qfunc


class TestCircuitGraph:
    """Test conversion of queues to DAGs"""

    def test_no_dependence(self):
        """Test case where operations do not depend on each other.
        This should result in a graph with no edges."""

        ops = [qml.RX(0.43, wires=0), qml.RY(0.35, wires=1)]

        res = CircuitGraph(ops, {}).graph
        assert len(res) == 2
        assert not res.edges()

    def test_dependence(self, ops):
        """Test a more complex example containing operations
        that do depend on the result of previous operations"""

        circuit = CircuitGraph(ops, {})
        graph = circuit.graph
        assert len(graph) == 9
        assert len(graph.edges()) == 9

        # all ops should be nodes in the graph
        for k in ops:
            assert k in graph.nodes

        # all nodes in the graph should be ops
        for k in graph.nodes:
            assert k is ops[k.queue_idx]

        # Finally, checking the adjacency of the returned DAG:
        assert set(graph.edges()) == set(
            (ops[a], ops[b])
            for a, b in [(0, 3), (1, 3), (2, 4), (3, 5), (3, 6), (4, 5), (5, 7), (5, 8), (6, 8),]
        )

    def test_ancestors_and_descendants_example(self, ops):
        """
        Test that the ``ancestors`` and ``descendants`` methods return the expected result.
        """
        circuit = CircuitGraph(ops, {})

        ancestors = circuit.ancestors([ops[6]])
        assert len(ancestors) == 3
        for o_idx in (0, 1, 3):
            assert ops[o_idx] in ancestors

        descendants = circuit.descendants([ops[6]])
        assert descendants == set([ops[8]])

    def test_update_node(self, ops):
        """Changing nodes in the graph."""

        circuit = CircuitGraph(ops, {})
        new = qml.RX(0.1, wires=0)
        circuit.update_node(ops[0], new)
        assert circuit.operations[0] is new

    def test_observables(self, circuit, obs):
        """Test that the `observables` property returns the list of observables in the circuit."""
        assert circuit.observables == obs

    def test_operations(self, circuit, queue):
        """Test that the `operations` property returns the list of operations in the circuit."""
        assert circuit.operations == queue

    def test_op_indices(self, circuit):
        """Test that for the given circuit, this method will fetch the correct operation indices for
        a given wire"""
        op_indices_for_wire_0 = [0, 3, 5, 7]
        op_indices_for_wire_1 = [1, 3, 6, 8]
        op_indices_for_wire_2 = [2, 4, 5, 8]

        assert circuit.wire_indices(0) == op_indices_for_wire_0
        assert circuit.wire_indices(1) == op_indices_for_wire_1
        assert circuit.wire_indices(2) == op_indices_for_wire_2

    def test_layers(self, parameterized_circuit):
        """A test of a simple circuit with 3 layers and 6 parameters"""

        dev = qml.device("default.gaussian", wires=3)
        qnode = qml.QNode(parameterized_circuit, dev)
        qnode._construct((0.1, 0.2, 0.3, 0.4, 0.5, 0.6), {})
        circuit = qnode.circuit
        layers = circuit.layers
        ops = circuit.operations

        assert len(layers) == 3
        assert layers[0].ops == [ops[x] for x in [0, 1, 2]]
        assert layers[0].param_inds == [0, 1, 2]
        assert layers[1].ops == [ops[3]]
        assert layers[1].param_inds == [3]
        assert layers[2].ops == [ops[x] for x in [5, 6]]
        assert layers[2].param_inds == [4, 5]

    def test_iterate_layers(self, parameterized_circuit):
        """A test of the different layers, their successors and ancestors using a simple circuit"""

        dev = qml.device("default.gaussian", wires=3)
        qnode = qml.QNode(parameterized_circuit, dev)
        qnode._construct((0.1, 0.2, 0.3, 0.4, 0.5, 0.6), {})
        circuit = qnode.circuit
        result = list(circuit.iterate_layers())

        assert len(result) == 3
        assert set(result[0][0]) == set([])
        assert set(result[0][1]) == set(circuit.operations[:3])
        assert result[0][2] == (0, 1, 2)
        assert set(result[0][3]) == set(circuit.operations[3:] + circuit.observables)

        assert set(result[1][0]) == set(circuit.operations[:2])
        assert set(result[1][1]) == set([circuit.operations[3]])
        assert result[1][2] == (3,)
        assert set(result[1][3]) == set(circuit.operations[4:6] + circuit.observables[:2])

        assert set(result[2][0]) == set(circuit.operations[:4])
        assert set(result[2][1]) == set(circuit.operations[5:])
        assert result[2][2] == (4, 5)
        assert set(result[2][3]) == set(circuit.observables[1:])


class TestCircuitGraphDrawing:
    def test_simple_circuit(self, parameterized_qubit_circuit):
        """A test of the different layers, their successors and ancestors using a simple circuit"""

        dev = qml.device("default.qubit", wires=5)
        qnode = qml.QNode(parameterized_qubit_circuit, dev)
        qnode._construct((0.1, 0.2, 0.3, 0.4, 0.5, 0.6), {})
        print(qnode.circuit.render(show_variable_names=True))
        qnode.evaluate((0.1, 0.2, 0.3, 47 / 17, 0.5, 0.6), {})
        print(qnode.circuit.render())

    def test_wide_circuit(self, parameterized_wide_qubit_circuit):
        """A test of the different layers, their successors and ancestors using a simple circuit"""

        dev = qml.device("default.qubit", wires=8)
        qnode = qml.QNode(parameterized_wide_qubit_circuit, dev)
        qnode._construct((0.1, 0.2, 0.3, 0.4, 0.5, 0.6), {})
        print(qnode.circuit.render(show_variable_names=True))
        qnode.evaluate((0.1, 0.2, 0.3, 47 / 17, 0.5, 0.6), {})
        print(qnode.circuit.render())

    def test_simple_cv_circuit(self, parameterized_cv_circuit):
        """A test of the different layers, their successors and ancestors using a simple circuit"""

        dev = qml.device("default.gaussian", wires=4)
        qnode = qml.QNode(parameterized_cv_circuit, dev)
        qnode._construct((0.1, 0.2, 0.3, 0.4, 0.5, 0.6), {})
        print(qnode.circuit.render())
        qnode.evaluate((0.1, 0.2, 0.3, 47 / 17, 0.5, 0.6), {})
        print(qnode.circuit.render())

    def test_wide_cv_circuit(self, parameterized_wide_cv_circuit):
        """A test of the different layers, their successors and ancestors using a simple circuit"""

        dev = qml.device("default.gaussian", wires=8)
        qnode = qml.QNode(parameterized_wide_cv_circuit, dev)
        qnode._construct((0.1, 0.2, 0.3, 0.4, 0.5, 0.6), {})
        print(qnode.circuit.render())
        qnode.evaluate((0.1, 0.2, 0.3, 47 / 17, 0.5, 0.6), {})
        print(qnode.circuit.render())

    def test_template(self, parameterized_wide_cv_circuit):
        """A test of the different layers, their successors and ancestors using a simple circuit"""

        dev = qml.device("default.qubit", wires=8)

        @qml.qnode(dev)
        def circuit(a, b, weights, c, d, other_weights):
            qml.templates.StronglyEntanglingLayers(weights, wires=range(8))
            qml.RX(a, wires=[0])
            qml.RX(b, wires=[1])
            qml.RX(c, wires=[2])
            qml.RX(d, wires=[3])
            [qml.RX(other_weights[i], wires=[i]) for i, weight in enumerate(other_weights)]

            return [qml.var(qml.PauliX(i)) for i in range(8)]

        weights = qml.init.strong_ent_layers_uniform(3, 8)

        circuit._construct((2, 3, weights, 1, 33, np.array([1, 3, 4, 2, 2, 2, 3, 4])), {})

        print(circuit.circuit.render(show_variable_names=True))

        circuit(2, 3, weights, 1, 33, np.array([1, 3, 4, 2, 2, 2, 3, 4]))

        print(circuit.circuit.render())
        circuit.print_applied()

        raise Exception()
