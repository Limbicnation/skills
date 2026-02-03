#!/bin/bash
# Godot 2D Engine Hello World Test
# This script verifies the GDScript generator works correctly

set -e

SCRIPT_DIR="/home/gero/GitHub/DeepLearning_Lab/skills/skills/godot-2d-engine/scripts"
OUTPUT_DIR="/tmp/godot_skill_test"

echo "🎮 Godot 2D Engine - Hello World Test"
echo "======================================"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Test 1: Generate platformer script
echo ""
echo "🏃 Test 1: Generating platformer controller..."
python3 "$SCRIPT_DIR/gdscript_2d.py" platformer \
  --speed 300.0 \
  --jump-velocity -450.0 \
  --output "$OUTPUT_DIR/player_controller.gd"

if [ -f "$OUTPUT_DIR/player_controller.gd" ]; then
  echo "✅ Platformer script generated!"
  echo "   Preview:"
  head -15 "$OUTPUT_DIR/player_controller.gd"
else
  echo "❌ Failed to generate platformer script"
  exit 1
fi

# Test 2: Generate Area2D trigger
echo ""
echo "🎯 Test 2: Generating Area2D trigger..."
python3 "$SCRIPT_DIR/gdscript_2d.py" area2d \
  --group "player" \
  --signals "zone_entered,zone_exited" \
  --output "$OUTPUT_DIR/trigger_zone.gd"

if [ -f "$OUTPUT_DIR/trigger_zone.gd" ]; then
  echo "✅ Area2D script generated!"
else
  echo "❌ Failed to generate Area2D script"
  exit 1
fi

# Test 3: Generate collectible
echo ""
echo "💎 Test 3: Generating collectible item..."
python3 "$SCRIPT_DIR/gdscript_2d.py" collectible \
  --output "$OUTPUT_DIR/coin.gd"

if [ -f "$OUTPUT_DIR/coin.gd" ]; then
  echo "✅ Collectible script generated!"
else
  echo "❌ Failed to generate collectible script"
  exit 1
fi

# Test 4: Generate enemy patrol
echo ""
echo "👾 Test 4: Generating enemy patrol..."
python3 "$SCRIPT_DIR/gdscript_2d.py" enemy_patrol \
  --speed 100.0 \
  --output "$OUTPUT_DIR/enemy.gd"

if [ -f "$OUTPUT_DIR/enemy.gd" ]; then
  echo "✅ Enemy patrol script generated!"
else
  echo "❌ Failed to generate enemy patrol script"
  exit 1
fi

# Test 5: Generate health component
echo ""
echo "❤️ Test 5: Generating health component..."
python3 "$SCRIPT_DIR/gdscript_2d.py" health_component \
  --output "$OUTPUT_DIR/health_component.gd"

if [ -f "$OUTPUT_DIR/health_component.gd" ]; then
  echo "✅ Health component generated!"
else
  echo "❌ Failed to generate health component"
  exit 1
fi

echo ""
echo "======================================"
echo "🎉 All Godot 2D tests passed!"
echo ""
echo "Generated scripts:"
ls -la "$OUTPUT_DIR"
