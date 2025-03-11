import gmsh
import numpy as np

# data
x_c = 587  # cm
y_c = 60  # cm
z_c = 100  # cm

epoxy_thickness = 1.905  # before was 2.54 cm = 1 inch
alumina_compressed_thickness = 2.54  # 1 inch
base_thickness = 0.786
alumina_thickness = 0.635
he_thickness = 0.6
inconel_thickness = 0.3
heater_gap = 0.878
cllif_thickness = 6.388 + 0.13022  # without heater: 0.1081
gap_thickness = 4.605
cap = 1.422
firebrick_thickness = 15.24
high = 21.093
cover = 2.392
z_tab = 28.00
lead_height = 4.00
lead_width = 8.00
lead_length = 16.00
heater_r = 0.439
heater_h = 25.40
heater_z = (
    epoxy_thickness
    + alumina_compressed_thickness
    + base_thickness
    + alumina_thickness
    + he_thickness
    + inconel_thickness
    + heater_gap
    + z_c
)
cllif_z = (
    epoxy_thickness
    + alumina_compressed_thickness
    + base_thickness
    + alumina_thickness
    + he_thickness
    + inconel_thickness
    + cllif_thickness
    + z_c
)

z_new = cllif_z - cllif_thickness
heater_r = 0.439
cllif_radius = 7.00

# Initialize Gmsh
gmsh.initialize()
gmsh.model.add("holed_cylinder")

# Define main cylinder parameters
main_radius = cllif_radius  # cm
main_height = cllif_thickness  # cm

# Define inner cutting cylinder (the hole)
# hole_radius = heater_r  # cm
# hole_height = cllif_z - heater_z  # Must be at least equal to main_height

hole_radius = heater_r  # cm
hole_height = cllif_z - heater_z  # Must be at least equal to main_height

# Create the main cylinder (tag = 1)
main_cylinder = gmsh.model.occ.addCylinder(
    x_c, y_c, z_new, 0, 0, main_height, main_radius
)

# Create the hole cylinder (tag = 2), making sure it goes all the way through
hole_cylinder = gmsh.model.occ.addCylinder(
    x_c, y_c, cllif_z, 0, 0, -hole_height, hole_radius
)

# Perform the boolean subtraction (main_cylinder - hole_cylinder)
cut_result = gmsh.model.occ.cut([(3, main_cylinder)], [(3, hole_cylinder)])

# Synchronize to apply changes
gmsh.model.occ.synchronize()


print(gmsh.model.getEntities(dim=2))
# Identify surface tags
# Note: You may need to inspect your geometry to determine the correct tags
# For demonstration, let's assume:
inner_surface_tag = 4  # Replace with actual tag of the inner surface
outer_surface_tag = 5  # Replace with actual tag of the outer surface
bottom_surface_tag = 6  # Replace with actual tag of the bottom surface
# Define mesh sizes
inner_mesh_size = 0.2  # Finer mesh on the inner surface
outer_mesh_size = 2.0  # Coarser mesh on the outer surface
bottom_mesh_size = 0.5  # Coarser mesh on the bottom surface

# Create mesh size fields
inner_field = gmsh.model.mesh.field.add("Constant")
gmsh.model.mesh.field.setNumber(inner_field, "VIn", inner_mesh_size)
gmsh.model.mesh.field.setNumbers(inner_field, "SurfacesList", [inner_surface_tag])

outer_field = gmsh.model.mesh.field.add("Constant")
gmsh.model.mesh.field.setNumber(outer_field, "VIn", outer_mesh_size)
gmsh.model.mesh.field.setNumbers(outer_field, "SurfacesList", [outer_surface_tag])

bottom_field = gmsh.model.mesh.field.add("Constant")
gmsh.model.mesh.field.setNumber(bottom_field, "VIn", bottom_mesh_size)
gmsh.model.mesh.field.setNumbers(bottom_field, "SurfacesList", [bottom_surface_tag])

# Combine fields
min_field = gmsh.model.mesh.field.add("Min")
gmsh.model.mesh.field.setNumbers(
    min_field, "FieldsList", [inner_field, outer_field, bottom_field]
)

# Set the background mesh field
gmsh.model.mesh.field.setAsBackgroundMesh(min_field)

# # Set global mesh refinement (smaller values → finer mesh)
# gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 1)  # Minimum element size
# gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 10)  # Maximum element size

# # Apply fine mesh locally to all points (optional)
# gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 0.3)

# Check that the cut operation was successful
if cut_result:
    remaining_volume = cut_result[0][0][1]  # Get the tag of the remaining volume
    print(f"Remaining volume tag: {remaining_volume}")

    # Remove any duplicate objects
    gmsh.model.occ.remove_all_duplicates()

    # Generate the 3D mesh only for the final shape
    gmsh.model.mesh.generate(3)
else:
    print("Boolean subtraction failed!")

# Save the mesh in Gmsh format
gmsh.write("baby.msh")
gmsh.write("baby.vtk")  # Save also in VTK format

# Open Gmsh GUI to visualize the mesh (optional)
gmsh.fltk.run()


print("Mesh successfully created and converted to VTK for ParaView.")

# Print all cell types in the mesh
element_types = gmsh.model.mesh.getElementTypes()
print("Element types in the mesh:")
for elem_type in element_types:
    print(
        f"Element type: {elem_type}, Name: {gmsh.model.mesh.getElementProperties(elem_type)[0]}"
    )
# Finalize Gmsh
gmsh.finalize()
