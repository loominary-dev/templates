# Skeletons demo

Bones, skeletons and what moves them, in one scene.

- **The critter** plays its `idle` animation (keys on its body and head) with
  **motors** on top: its tail **waves**, its ears **jiggle** when its head
  moves. Click and its tail wags fast for two seconds (**Set motor
  duration**), easing in and out (the tail bone's **Motor Ease**), and **On
  motor finished** sets it back to its slow wave.
- **The arm** reaches for the mouse every step with **Aim bone**: two bones,
  the elbow's **Limit Angles** letting it bend one way only, its **Aim Lag**
  making it follow a little behind.
- **The snake** **follows** the mouse: its head's tip goes to the pointer
  and each bone before it trails behind, each joint limited to 45 degrees.
- **The flag** is one picture, a **Mesh Sprite**, bent by three bones; the
  middle one has a wave motor.
- **The blob** has no bones: a **deform** track on its skeleton's
  `breathe` animation eases its points between two shapes.

Choose a skeleton and open the **Timeline** tab to see its animations, turn
on **Onion** to see the poses either side of the playhead, and tick
**Preview motors and IK** in its Inspector to watch the motors while editing.

Made by `tools/make-skeletons-demo.py`.
