This code will position the camera around a central object in Blender, moving in a cylindrical path according to the chosen parameters.
As the camera moves, it will render images and output extrinsic and intrinsic parameters in metadata files, suitable for training NeRFs, Gaussian Splats etc. Outputs can be conveted to 4x4 poses using the scipt within "metadata_to_poses.py"
