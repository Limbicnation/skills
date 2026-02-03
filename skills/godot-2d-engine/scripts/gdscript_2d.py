#!/usr/bin/env python3
"""
GDScript 2D Code Generator

Generate GDScript templates for common 2D game patterns.
Run with: python gdscript_2d.py <template> [options]

Examples:
    python gdscript_2d.py platformer --output player.gd
    python gdscript_2d.py area2d --output trigger.gd --signals "player_entered,player_exited"
"""

import argparse
import json
from pathlib import Path

TEMPLATES = {
    "platformer": '''extends CharacterBody2D

const SPEED = {speed}
const JUMP_VELOCITY = {jump_velocity}

func _physics_process(delta: float) -> void:
    # Gravity
    if not is_on_floor():
        velocity += get_gravity() * delta

    # Jump
    if Input.is_action_just_pressed("{jump_action}") and is_on_floor():
        velocity.y = JUMP_VELOCITY

    # Horizontal movement
    var direction := Input.get_axis("{left_action}", "{right_action}")
    if direction:
        velocity.x = direction * SPEED
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)

    move_and_slide()
''',

    "topdown": '''extends CharacterBody2D

@export var speed: float = {speed}

func _physics_process(_delta: float) -> void:
    var input_direction := Input.get_vector(
        "{left_action}", "{right_action}", "{up_action}", "{down_action}"
    )
    velocity = input_direction * speed
    move_and_slide()
''',

    "area2d": '''extends Area2D

{signals}

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("{group}"):
        {enter_signal}.emit()

func _on_body_exited(body: Node2D) -> void:
    if body.is_in_group("{group}"):
        {exit_signal}.emit()
''',

    "collectible": '''extends Area2D

signal collected(value: int)

@export var value: int = 1

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("player"):
        collected.emit(value)
        queue_free()
''',

    "enemy_patrol": '''extends CharacterBody2D

@export var speed: float = {speed}
@export var patrol_distance: float = 100.0

var start_position: Vector2
var direction: int = 1

func _ready() -> void:
    start_position = global_position

func _physics_process(_delta: float) -> void:
    velocity.x = direction * speed
    
    # Reverse at patrol bounds
    if abs(global_position.x - start_position.x) >= patrol_distance:
        direction *= -1
        $Sprite2D.flip_h = direction < 0
    
    move_and_slide()
''',

    "projectile": '''extends Area2D

@export var speed: float = {speed}
@export var damage: int = 1
var direction: Vector2 = Vector2.RIGHT

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    $LifetimeTimer.timeout.connect(queue_free)
    $LifetimeTimer.start()

func _physics_process(delta: float) -> void:
    position += direction * speed * delta

func _on_body_entered(body: Node2D) -> void:
    if body.has_method("take_damage"):
        body.take_damage(damage)
    queue_free()
''',

    "health_component": '''extends Node

signal health_changed(current: int, max_health: int)
signal died

@export var max_health: int = 100
var current_health: int

func _ready() -> void:
    current_health = max_health

func take_damage(amount: int) -> void:
    current_health = max(0, current_health - amount)
    health_changed.emit(current_health, max_health)
    if current_health == 0:
        died.emit()

func heal(amount: int) -> void:
    current_health = min(max_health, current_health + amount)
    health_changed.emit(current_health, max_health)
''',

    "camera_follow": '''extends Camera2D

@export var target: Node2D
@export var smoothing: float = 5.0
@export var offset: Vector2 = Vector2.ZERO

func _process(delta: float) -> void:
    if target:
        global_position = global_position.lerp(
            target.global_position + offset,
            smoothing * delta
        )
''',

    "state_machine": '''extends Node

signal state_changed(new_state: String)

var current_state: String = ""
var states: Dictionary = {{}}

func _ready() -> void:
    # Register states from child nodes
    for child in get_children():
        if child.has_method("enter") and child.has_method("exit"):
            states[child.name] = child
            child.state_machine = self
    
    # Start with first state
    if states.size() > 0:
        change_state(states.keys()[0])

func _physics_process(delta: float) -> void:
    if current_state and states.has(current_state):
        states[current_state].physics_update(delta)

func change_state(new_state: String) -> void:
    if current_state and states.has(current_state):
        states[current_state].exit()
    
    current_state = new_state
    
    if states.has(current_state):
        states[current_state].enter()
        state_changed.emit(current_state)
''',
}


def generate_script(template_name: str, **kwargs) -> str:
    """Generate GDScript from template with given parameters."""
    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
    
    template = TEMPLATES[template_name]
    
    # Default values
    defaults = {
        "speed": "200.0",
        "jump_velocity": "-400.0",
        "jump_action": "ui_accept",
        "left_action": "ui_left",
        "right_action": "ui_right",
        "up_action": "ui_up",
        "down_action": "ui_down",
        "group": "player",
        "signals": "signal player_entered\nsignal player_exited",
        "enter_signal": "player_entered",
        "exit_signal": "player_exited",
    }
    
    # Merge with provided kwargs
    params = {**defaults, **kwargs}
    
    return template.format(**params)


def parse_args():
    parser = argparse.ArgumentParser(description='Generate GDScript for 2D games')
    parser.add_argument('template', choices=TEMPLATES.keys(), help='Template to generate')
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    parser.add_argument('--speed', type=str, default='200.0', help='Movement speed')
    parser.add_argument('--jump-velocity', type=str, default='-400.0', help='Jump velocity')
    parser.add_argument('--group', type=str, default='player', help='Target group name')
    parser.add_argument('--signals', type=str, help='Custom signals (comma-separated)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    kwargs = {
        "speed": args.speed,
        "jump_velocity": args.jump_velocity,
        "group": args.group,
    }
    
    # Parse custom signals
    if args.signals:
        signal_list = args.signals.split(',')
        kwargs["signals"] = '\n'.join(f"signal {s.strip()}" for s in signal_list)
        if len(signal_list) >= 2:
            kwargs["enter_signal"] = signal_list[0].strip()
            kwargs["exit_signal"] = signal_list[1].strip()
    
    # Generate script
    script = generate_script(args.template, **kwargs)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(script)
        
        result = {
            "success": True,
            "template": args.template,
            "output": str(output_path),
        }
        
        if args.json:
            print(json.dumps(result))
        else:
            print(f"Generated: {output_path}")
    else:
        if args.json:
            print(json.dumps({"success": True, "template": args.template, "script": script}))
        else:
            print(script)


if __name__ == '__main__':
    main()
