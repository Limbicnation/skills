# Godot Export Presets for Blender

Optimized export settings for different Godot use cases.

## glTF 2.0 (Recommended)

### Basic 3D Asset

```bash
blender -b asset.blend --python export.py -- \
  --format gltf \
  --output ./exports/asset.gltf
```

**Settings**: Y-up, apply modifiers, separate textures

### Embedded Asset (GLB)

```bash
blender -b asset.blend --python export.py -- \
  --format glb \
  --output ./exports/asset.glb
```

**Settings**: Single binary file, embedded textures

### Low-Poly Game Asset

```bash
blender -b asset.blend --python export.py -- \
  --format gltf \
  --output ./exports/asset.gltf \
  --draco
```

**Settings**: Draco compression for smaller file size

## FBX (Legacy)

### Character with Animations

```bash
blender -b character.blend --python export.py -- \
  --format fbx \
  --output ./exports/character.fbx
```

**Settings**: Baked animations, Y-up, -Z forward

### Static Prop

```bash
blender -b prop.blend --python export.py -- \
  --format fbx \
  --output ./exports/prop.fbx \
  --no-animations
```

## Godot Import Tips

1. **Coordinate System**: Blender uses Z-up, Godot uses Y-up. Scripts handle conversion automatically.

2. **Materials**: Godot imports Principled BSDF materials correctly. Use:
   - Base Color → Albedo
   - Metallic → Metallic
   - Roughness → Roughness
   - Normal (Non-Color) → Normal Map

3. **Scale**: Export at 1:1 scale. Adjust in Godot's import settings if needed.

4. **Animations**: Use glTF for best animation compatibility with Godot 4.x.
