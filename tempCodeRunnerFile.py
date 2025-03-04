import matplotlib.pyplot as plt

# Data for the chart
trends = [
    'Quantum Hardware Advancements',
    'Quantum Algorithms',
    'Quantum Software and Tools',
    'Quantum Cryptography',
    'Applications and Use Cases'
]

impact = [80, 70, 60, 75, 65]  # Estimated impact (just an example, adjust as needed)

# Creating the bar chart
plt.figure(figsize=(10, 6))
plt.barh(trends, impact, color='skyblue')

# Adding title and labels
plt.title('Recent Trends in Quantum Computing', fontsize=14)
plt.xlabel('Impact (Relative Estimate)', fontsize=12)
plt.ylabel('Trend Categories', fontsize=12)

# Displaying the chart
plt.tight_layout()
plt.show()
