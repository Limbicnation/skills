# Godot 2D Node Properties Reference

Common properties for 2D nodes used in the `godot-mcp` server.

## Sprite2D

```json
{
  "texture": "res://path/to/texture.png",
  "position": {"x": 100, "y": 200},
  "rotation": 0.0,
  "scale": {"x": 1, "y": 1},
  "flip_h": false,
  "flip_v": false,
  "offset": {"x": 0, "y": 0},
  "centered": true,
  "region_enabled": false,
  "region_rect": {"x": 0, "y": 0, "w": 64, "h": 64}
}
```

## AnimatedSprite2D

```json
{
  "sprite_frames": "res://path/to/frames.tres",
  "animation": "default",
  "autoplay": "idle",
  "playing": true,
  "speed_scale": 1.0,
  "flip_h": false,
  "flip_v": false
}
```

## Area2D

```json
{
  "collision_layer": 1,
  "collision_mask": 1,
  "monitoring": true,
  "monitorable": true,
  "priority": 0
}
```

## CollisionShape2D

```json
{
  "shape": {
    "type": "RectangleShape2D",
    "size": {"x": 32, "y": 32}
  },
  "disabled": false,
  "one_way_collision": false
}
```

### Shape Types

- `RectangleShape2D`: `{"size": {"x": W, "y": H}}`
- `CircleShape2D`: `{"radius": R}`
- `CapsuleShape2D`: `{"radius": R, "height": H}`
- `SegmentShape2D`: `{"a": {"x": X1, "y": Y1}, "b": {"x": X2, "y": Y2}}`

## CharacterBody2D

```json
{
  "motion_mode": 0,
  "up_direction": {"x": 0, "y": -1},
  "floor_stop_on_slope": true,
  "floor_max_angle": 0.785398,
  "collision_layer": 1,
  "collision_mask": 1
}
```

Motion modes: `0` = Grounded, `1` = Floating

## TileMapLayer (Godot 4.3+)

```json
{
  "tile_set": "res://path/to/tileset.tres",
  "cell_quadrant_size": 16,
  "collision_enabled": true,
  "use_kinematic_bodies": false,
  "y_sort_enabled": false
}
```

## Camera2D

```json
{
  "enabled": true,
  "zoom": {"x": 1, "y": 1},
  "offset": {"x": 0, "y": 0},
  "limit_left": -10000000,
  "limit_right": 10000000,
  "limit_top": -10000000,
  "limit_bottom": 10000000,
  "position_smoothing_enabled": false,
  "position_smoothing_speed": 5.0
}
```

## CanvasLayer

```json
{
  "layer": 1,
  "offset": {"x": 0, "y": 0},
  "scale": {"x": 1, "y": 1},
  "follow_viewport_enabled": false
}
```

## ParallaxBackground

```json
{
  "scroll_offset": {"x": 0, "y": 0},
  "scroll_base_offset": {"x": 0, "y": 0},
  "scroll_base_scale": {"x": 1, "y": 1}
}
```

## ParallaxLayer

```json
{
  "motion_scale": {"x": 0.5, "y": 0.5},
  "motion_offset": {"x": 0, "y": 0},
  "motion_mirroring": {"x": 1920, "y": 0}
}
```
