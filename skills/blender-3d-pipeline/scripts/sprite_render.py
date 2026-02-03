#!/usr/bin/env python3
"""
Blender Sprite Rendering Script

Render 3D objects as 2D sprites for use in Godot 2D games.
Run with: blender -b model.blend --python sprite_render.py -- [options]

Examples:
    blender -b character.blend --python sprite_render.py -- --output sprite.png --size 256
    blender -b model.blend --python sprite_render.py -- --output sheet.png --sheet --angles 8
"""

import bpy
import sys
import json
import argparse
import math
from pathlib import Path


def setup_orthographic_camera(distance: float = 10.0) -> bpy.types.Object:
    """Create and position an orthographic camera for sprite rendering."""
    
    # Delete existing cameras
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Create new camera
    cam_data = bpy.data.cameras.new(name='SpriteCamera')
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 2.0  # Adjust based on object size
    
    cam_obj = bpy.data.objects.new(name='SpriteCamera', object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    
    # Position camera
    cam_obj.location = (0, -distance, 0)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    
    # Set as active camera
    bpy.context.scene.camera = cam_obj
    
    return cam_obj


def setup_render_settings(
    resolution: int = 256,
    transparent: bool = True,
    samples: int = 64
):
    """Configure render settings for sprite output."""
    scene = bpy.context.scene
    
    # Resolution
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    
    # Output format
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    
    # Transparency
    scene.render.film_transparent = transparent
    
    # Use Cycles for better quality (fallback to Eevee)
    if 'CYCLES' in [e.bl_idname for e in bpy.types.RenderEngine.__subclasses__()]:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
    else:
        scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'EEVEE_NEXT') else 'BLENDER_EEVEE'


def setup_lighting():
    """Set up basic 3-point lighting for sprite rendering."""
    
    # Remove existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Key light
    key_data = bpy.data.lights.new(name='KeyLight', type='SUN')
    key_data.energy = 3.0
    key_obj = bpy.data.objects.new(name='KeyLight', object_data=key_data)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(45), math.radians(-30), 0)
    
    # Fill light
    fill_data = bpy.data.lights.new(name='FillLight', type='SUN')
    fill_data.energy = 1.0
    fill_obj = bpy.data.objects.new(name='FillLight', object_data=fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(45), math.radians(30), 0)
    
    # Rim light
    rim_data = bpy.data.lights.new(name='RimLight', type='SUN')
    rim_data.energy = 2.0
    rim_obj = bpy.data.objects.new(name='RimLight', object_data=rim_data)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(-30), math.radians(180), 0)


def render_single_sprite(output_path: str, angle: float = 0) -> str:
    """Render a single sprite at the given angle."""
    
    # Rotate all mesh objects
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.rotation_euler.z = math.radians(angle)
    
    # Render
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    return output_path


def render_sprite_sheet(
    output_path: str,
    angles: int = 8,
    columns: int = 4,
    resolution: int = 256
) -> str:
    """Render a sprite sheet with multiple angles."""
    import tempfile
    import os
    
    # Render individual frames
    frames = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(angles):
            angle = (360 / angles) * i
            frame_path = os.path.join(tmpdir, f"frame_{i:03d}.png")
            render_single_sprite(frame_path, angle)
            frames.append(frame_path)
        
        # Combine into sprite sheet using compositor
        rows = math.ceil(angles / columns)
        sheet_width = columns * resolution
        sheet_height = rows * resolution
        
        # Create new image for sprite sheet
        sheet = bpy.data.images.new(
            name="SpriteSheet",
            width=sheet_width,
            height=sheet_height,
            alpha=True
        )
        
        # Load and composite frames
        pixels = [0.0] * (sheet_width * sheet_height * 4)
        
        for i, frame_path in enumerate(frames):
            frame_img = bpy.data.images.load(frame_path)
            frame_pixels = list(frame_img.pixels)
            
            col = i % columns
            row = rows - 1 - (i // columns)  # Flip Y for image coordinates
            
            for y in range(resolution):
                for x in range(resolution):
                    src_idx = (y * resolution + x) * 4
                    dst_x = col * resolution + x
                    dst_y = row * resolution + y
                    dst_idx = (dst_y * sheet_width + dst_x) * 4
                    
                    pixels[dst_idx:dst_idx + 4] = frame_pixels[src_idx:src_idx + 4]
            
            bpy.data.images.remove(frame_img)
        
        sheet.pixels = pixels
        sheet.filepath_raw = output_path
        sheet.file_format = 'PNG'
        sheet.save()
    
    return output_path


def auto_frame_object():
    """Automatically adjust camera to frame the object."""
    # Find bounding box of all mesh objects
    min_coord = [float('inf')] * 3
    max_coord = [float('-inf')] * 3
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for corner in obj.bound_box:
                world_corner = obj.matrix_world @ bpy.types.Object.bl_rna.properties['location'].default.to_3d()
                for i in range(3):
                    world_coord = obj.matrix_world @ corner
                    min_coord[i] = min(min_coord[i], corner[i])
                    max_coord[i] = max(max_coord[i], corner[i])
    
    # Calculate size
    size = max(max_coord[i] - min_coord[i] for i in range(3))
    
    # Adjust camera ortho scale
    if bpy.context.scene.camera:
        cam = bpy.context.scene.camera.data
        cam.ortho_scale = size * 1.5  # Add some padding


def parse_args():
    """Parse command line arguments after '--'."""
    try:
        idx = sys.argv.index('--')
        args = sys.argv[idx + 1:]
    except ValueError:
        args = []

    parser = argparse.ArgumentParser(description='Render sprites from 3D objects')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='Output file path')
    parser.add_argument('--size', type=int, default=256,
                        help='Sprite size in pixels')
    parser.add_argument('--angles', type=int, default=1,
                        help='Number of rotation angles to render')
    parser.add_argument('--sheet', action='store_true',
                        help='Combine angles into a sprite sheet')
    parser.add_argument('--columns', type=int, default=4,
                        help='Columns in sprite sheet')
    parser.add_argument('--samples', type=int, default=64,
                        help='Render samples (quality)')
    parser.add_argument('--no-transparent', action='store_true',
                        help='Disable transparent background')
    parser.add_argument('--no-auto-frame', action='store_true',
                        help='Do not auto-frame the object')
    parser.add_argument('--json', action='store_true',
                        help='Output result as JSON')

    return parser.parse_args(args)


def main():
    args = parse_args()
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Setup scene
    setup_orthographic_camera()
    setup_lighting()
    setup_render_settings(
        resolution=args.size,
        transparent=not args.no_transparent,
        samples=args.samples
    )
    
    if not args.no_auto_frame:
        auto_frame_object()
    
    # Render
    result = {
        'success': True,
        'size': args.size,
        'angles': args.angles,
    }
    
    if args.sheet and args.angles > 1:
        rendered_path = render_sprite_sheet(
            str(output_path),
            angles=args.angles,
            columns=args.columns,
            resolution=args.size
        )
        result['type'] = 'sprite_sheet'
        result['columns'] = args.columns
        result['rows'] = math.ceil(args.angles / args.columns)
    elif args.angles > 1:
        # Render multiple separate files
        rendered_paths = []
        stem = output_path.stem
        suffix = output_path.suffix
        
        for i in range(args.angles):
            angle = (360 / args.angles) * i
            frame_path = str(output_path.parent / f"{stem}_{i:03d}{suffix}")
            render_single_sprite(frame_path, angle)
            rendered_paths.append(frame_path)
        
        result['type'] = 'multiple'
        result['files'] = rendered_paths
        rendered_path = rendered_paths[0]
    else:
        rendered_path = render_single_sprite(str(output_path))
        result['type'] = 'single'
    
    result['output'] = rendered_path
    
    # Output result
    if args.json:
        print(json.dumps(result))
    else:
        print(f"Rendered: {result['output']}")
        print(f"Type: {result['type']}")
        print(f"Size: {args.size}x{args.size}")


if __name__ == '__main__':
    main()
