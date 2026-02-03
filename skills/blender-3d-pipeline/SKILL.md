---
name: blender-3d-pipeline
description: Execute Blender 3D operations for game asset creation. Use when the user needs to generate 3D primitives, apply PBR materials, export glTF/FBX for Godot, or render sprites from 3D objects. Covers procedural modeling, material setup, export optimization, and 3D-to-2D sprite generation workflows.
---

# Blender 3D Asset Pipeline

Automate 3D asset creation in Blender for game development, with optimized export pipelines for Godot Engine.

## Quick Reference

| Task | Script | Example |
|------|--------|---------|
| Create primitive | `primitives.py` | `blender --background -P primitives.py -- cube 2.0` |
| Apply PBR material | `materials.py` | `blender --background -P materials.py -- red_metal` |
| Export glTF | `export.py` | `blender -b scene.blend -P export.py -- /out/model.gltf` |
| Render sprite | `sprite_render.py` | `blender -b model.blend -P sprite_render.py -- /out/sprite.png` |

## Core Operations

### Primitive Generation

```bash
# Create a cube with size 2.0
blender --background --python scripts/primitives.py -- cube --size 2.0 --output /tmp/cube.blend

# Create a UV sphere
blender --background --python scripts/primitives.py -- sphere --radius 1.0 --segments 32

# Create a cylinder
blender --background --python scripts/primitives.py -- cylinder --radius 0.5 --depth 2.0
```

### PBR Material Assignment

```bash
# Apply red metallic material to active object
blender -b model.blend --python scripts/materials.py -- \
  --color 0.8,0.1,0.1 --metallic 0.9 --roughness 0.2

# Apply textured material
blender -b model.blend --python scripts/materials.py -- \
  --albedo /textures/brick_albedo.png \
  --normal /textures/brick_normal.png \
  --roughness-map /textures/brick_roughness.png
```

### Export for Godot

```bash
# Export as glTF 2.0 (recommended for Godot)
blender -b scene.blend --python scripts/export.py -- \
  --format gltf --output /exports/model.gltf

# Export as FBX with Godot-compatible settings
blender -b scene.blend --python scripts/export.py -- \
  --format fbx --output /exports/model.fbx --y-up
```

### Sprite Rendering (3D to 2D)

```bash
# Render orthographic sprite from 3D model
blender -b character.blend --python scripts/sprite_render.py -- \
  --output /sprites/character.png --size 256 --angles 8

# Generate sprite sheet
blender -b character.blend --python scripts/sprite_render.py -- \
  --output /sprites/sheet.png --sheet --columns 4 --rows 2
```

## Integration with Godot

### Recommended Workflow

1. **Create 3D assets** using primitives and procedural modeling
2. **Apply PBR materials** with Godot-compatible settings
3. **Export as glTF** for 3D-in-2D integration
4. **Or render sprites** for pure 2D games

### Export Settings for Godot

- **Format**: glTF 2.0 (`.gltf` or `.glb`)
- **Coordinate System**: +Y up (Godot default)
- **Apply Modifiers**: Yes
- **Materials**: Embed textures or use separate files

## References

- **Export presets**: See [references/godot_export_presets.md](references/godot_export_presets.md)
- **Material templates**: See [references/pbr_templates.md](references/pbr_templates.md)
