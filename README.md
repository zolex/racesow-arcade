# Racesow Arcade
Racesow in python


- movement: WSAD
- jump: space
- walljump: left ALT
- shoot: ENTER/RETURN
- switch weapon: left CTRL

## Game Mechanics

### Run

`press right (D)` to run and speed up. at faster speeds, running will slow you down.

### Jump

`press (SPACE)` to jump and gain or at least maintain speed.

`press right (D)` while jumping will help you to maintain speed when jumping to late, but it also limits your acceleration.

- **the closer you are to the ground when pressing jump, the faster you will speed up**. 
- to safely maintain your speed, you can press jump very early and hold it until touching the ground.
- The HUD shows your acceleration for the last jump next to ACC. It also displays if you jumped too early or too late, so you can get a sense of perfect timing

### Wall-Jump

`press (ALT)` when passing a wall to perform a wall-jump. 

Allows crossing larger gaps or gaining upwards speed when [plasma-climbing](#Plasma-Climb)

### Air Control

`press left (A) or right (D)` while mid-air

Allows moving while in the air. Helpful to climb edges, avoid hitting obstacles, or precisely positioning for a [double rocket-jump](#Double-Rocket-Jump)

### Crouch

`press down (S)` to crouch and move under obstacles

### Crouch-Slide

`press down (S) + right (A)` to crouch-slide 

Allows moving under obstacles without losing too much speed.

### Ramp-slide

`press down (S) + right (A)` when on a ramp

Sliding up or down a ramp is faster than running and jumping over ramps.

### Plasma-Climb

`press down (S) and shoot (RETURN)` when in front of a wall

Climb up a wall by using the plasma gun.

*note that it is the direction you are shooting at, so shooting down moves you up*

### Plasma-Slide

`press left (A) or right (D)` while plasma climbing

You can gain speed by shooting left or right while plasma climbing, but it limits the actual climbing. 

*note that it is the direction you are shooting at, so shooting left moves you right and vice versa*

### Rocket-Jump

`press down (S), jump (SPACE) and shoot (RETURN)` while on the ground

- Shooting a rocket under your feed while jumping lets you jump higher.
- Proper timing of the jump and the shot can give you a forward boost instead of just jumping high.

### Double Rocket-Jump

`press down (S) and shoot (RETURN)` while falling, land on the ground and time the second rocket
`press down (S) and shoot (RETURN)` again to have two simultaneous explosions

You can shoot the first rocket and then overtake it while falling, so that you have the time to shoot a second rocket and jump even higher.

*note that the exact position of the explosions will affect how you are boosted. e.g. having the first rocket explode a little behind you and the second directly under you, will boost you more forwards and not just straight upwards*
