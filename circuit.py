import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.visualization import circuit_drawer

# Define quantum circuit for E91 Bell state preparation and measurement
qc = QuantumCircuit(2, 2)

# Bell state creation
qc.h(0)  # Hadamard gate on qubit 0
qc.cx(0, 1)  # CNOT gate (0 -> 1)

# Measurement rotation (represented as general single-qubit rotations)
qc.ry(0.5, 0)  # Rotation on Alice's qubit (simulating measurement basis change)
qc.ry(0.25, 1)  # Rotation on Bob's qubit (simulating measurement basis change)

# Measurement
qc.measure_all()

# Draw circuit
circuit_drawer(qc, output="mpl")  # Uses ASCII representation instead of Matplotlib
plt.show()