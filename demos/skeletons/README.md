# Skeletons demo

Four characters, each showing off what bones do. Hold the mouse down on one
to change what it does; hold **B** to fade the pictures and see the bones.

- **The dinosaur** walks, and runs while you hold the mouse on it. Its legs,
  arms, head and jaw are rigid pictures on bones; its body with the neck,
  and its tail, are **Mesh Sprites**, single pictures bent by their bones.
  The walk and run are animations whose feet stay flat on the ground while
  planted; holding the mouse **blends** from one to the other.
- **The tree** sways in a breeze. The trunk and branches are one picture
  bent by a branching tree of bones, moved by a **sway motor** at the foot of
  the trunk; each leaf clump hangs on its own bone with a **jiggle motor**.
  Holding the mouse on it raises the motor's amount: the wind gets up.
- **The jellyfish** drifts. Its bell is a Mesh Sprite pulsed by **deform
  keys**, and each tentacle and frilled arm is a Mesh Sprite on a chain of
  bones with a **wave motor**. Holding the mouse on it blends into a faster
  swim.
- **The dapper skeleton** idles, now and then tipping its hat. Every bone is
  a rigid picture, and its elbows have **angle limits**, so they never fold
  back. Holding the mouse on it blends into the Charleston.

Choose a skeleton and open the **Timeline** to see its animations.

Made by `tools/make-skeletons-demo.py` from the drawings in
`tools/skeleton_art`.
