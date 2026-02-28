---
name: godot-2d-engine
description: Create and manage Godot 2D game scenes programmatically. Use when the user needs to set up 2D scenes, configure Sprite2D/Area2D/TileMap nodes, generate GDScript for physics and input handling, or create game logic with signals and groups. Covers complete 2D game development workflows.
---

# Godot 2D Engine Integration

Programmatically manage Godot 2D game development through the existing `godot-mcp` server with specialized 2D capabilities.

## Quick Reference

| Task | Tool | Example |
|------|------|---------|
| Create 2D scene | `create_scene` | `rootNodeType: "Node2D"` |
| Add Sprite2D | `add_node` | `nodeType: "Sprite2D"` |
| Set up Area2D | `add_node` + properties | With collision shape |
| Configure TileMap | `add_node` | `nodeType: "TileMapLayer"` |
| Generate GDScript | `scripts/gdscript_2d.py` | Physics, input, signals |

## 2D Scene Management

### Create a 2D Scene

```json
{
  "tool": "create_scene",
  "arguments": {
    "projectPath": "/path/to/godot/project",
    "scenePath": "res://scenes/game_level.tscn",
    "rootNodeType": "Node2D"
  }
}
```

### Add Sprite2D Node

```json
{
  "tool": "add_node",
  "arguments": {
    "projectPath": "/path/to/godot/project",
    "scenePath": "res://scenes/game_level.tscn",
    "parentNodePath": "root",
    "nodeType": "Sprite2D",
    "nodeName": "Player",
    "properties": {
      "texture": "res://assets/player.png",
      "position": {"x": 100, "y": 200}
    }
  }
}
```

### Add AnimatedSprite2D

```json
{
  "tool": "add_node",
  "arguments": {
    "projectPath": "/path/to/godot/project",
    "scenePath": "res://scenes/game_level.tscn",
    "parentNodePath": "root",
    "nodeType": "AnimatedSprite2D",
    "nodeName": "Enemy",
    "properties": {
      "sprite_frames": "res://resources/enemy_frames.tres"
    }
  }
}
```

### Set Up Area2D with Collision

```json
{
  "tool": "add_node",
  "arguments": {
    "projectPath": "/path/to/godot/project",
    "scenePath": "res://scenes/game_level.tscn",
    "parentNodePath": "root",
    "nodeType": "Area2D",
    "nodeName": "Hitbox",
    "properties": {
      "collision_layer": 2,
      "collision_mask": 1,
      "monitoring": true
    }
  }
}
```

Then add collision shape:

```json
{
  "tool": "add_node",
  "arguments": {
    "projectPath": "/path/to/godot/project",
    "scenePath": "res://scenes/game_level.tscn",
    "parentNodePath": "root/Hitbox",
    "nodeType": "CollisionShape2D",
    "nodeName": "CollisionShape",
    "properties": {
      "shape": {
        "type": "RectangleShape2D",
        "size": {"x": 32, "y": 32}
      }
    }
  }
}
```

### Configure TileMapLayer (Godot 4.3+)

```json
{
  "tool": "add_node",
  "arguments": {
    "projectPath": "/path/to/godot/project",
    "scenePath": "res://scenes/game_level.tscn",
    "parentNodePath": "root",
    "nodeType": "TileMapLayer",
    "nodeName": "Ground",
    "properties": {
      "tile_set": "res://resources/tileset.tres",
      "rendering_quadrant_size": 16
    }
  }
}
```

## GDScript Generation

### Player Controller (Platformer)

```gdscript
extends CharacterBody2D

const SPEED = 300.0
const JUMP_VELOCITY = -400.0

func _physics_process(delta: float) -> void:
    # Gravity
    if not is_on_floor():
        velocity += get_gravity() * delta

    # Jump
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = JUMP_VELOCITY

    # Horizontal movement
    var direction := Input.get_axis("ui_left", "ui_right")
    if direction:
        velocity.x = direction * SPEED
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)

    move_and_slide()
```

### Area2D Trigger

```gdscript
extends Area2D

signal player_entered
signal player_exited

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("player"):
        player_entered.emit()

func _on_body_exited(body: Node2D) -> void:
    if body.is_in_group("player"):
        player_exited.emit()
```

### Top-Down Movement

```gdscript
extends CharacterBody2D

@export var speed: float = 200.0

func _physics_process(_delta: float) -> void:
    var input_direction := Input.get_vector(
        "ui_left", "ui_right", "ui_up", "ui_down"
    )
    velocity = input_direction * speed
    move_and_slide()
```

## Common 2D Patterns

### Layer Management

| Layer | Typical Use |
|-------|-------------|
| 1 | Player |
| 2 | Enemies |
| 3 | Projectiles |
| 4 | Pickups |
| 5 | Environment |

### Signal Connections

```gdscript
# In _ready()
$Area2D.body_entered.connect(_on_area_entered)
$AnimatedSprite2D.animation_finished.connect(_on_animation_done)
$Timer.timeout.connect(_on_timer_timeout)
```

## References

- **GDScript templates**: See [references/gdscript_templates.md](references/gdscript_templates.md)
- **Node properties**: See [references/node_properties.md](references/node_properties.md)
