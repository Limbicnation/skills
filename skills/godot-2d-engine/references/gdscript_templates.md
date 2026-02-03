# GDScript Templates

Common script templates for 2D game development.

## Available Templates

### Player Controllers

| Template | Use Case | Command |
|----------|----------|---------|
| `platformer` | Side-scrolling platformer | `python gdscript_2d.py platformer` |
| `topdown` | Top-down RPG/shooter | `python gdscript_2d.py topdown` |

### Game Objects

| Template | Use Case | Command |
|----------|----------|---------|
| `area2d` | Trigger zone | `python gdscript_2d.py area2d` |
| `collectible` | Pickup item | `python gdscript_2d.py collectible` |
| `projectile` | Bullet/arrow | `python gdscript_2d.py projectile` |
| `enemy_patrol` | Patrolling enemy | `python gdscript_2d.py enemy_patrol` |

### Components

| Template | Use Case | Command |
|----------|----------|---------|
| `health_component` | Health system | `python gdscript_2d.py health_component` |
| `camera_follow` | Smooth camera | `python gdscript_2d.py camera_follow` |
| `state_machine` | State management | `python gdscript_2d.py state_machine` |

## Customization Options

```bash
# Custom speed
python gdscript_2d.py platformer --speed 400.0

# Custom jump
python gdscript_2d.py platformer --jump-velocity -600.0

# Custom group detection
python gdscript_2d.py area2d --group enemy

# Custom signals
python gdscript_2d.py area2d --signals "enemy_entered,enemy_exited"
```
