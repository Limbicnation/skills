#!/bin/bash
# Blender 3D Pipeline Hello World Test
# This script verifies the Blender skill scripts work correctly

set -e

SCRIPT_DIR="/home/gero/GitHub/DeepLearning_Lab/skills/skills/blender-3d-pipeline/scripts"
OUTPUT_DIR="/tmp/blender_skill_test"

echo "🧊 Blender 3D Pipeline - Hello World Test"
echo "=========================================="

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Test 1: Create a cube primitive
echo ""
echo "📦 Test 1: Creating a red cube..."
blender --background --python "$SCRIPT_DIR/primitives.py" -- cube \
  --size 2.0 \
  --name "TestCube" \
  --clear \
  --output "$OUTPUT_DIR/test_cube.blend" \
  --json

if [ -f "$OUTPUT_DIR/test_cube.blend" ]; then
  echo "✅ Cube created successfully!"
else
  echo "❌ Failed to create cube"
  exit 1
fi

# Test 2: Apply PBR material
echo ""
echo "🎨 Test 2: Applying red metallic material..."
blender -b "$OUTPUT_DIR/test_cube.blend" --python "$SCRIPT_DIR/materials.py" -- \
  --name "RedMetal" \
  --color 0.8,0.1,0.1 \
  --metallic 0.9 \
  --roughness 0.2 \
  --object "TestCube" \
  --output "$OUTPUT_DIR/test_cube_material.blend" \
  --json

if [ -f "$OUTPUT_DIR/test_cube_material.blend" ]; then
  echo "✅ Material applied successfully!"
else
  echo "❌ Failed to apply material"
  exit 1
fi

# Test 3: Export as glTF
echo ""
echo "📤 Test 3: Exporting as glTF for Godot..."
blender -b "$OUTPUT_DIR/test_cube_material.blend" --python "$SCRIPT_DIR/export.py" -- \
  --format gltf \
  --output "$OUTPUT_DIR/test_cube.gltf" \
  --json

if [ -f "$OUTPUT_DIR/test_cube.gltf" ]; then
  echo "✅ glTF export successful!"
else
  echo "❌ Failed to export glTF"
  exit 1
fi

# Test 4: Render sprite
echo ""
echo "🖼️ Test 4: Rendering as 2D sprite..."
blender -b "$OUTPUT_DIR/test_cube_material.blend" --python "$SCRIPT_DIR/sprite_render.py" -- \
  --output "$OUTPUT_DIR/test_sprite.png" \
  --size 256 \
  --samples 16 \
  --json

if [ -f "$OUTPUT_DIR/test_sprite.png" ]; then
  echo "✅ Sprite rendered successfully!"
else
  echo "❌ Failed to render sprite"
  exit 1
fi

echo ""
echo "=========================================="
echo "🎉 All Blender tests passed!"
echo ""
echo "Output files:"
ls -la "$OUTPUT_DIR"
