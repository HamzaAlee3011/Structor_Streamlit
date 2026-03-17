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
    opsvis.plot_load(fig_wi_he=(30, 30), sfac=1)
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
E = 29000  # N/m²
A = 100  # m²
Iz = 600  # m⁴
tag = 1  # tag for material

# Defining Geometric transformation for Analysis
ops.geomTransf('Linear', 1)
ops.section('Elastic', 1, E*144, A/(12**2), Iz/(12**4))
ops.section('Elastic', 2, E*144, A/(12**2), 2*Iz/(12**4))

# Node data
nodal_data = [[0, 0],
              [0, 5],
              [0, 10],
              [12, 10],
              [12, 0]]

for i, (x, y) in enumerate(nodal_data):
    ops.node(i + 1, x, y)


ops.element('elasticBeamColumn', 1, 1, 2,  2, 1)
ops.element('elasticBeamColumn', 2, 2, 3,  2, 1)
ops.element('elasticBeamColumn', 3, 3, 4,  1, 1)
ops.element('elasticBeamColumn', 4, 4, 5,  2, 1)

# Add supports (optional but useful)
ops.fix(1, 1, 1, 0)  # fully fixed
ops.fix(5, 1, 1, 1)  # fully fixed

# Add time series
ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)

# Apply point load and point moment
ops.eleLoad('-ele', 3, '-type', '-beamUniform', -20)
# ops.eleLoad('-ele', 1, '-type', '-beamPoint', -200, 0.5)
# ops.eleLoad('-ele', 4, '-type', '-beamNonuniform', -10, -50)  # N/m
ops.load(2, 200, 0, 0)
# ops.load(3, 0, 0, -50)


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
PlotLoads('Loads')
# PlotReactions('Reactions')
PlotDeformedShape('deformed')
# PlotInternalForces(title='Bending Moment Diagram', force_type='M')
# Request reactions
ops.reactions()

# Displacements at nodes 2 and 3
disp_2 = ops.nodeDisp(3)
disp_3 = ops.nodeDisp(4)

# Reactions at supports 1 and 4
reaction_1 = ops.nodeReaction(1)
reaction_4 = ops.nodeReaction(5)

# Print results
print("Displacement at Node 2:", *map(lambda x: x*12, disp_2))
print("Displacement at Node 3:", *map(lambda x: x*12, disp_3))
print("Reaction at Node 1:", reaction_1)
print("Reaction at Node 4:", reaction_4)