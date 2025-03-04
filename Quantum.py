from flask import Flask, render_template, request, redirect, url_for, session, flash
import numpy as np
from qiskit import QuantumCircuit
from qiskit import transpile
from qiskit_aer import Aer
import PyPDF2
import random
import io

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Constants
NUM_ENTANGLED_PAIRS = 1000
QBER_THRESHOLD = 11
TOTAL_QUBITS = 10

# In-memory storage for uploaded and received files
uploaded_files = {}
received_files = {}

# E91 Protocol Functions
def create_bell_pair():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc

# Initialize the backend
backend = Aer.get_backend('qasm_simulator')

def measure_qubit(angle):
    qc = QuantumCircuit(1, 1)
    qc.ry(2 * angle, 0)
    qc.measure(0, 0)
    new_circuit = transpile(qc, backend)  # Transpile circuit for the specific backend
    result = backend.run(new_circuit, shots=1).result()  # Run the transpiled circuit on the backend
    counts = result.get_counts()
    return int(max(counts, key=counts.get))

def simulate_e91():
    alice_angles = [0, np.pi / 4]
    bob_angles = [np.pi / 8, 3 * np.pi / 8]
    key_a, key_b = [], []
    
    for _ in range(NUM_ENTANGLED_PAIRS // (TOTAL_QUBITS // 2)):
        qc = create_bell_pair()
        alice_angle = random.choice(alice_angles)
        bob_angle = random.choice(bob_angles)

        alice_measurement = measure_qubit(alice_angle)
        bob_measurement = measure_qubit(bob_angle)
        
        if alice_angle == 0 and bob_angle == np.pi / 8 or alice_angle == np.pi / 4 and bob_angle == 3 * np.pi / 8:
            if alice_measurement == bob_measurement:
                key_a.append(alice_measurement)
                key_b.append(bob_measurement)
    return key_a, key_b

def calculate_qber(key_a, key_b):
    mismatches = sum(1 for a, b in zip(key_a, key_b) if a != b)
    return (mismatches / len(key_a)) * 100 if len(key_a) > 0 else 100

def extract_text_from_pdf(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    return ''.join(page.extract_text() or "" for page in reader.pages)

def encrypt_message(message, key):
    message_bits = ''.join(format(byte, '08b') for byte in message.encode('utf-8'))
    key_bits = ''.join(str(bit) for bit in key)
    extended_key = (key_bits * ((len(message_bits) // len(key_bits)) + 1))[:len(message_bits)]
    return ''.join(str(int(m_bit) ^ int(k_bit)) for m_bit, k_bit in zip(message_bits, extended_key))

def decrypt_message(encrypted_bits, key):
    key_bits = ''.join(str(bit) for bit in key)
    extended_key = (key_bits * ((len(encrypted_bits) // len(key_bits)) + 1))[:len(encrypted_bits)]
    decrypted_bits = ''.join(str(int(e_bit) ^ int(k_bit)) for e_bit, k_bit in zip(encrypted_bits, extended_key))
    return ''.join(chr(int(decrypted_bits[i:i+8], 2)) for i in range(0, len(decrypted_bits), 8))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        if user.lower() in ['hospital 1', 'hospital 2']:
            session['username'] = user.lower()
            return redirect(url_for('dashboard'))
        flash('Invalid username. Please log in as Hospital 1 or Hospital 2.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    if user == 'hospital 1':
        if request.method == 'POST':
            file = request.files['file']
            if file and file.filename.endswith('.pdf'):
                file_content = extract_text_from_pdf(io.BytesIO(file.read()))
                uploaded_files['hospital 1'] = file_content#love
                flash('File uploaded successfully.')
                return redirect(url_for('transfer'))
            flash('Invalid file format. Please upload a PDF file.')
        return render_template('hospital1_dashboard.html')
    elif user == 'hospital 2':
        file_content = decrypt_message(*received_files['hospital 2']) if 'hospital 2' in received_files else None
        return render_template('hospital2_dashboard.html', file_content=file_content)

@app.route('/transfer')
def transfer():
    if 'username' not in session or session['username'] != 'hospital 1':
        flash('Access denied.')
        return redirect(url_for('login'))
    if 'hospital 1' not in uploaded_files:
        flash('No file to transfer.')
        return redirect(url_for('dashboard'))

    alice_key, bob_key = simulate_e91()
    qber = calculate_qber(alice_key, bob_key)

    if len(alice_key) < 10:
        flash('Key exchange failed due to insufficient key length.')
        return redirect(url_for('dashboard'))

    if qber < QBER_THRESHOLD:
        final_key = alice_key[:len(alice_key) // 2]
        file_content = uploaded_files['hospital 1']
        encrypted_content = encrypt_message(file_content, final_key)
        received_files['hospital 2'] = (encrypted_content, final_key)
        flash('File transferred securely to Hospital 2.')
        flash(f'QBER : {qber:.2f}%')
    else:
        flash(f'Key exchange failed. QBER is {qber:.2f}%.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
