import openseespy.opensees as ops
import opsvis
import opsvis as opsv
import matplotlib.pyplot as plt

# Plotting function for structure
def PlotStructure(title):
    opsv.plot_model(fig_wi_he=(30, 30))  # smaller size for clarity
    plt.title(title)
    plt.grid()
    plt.xlabel('Distance (m)')
    plt.ylabel('Distance (m)')
    plt.show()

# Plotting function for loads
def PlotLoads(title):
    # opsv.plot_loads_2d(nep=20, sfac=True, fig_wi_he=(30, 30), fig_lbrt=False, fmt_model_loads={'color': 'black', 'linestyle': 'solid', 'linewidth': 0.8, 'marker': '', 'markersize': 0.7}, node_supports=True, truss_node_offset=0, ax=False)
    opsvis.plot_load(fig_wi_he=(30, 30), sfac=True)
    plt.title(title)
    plt.grid()
    plt.xlabel('Distance (m)')
    # plt.ylabel('Load (N)')
    plt.show()

# Plotting function for deformation shape
def PlotDeformedShape(title):
    opsv.plot_defo()
    plt.title(title)
    plt.grid()
    plt.xlabel('Distance (m)')
    plt.ylabel('deformations (m)')
    plt.show()

# Plotting function for Internal forces
def PlotInternalForces(title, force_type):
    opsv.section_force_diagram_2d(force_type, sfac=0.00001, fig_wi_he=(30, 30), )
    plt.title(title)
    plt.grid()
    plt.xlabel('Distance (m)')
    plt.ylabel('deformations (m)')
    plt.show()

# Plotting function for Internal forces
def PlotReactions(title):
    opsv.plot_reactions(fig_wi_he=(30, 30))
    plt.title(title)
    plt.grid()
    plt.xlabel('Distance (m)')
    plt.ylabel('deformations (m)')
    plt.show()

# Remove any existing model
ops.wipe()

# Initialising the model properties
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Material Properties
E = 21e6  # N/m²
A = 0.15  # m²
Iz = 0.0045  # m⁴
tag = 1  # tag for material

# Defining Geometric transformation for Analysis
ops.geomTransf('Linear', 1)
ops.section('Elastic', tag, E, A, Iz)

# Node data
nodal_data = [[0, 0],
              [0, 3],
              [4, 3],
              [4, 6]]

for i, (x, y) in enumerate(nodal_data):
    ops.node(i + 1, x, y)

for i in range(3):
    ops.element('elasticBeamColumn', i+1, i+1, i+2, A, E, Iz, 1)

# Add supports (optional but useful)
ops.fix(1, 1, 1, 1)  # fully fixed
ops.fix(4, 1, 1, 1)  # fully fixed

# Add time series
ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)

# Apply point load
ops.load(2, 100, 0, 0)
ops.load(3, 0, 0, -50)

# Define system
ops.system("BandGeneral")
ops.numberer('RCM')
ops.constraints('Transformation')
ops.integrator('LoadControl', 1)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

# Now plot the model
PlotStructure('Nodes')
PlotReactions('Reactions')
# PlotLoads('Loads')
# PlotDeformedShape('deformed')
# PlotInternalForces(title='Bending Moment Diagram', force_type='M')
# Request reactions
ops.reactions()

# Displacements at nodes 2 and 3
disp_2 = ops.nodeDisp(2)
disp_3 = ops.nodeDisp(3)

# Reactions at supports 1 and 4
reaction_1 = ops.nodeReaction(1)
reaction_4 = ops.nodeReaction(4)

# Print results
print("Displacement at Node 2:", disp_2)
print("Displacement at Node 3:", disp_3)
print("Reaction at Node 1:", reaction_1)
print("Reaction at Node 4:", reaction_4)