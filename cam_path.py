import os
from pathlib import Path
import bpy
import numpy as np

# === Path Settings ===
prefix = ""
scene_path = f""
output_path = f"{prefix}"
save_scene = False

# === Utility Functions ===

def save_metadata_txt(file_path, metadata_dict):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        for key, value in metadata_dict.items():
            if isinstance(value, (list, np.ndarray)):
                f.write(f"{key}: {np.array2string(np.array(value), separator=', ')}\n")
            else:
                f.write(f"{key}: {value}\n")

def rotation_matrix_to_euler_xyz(R):
    """
    Convert a 3x3 rotation matrix to Euler angles (XYZ order).
    """
    assert R.shape == (3, 3)
    sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
    singular = sy < 1e-6

    if not singular:
        x = np.arctan2(R[2,1], R[2,2])
        y = np.arctan2(-R[2,0], sy)
        z = np.arctan2(R[1,0], R[0,0])
    else:
        x = np.arctan2(-R[1,2], R[1,1])
        y = np.arctan2(-R[2,0], sy)
        z = 0

    return np.array([x, y, z])

# === Load Scene ===
bpy.ops.wm.open_mainfile(filepath=scene_path)

# === Constants ===
radius = 6
centre = np.asarray([-1.22,0.0,0.5])
number_of_angles = 7 
number_of_increments = 1 
number_of_frames = number_of_angles*number_of_increments
initial_angle = -np.pi/6
delta_theta = np.pi/8 
camera_z_initial = 2.6
z_increment = 1.1

# === Render Loop ===
angle = initial_angle
for i in range(number_of_frames):
    core_filename = str(i).zfill(3)
    camera = bpy.context.scene.camera
    camera_z = camera_z_initial + z_increment*np.floor(i/number_of_angles) # when number of angles carried out, increase z 
    angle = angle + delta_theta * (1-2*(((np.floor(i/number_of_angles))%2))) # will go back and forth 

    camera_location = np.array([
        radius * np.cos(angle) + centre[0],
        radius * np.sin(angle) + centre[1],
        camera_z
    ])
    camera.location = camera_location

    # Compute look-at rotation matrix
    if i < 60:
        look_at = np.array([centre[0], centre[1], centre[2]+0.8])
    else:
        look_at = np.array([centre[0], centre[1], centre[2]])
        
    g = (camera_location - look_at)
    g /= np.linalg.norm(g)
    a = np.cross(np.array([0, 0, 1]), g)
    a /= np.linalg.norm(a)
    up = np.cross(g, a)
    up /= np.linalg.norm(up)

    R = np.column_stack((a, up, g))
    euler_xyz = rotation_matrix_to_euler_xyz(R)

    camera.rotation_euler = euler_xyz

    # Save metadata
    metadata_output_path = Path(output_path, f"{core_filename}_metadata.txt")
    metadata_output = {
        'location': camera_location.tolist(),
        'orientation_euler_xyz': euler_xyz.tolist(),
        'orientation_matrix': R.tolist(),
        'focal_length': camera.data.lens,
        'sensor_width': camera.data.sensor_width,
        'resolution_x': bpy.context.scene.render.resolution_x,
        'resolution_y': bpy.context.scene.render.resolution_y
    }
    save_metadata_txt(metadata_output_path, metadata_output)

    bpy.context.view_layer.update()
    render_path = Path(output_path, core_filename)
    image_path = render_path.with_suffix(".png")
    bpy.context.scene.render.filepath = str(image_path)
    if save_scene:
        bpy.ops.wm.save_as_mainfile(filepath=str(render_path.with_suffix(".blend")))
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
    bpy.ops.render.render(write_still=True)
