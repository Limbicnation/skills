#!/usr/bin/env python3
"""
Blender PBR Material Assignment Script

Apply PBR materials to objects using Principled BSDF.
Run with: blender -b model.blend --python materials.py -- [options]

Examples:
    blender -b model.blend --python materials.py -- --color 0.8,0.1,0.1 --metallic 0.9
    blender -b model.blend --python materials.py -- --albedo /path/to/albedo.png
"""

import bpy
import sys
import json
import argparse
from pathlib import Path


def create_principled_material(
    name: str = "PBR_Material",
    base_color: tuple = (0.8, 0.8, 0.8, 1.0),
    metallic: float = 0.0,
    roughness: float = 0.5,
    specular: float = 0.5,
    emission_color: tuple = (0.0, 0.0, 0.0, 1.0),
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    """Create a new PBR material with Principled BSDF."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Get the Principled BSDF node
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    
    if principled:
        principled.inputs["Base Color"].default_value = base_color
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
        # Specular is deprecated in Blender 4.0+, use IOR instead
        if "Specular IOR Level" in principled.inputs:
            principled.inputs["Specular IOR Level"].default_value = specular
        elif "Specular" in principled.inputs:
            principled.inputs["Specular"].default_value = specular
        
        # Emission
        if emission_strength > 0:
            if "Emission Color" in principled.inputs:
                principled.inputs["Emission Color"].default_value = emission_color
            principled.inputs["Emission Strength"].default_value = emission_strength
    
    return mat


def add_texture_node(
    mat: bpy.types.Material,
    image_path: str,
    input_name: str,
    color_space: str = "sRGB"
) -> bpy.types.ShaderNodeTexImage:
    """Add a texture node and connect it to the Principled BSDF."""
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    
    if not principled:
        return None
    
    # Create image texture node
    tex_node = nodes.new(type="ShaderNodeTexImage")
    tex_node.location = (-400, nodes.get("Principled BSDF").location.y)
    
    # Load image
    try:
        img = bpy.data.images.load(image_path)
        img.colorspace_settings.name = color_space
        tex_node.image = img
    except Exception as e:
        print(f"Error loading texture: {e}")
        return None
    
    # Connect to appropriate input
    if input_name in principled.inputs:
        if input_name == "Normal":
            # Need a normal map node
            normal_node = nodes.new(type="ShaderNodeNormalMap")
            normal_node.location = (-200, tex_node.location.y - 200)
            links.new(tex_node.outputs["Color"], normal_node.inputs["Color"])
            links.new(normal_node.outputs["Normal"], principled.inputs["Normal"])
        else:
            links.new(tex_node.outputs["Color"], principled.inputs[input_name])
    
    return tex_node


def apply_material_to_object(obj: bpy.types.Object, mat: bpy.types.Material):
    """Apply material to an object."""
    if obj.type != 'MESH':
        return False
    
    # Clear existing materials
    obj.data.materials.clear()
    
    # Add new material
    obj.data.materials.append(mat)
    return True


def parse_args():
    """Parse command line arguments after '--'."""
    try:
        idx = sys.argv.index('--')
        args = sys.argv[idx + 1:]
    except ValueError:
        args = []

    parser = argparse.ArgumentParser(description='Apply PBR materials in Blender')
    parser.add_argument('--name', type=str, default='PBR_Material', help='Material name')
    parser.add_argument('--color', type=str, default='0.8,0.8,0.8', help='Base color as R,G,B (0-1)')
    parser.add_argument('--metallic', type=float, default=0.0, help='Metallic value (0-1)')
    parser.add_argument('--roughness', type=float, default=0.5, help='Roughness value (0-1)')
    parser.add_argument('--specular', type=float, default=0.5, help='Specular/IOR level (0-1)')
    parser.add_argument('--emission-color', type=str, help='Emission color as R,G,B')
    parser.add_argument('--emission-strength', type=float, default=0.0, help='Emission strength')
    parser.add_argument('--albedo', type=str, help='Path to albedo/diffuse texture')
    parser.add_argument('--normal', type=str, help='Path to normal map texture')
    parser.add_argument('--roughness-map', type=str, help='Path to roughness texture')
    parser.add_argument('--metallic-map', type=str, help='Path to metallic texture')
    parser.add_argument('--object', type=str, help='Object name to apply material (default: active)')
    parser.add_argument('--all-selected', action='store_true', help='Apply to all selected objects')
    parser.add_argument('--output', type=str, help='Output .blend file path')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')

    return parser.parse_args(args)


def main():
    args = parse_args()
    
    # Parse color
    color = tuple(float(x) for x in args.color.split(',')) + (1.0,)
    
    # Parse emission color if provided
    emission_color = (0.0, 0.0, 0.0, 1.0)
    if args.emission_color:
        emission_color = tuple(float(x) for x in args.emission_color.split(',')) + (1.0,)
    
    # Create material
    mat = create_principled_material(
        name=args.name,
        base_color=color,
        metallic=args.metallic,
        roughness=args.roughness,
        specular=args.specular,
        emission_color=emission_color,
        emission_strength=args.emission_strength,
    )
    
    # Add textures if provided
    textures_added = []
    if args.albedo:
        add_texture_node(mat, args.albedo, "Base Color", "sRGB")
        textures_added.append("albedo")
    if args.normal:
        add_texture_node(mat, args.normal, "Normal", "Non-Color")
        textures_added.append("normal")
    if args.roughness_map:
        add_texture_node(mat, args.roughness_map, "Roughness", "Non-Color")
        textures_added.append("roughness")
    if args.metallic_map:
        add_texture_node(mat, args.metallic_map, "Metallic", "Non-Color")
        textures_added.append("metallic")
    
    # Apply to objects
    objects_applied = []
    
    if args.all_selected:
        for obj in bpy.context.selected_objects:
            if apply_material_to_object(obj, mat):
                objects_applied.append(obj.name)
    elif args.object:
        obj = bpy.data.objects.get(args.object)
        if obj and apply_material_to_object(obj, mat):
            objects_applied.append(obj.name)
    elif bpy.context.active_object:
        obj = bpy.context.active_object
        if apply_material_to_object(obj, mat):
            objects_applied.append(obj.name)
    
    # Save if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    
    # Output result
    result = {
        'success': True,
        'material_name': mat.name,
        'textures': textures_added,
        'objects_applied': objects_applied,
        'output_file': args.output
    }
    
    if args.json:
        print(json.dumps(result))
    else:
        print(f"Created material: {mat.name}")
        if textures_added:
            print(f"Textures: {', '.join(textures_added)}")
        if objects_applied:
            print(f"Applied to: {', '.join(objects_applied)}")
        if args.output:
            print(f"Saved to: {args.output}")


if __name__ == '__main__':
    main()
