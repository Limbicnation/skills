#!/usr/bin/env python3
"""
Blender Export Script for Godot

Export Blender scenes/objects as glTF or FBX optimized for Godot Engine.
Run with: blender -b scene.blend --python export.py -- [options]

Examples:
    blender -b scene.blend --python export.py -- --format gltf --output /out/model.gltf
    blender -b scene.blend --python export.py -- --format fbx --output /out/model.fbx
"""

import bpy
import sys
import json
import argparse
from pathlib import Path


def export_gltf(
    filepath: str,
    export_selected: bool = False,
    export_materials: str = 'EXPORT',
    export_textures: bool = True,
    use_draco: bool = False,
    export_animations: bool = True,
) -> dict:
    """Export scene as glTF 2.0 optimized for Godot."""
    
    # Ensure directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # Determine format from extension
    if filepath.endswith('.glb'):
        export_format = 'GLB'
    else:
        export_format = 'GLTF_SEPARATE'
    
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format=export_format,
        use_selection=export_selected,
        export_apply=True,  # Apply modifiers
        export_yup=True,     # Godot uses Y-up
        export_texcoords=True,
        export_normals=True,
        export_colors=True,
        export_materials=export_materials,
        export_image_format='AUTO',
        export_draco_mesh_compression_enable=use_draco,
        export_animations=export_animations,
    )
    
    return {
        'format': 'glTF 2.0',
        'filepath': filepath,
        'export_format': export_format,
    }


def export_fbx(
    filepath: str,
    export_selected: bool = False,
    use_mesh_modifiers: bool = True,
    embed_textures: bool = False,
    export_animations: bool = True,
) -> dict:
    """Export scene as FBX optimized for Godot."""
    
    # Ensure directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=export_selected,
        use_mesh_modifiers=use_mesh_modifiers,
        mesh_smooth_type='FACE',
        use_mesh_edges=False,
        use_tspace=True,
        embed_textures=embed_textures,
        path_mode='COPY' if embed_textures else 'AUTO',
        axis_forward='-Z',  # Godot compatibility
        axis_up='Y',        # Godot uses Y-up
        bake_anim=export_animations,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        add_leaf_bones=False,
    )
    
    return {
        'format': 'FBX',
        'filepath': filepath,
    }


def export_obj(
    filepath: str,
    export_selected: bool = False,
    use_mesh_modifiers: bool = True,
) -> dict:
    """Export scene as OBJ (legacy format)."""
    
    # Ensure directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=export_selected,
        apply_modifiers=use_mesh_modifiers,
        export_uv=True,
        export_normals=True,
        export_materials=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
    )
    
    return {
        'format': 'OBJ',
        'filepath': filepath,
    }


def parse_args():
    """Parse command line arguments after '--'."""
    try:
        idx = sys.argv.index('--')
        args = sys.argv[idx + 1:]
    except ValueError:
        args = []

    parser = argparse.ArgumentParser(description='Export Blender assets for Godot')
    parser.add_argument('--format', type=str, default='gltf', 
                        choices=['gltf', 'glb', 'fbx', 'obj'],
                        help='Export format')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='Output file path')
    parser.add_argument('--selected', action='store_true',
                        help='Export only selected objects')
    parser.add_argument('--no-textures', action='store_true',
                        help='Do not export textures')
    parser.add_argument('--draco', action='store_true',
                        help='Use Draco compression (glTF only)')
    parser.add_argument('--embed', action='store_true',
                        help='Embed textures in file (FBX/GLB)')
    parser.add_argument('--no-animations', action='store_true',
                        help='Do not export animations')
    parser.add_argument('--json', action='store_true',
                        help='Output result as JSON')

    return parser.parse_args(args)


def main():
    args = parse_args()
    
    format_type = args.format.lower()
    result = None
    
    # Ensure output has correct extension
    output = args.output
    if format_type in ['gltf', 'glb']:
        if not output.endswith(('.gltf', '.glb')):
            output = output + ('.glb' if format_type == 'glb' else '.gltf')
    elif format_type == 'fbx':
        if not output.endswith('.fbx'):
            output = output + '.fbx'
    elif format_type == 'obj':
        if not output.endswith('.obj'):
            output = output + '.obj'
    
    # Export based on format
    if format_type in ['gltf', 'glb']:
        result = export_gltf(
            filepath=output,
            export_selected=args.selected,
            export_materials='NONE' if args.no_textures else 'EXPORT',
            export_textures=not args.no_textures,
            use_draco=args.draco,
            export_animations=not args.no_animations,
        )
    elif format_type == 'fbx':
        result = export_fbx(
            filepath=output,
            export_selected=args.selected,
            embed_textures=args.embed,
            export_animations=not args.no_animations,
        )
    elif format_type == 'obj':
        result = export_obj(
            filepath=output,
            export_selected=args.selected,
        )
    
    # Add common fields
    if result:
        result['success'] = True
        result['selected_only'] = args.selected
    
    # Output result
    if args.json:
        print(json.dumps(result))
    else:
        print(f"Exported: {result['filepath']}")
        print(f"Format: {result['format']}")


if __name__ == '__main__':
    main()
