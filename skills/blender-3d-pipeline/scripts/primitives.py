#!/usr/bin/env python3
"""
Blender Primitive Generation Script

Generate 3D primitives with customizable parameters.
Run with: blender --background --python primitives.py -- <shape> [options]

Examples:
    blender --background --python primitives.py -- cube --size 2.0
    blender --background --python primitives.py -- sphere --radius 1.0 --segments 32
    blender --background --python primitives.py -- cylinder --radius 0.5 --depth 2.0
"""

import bpy
import sys
import json
import argparse
from pathlib import Path


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_cube(size: float = 2.0, location: tuple = (0, 0, 0)) -> bpy.types.Object:
    """Create a cube primitive."""
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    return bpy.context.active_object


def create_sphere(
    radius: float = 1.0,
    segments: int = 32,
    rings: int = 16,
    location: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """Create a UV sphere primitive."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        segments=segments,
        ring_count=rings,
        location=location
    )
    return bpy.context.active_object


def create_cylinder(
    radius: float = 1.0,
    depth: float = 2.0,
    vertices: int = 32,
    location: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """Create a cylinder primitive."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        vertices=vertices,
        location=location
    )
    return bpy.context.active_object


def create_cone(
    radius1: float = 1.0,
    radius2: float = 0.0,
    depth: float = 2.0,
    vertices: int = 32,
    location: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """Create a cone primitive."""
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        vertices=vertices,
        location=location
    )
    return bpy.context.active_object


def create_torus(
    major_radius: float = 1.0,
    minor_radius: float = 0.25,
    major_segments: int = 48,
    minor_segments: int = 12,
    location: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """Create a torus primitive."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=major_segments,
        minor_segments=minor_segments,
        location=location
    )
    return bpy.context.active_object


def create_plane(size: float = 2.0, location: tuple = (0, 0, 0)) -> bpy.types.Object:
    """Create a plane primitive."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    return bpy.context.active_object


PRIMITIVES = {
    'cube': create_cube,
    'sphere': create_sphere,
    'cylinder': create_cylinder,
    'cone': create_cone,
    'torus': create_torus,
    'plane': create_plane,
}


def parse_args():
    """Parse command line arguments after '--'."""
    # Find arguments after '--'
    try:
        idx = sys.argv.index('--')
        args = sys.argv[idx + 1:]
    except ValueError:
        args = []

    parser = argparse.ArgumentParser(description='Generate Blender primitives')
    parser.add_argument('shape', choices=PRIMITIVES.keys(), help='Primitive shape to create')
    parser.add_argument('--size', type=float, default=2.0, help='Size (for cube/plane)')
    parser.add_argument('--radius', type=float, default=1.0, help='Radius')
    parser.add_argument('--depth', type=float, default=2.0, help='Depth/height')
    parser.add_argument('--segments', type=int, default=32, help='Number of segments')
    parser.add_argument('--rings', type=int, default=16, help='Number of rings (sphere)')
    parser.add_argument('--vertices', type=int, default=32, help='Number of vertices')
    parser.add_argument('--location', type=str, default='0,0,0', help='Location as x,y,z')
    parser.add_argument('--output', type=str, help='Output .blend file path')
    parser.add_argument('--name', type=str, help='Name for the created object')
    parser.add_argument('--clear', action='store_true', help='Clear scene before creating')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')

    return parser.parse_args(args)


def main():
    args = parse_args()
    
    # Parse location
    location = tuple(float(x) for x in args.location.split(','))
    
    # Clear scene if requested
    if args.clear:
        clear_scene()
    
    # Create the primitive
    shape = args.shape
    obj = None
    
    if shape == 'cube':
        obj = create_cube(size=args.size, location=location)
    elif shape == 'sphere':
        obj = create_sphere(radius=args.radius, segments=args.segments, rings=args.rings, location=location)
    elif shape == 'cylinder':
        obj = create_cylinder(radius=args.radius, depth=args.depth, vertices=args.vertices, location=location)
    elif shape == 'cone':
        obj = create_cone(radius1=args.radius, depth=args.depth, vertices=args.vertices, location=location)
    elif shape == 'torus':
        obj = create_torus(location=location)
    elif shape == 'plane':
        obj = create_plane(size=args.size, location=location)
    
    # Rename if specified
    if args.name and obj:
        obj.name = args.name
    
    # Save if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    
    # Output result
    result = {
        'success': True,
        'object_name': obj.name if obj else None,
        'shape': shape,
        'location': list(location),
        'output_file': args.output
    }
    
    if args.json:
        print(json.dumps(result))
    else:
        print(f"Created {shape}: {obj.name if obj else 'unknown'}")
        if args.output:
            print(f"Saved to: {args.output}")


if __name__ == '__main__':
    main()
