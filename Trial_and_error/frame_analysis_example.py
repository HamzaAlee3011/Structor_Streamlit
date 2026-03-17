# import sympy as sp
#
# # Define the symbol
# x = sp.Symbol('x', real=True, positive=True)
#
# # Given values (converted where necessary)
# E = 10*10e3  # MPa = N/mm²
# I = 1.562e6  # mm^4
# L = 5000  # mm
# K = 0.7
# e = 150  # mm
# c = 75  # mm
# A = 7500  # mm²
# r = 43.29  # mm
#
# # Define the function
# theta = (K * L / r) * sp.sqrt(x / (4 * E * A))
# f_x = x * (1 + (e * c / r**2) * sp.sec(theta)) - (7500 * 15)
#
# # Solve the equation numerically using nsolve
# # Provide an initial guess close to the expected root
# initial_guess = 100  # Adjust if needed
# x_val = sp.nsolve(f_x, x, initial_guess)
#
# # Print result
# print(f"Solution for x: {x_val.evalf():.4f} N")
#

import openseespy.opensees as ops

# Initialize the OpenSees model
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)  # 2D model with 3 DOF per node

# Define nodes (nodeTag, xCrd, yCrd)
ops.node(1, 0.0, 0.0)  # Node 1 at (0, 0)
ops.node(2, 0.0, 3.0)  # Node 2 at (0, 3)
ops.node(3, 4.0, 3.0)  # Node 2 at (4, 3)
ops.node(4, 4.0, 6.0)  # Node 2 at (4, 6)

# Fix supports (nodeTag, DOF1, DOF2, DOF3)
ops.fix(1, 1, 1, 1)  # Fully fixed at Node 1
ops.fix(4, 1, 1, 1)  # Fully fixed at Node 1

# Define material (uniaxialMaterial type, matTag, E)
ops.uniaxialMaterial('Elastic', 1, 21000000)  # Elastic material with E = 3000

# Define section (section type, secTag, matTag, A, I)
ops.section('Elastic', 1, 210000, 0.15, 0.0045)  # Area = 0.02, I = 0.0001

# Define geometric transformation (geomTransf type, transfTag)
ops.geomTransf('Linear', 1)

# Define element (element type, eleTag, iNode, jNode, transfTag, secTag)
ops.element('elasticBeamColumn', 1, 1, 2, 1, 1)
ops.element('elasticBeamColumn', 2, 2, 3, 1, 1)
ops.element('elasticBeamColumn', 3, 3, 4, 1, 1)

# Apply loads
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, 100, 0.0, 0.0)  # Apply 10 kN horizontal load at Node 2
ops.load(3, 0, 0.0, -50)  # Apply 10 kN horizontal load at Node 2

# Define analysis parameters
ops.system('BandGeneral')
ops.numberer('Plain')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

# Perform the analysis
ops.analyze(1)

# Get results
disp_node2 = ops.nodeDisp(2)  # Displacements at Node 2
disp_node3 = ops.nodeDisp(3)  # Displacements at Node 2
print(f"Displacements at Node 2: {disp_node2}")
print(f"Displacements at Node 3: {disp_node3}")

# Clean up
ops.wipe()

ops.defaultUnits()

