#!/usr/bin/env python3
"""
STEP File to GLTF Conversion Script

This script helps convert STEP assembly files to individual GLTF/GLB files
for use in Three.js robot visualization.

Requirements:
1. Online STEP to OBJ converter (recommended: CAD Assistant, CloudConvert)
2. Blender for OBJ to GLTF conversion
3. Manual splitting of assembly into individual parts

Workflow:
1. Convert STEP to OBJ online
2. Import OBJ into Blender
3. Separate into individual objects
4. Export each as GLTF/GLB
"""

import os
import subprocess
import json
from pathlib import Path

def create_blender_script():
    """Create a Blender Python script for batch conversion"""
    
    blender_script = '''
import bpy
import os
import bmesh

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Import OBJ file (replace with your actual path)
obj_file = "/home/jonas-petersen/dev/hand-teleop/core/robot_control/stp/SO101_Assembly.obj"
if os.path.exists(obj_file):
    bpy.ops.import_scene.obj(filepath=obj_file)
    
    # Get all mesh objects
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    
    # Export each object as GLB
    output_dir = "/home/jonas-petersen/dev/hand-teleop/frontend/assets/robot_models/so101/"
    
    for i, obj in enumerate(mesh_objects):
        # Select only this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Export as GLB
        output_path = os.path.join(output_dir, f"link_{i:02d}_{obj.name}.glb")
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            use_selection=True,
            export_format='GLB',
            export_materials='EXPORT'
        )
        print(f"Exported: {output_path}")

else:
    print(f"OBJ file not found: {obj_file}")
    print("Please convert STEP to OBJ first")
'''
    
    script_path = "/tmp/blender_convert.py"
    with open(script_path, 'w') as f:
        f.write(blender_script)
    
    return script_path

def main():
    print("🤖 SO-101 STEP to GLTF Conversion Assistant")
    print("=" * 50)
    
    step_file = "/home/jonas-petersen/dev/hand-teleop/core/robot_control/stp/SO101 Assembl v3.stp"
    
    if not os.path.exists(step_file):
        print(f"❌ STEP file not found: {step_file}")
        return
    
    print(f"✅ Found STEP file: {step_file}")
    print()
    
    print("📋 Conversion Steps:")
    print()
    print("1. 🌐 Convert STEP to OBJ online:")
    print("   - Go to: https://www.cloudconvert.com/step-to-obj")
    print("   - Or use: CAD Assistant (free CAD viewer)")
    print("   - Upload your STEP file")
    print("   - Download as OBJ format")
    print("   - Save as: SO101_Assembly.obj in the stp/ folder")
    print()
    
    print("2. 🔧 Run Blender conversion:")
    script_path = create_blender_script()
    print(f"   - Blender script created: {script_path}")
    print("   - Run: blender --background --python /tmp/blender_convert.py")
    print()
    
    print("3. 📁 Expected output:")
    print("   - Individual GLB files in: frontend/assets/robot_models/so101/")
    print("   - Files will be named: link_00_*.glb, link_01_*.glb, etc.")
    print()
    
    print("4. 🏷️ Map to URDF links:")
    print("   You'll need to identify which GLB corresponds to:")
    print("   - base_link")
    print("   - link_1 (shoulder)")
    print("   - link_2 (upper_arm)")  
    print("   - link_3 (forearm)")
    print("   - link_4 (wrist_1)")
    print("   - link_5 (wrist_2)")
    print("   - link_6 (wrist_3)")
    print("   - gripper_link")
    print()
    
    print("5. 🔄 Update Three.js code to load real meshes")
    print()
    
    print("Alternative: Use existing robot models")
    print("- UR5/UR10 (Universal Robots) - widely available")
    print("- Franka Panda - research-friendly")
    print("- Kuka IIWA - industrial standard")

if __name__ == "__main__":
    main()
