# Particle effects demo

A scene for each thing a **Particles** object does. Every effect is a
`.effect.json` under `assets/effects`, opened on its own page by
double-clicking it; each emitter in a scene is a Type built on Particles
that names its effect, and any emitter's **Preview** in the Inspector plays
it in the viewport.

Keys **1** to **6** change scene (a Scene Manager in the singleton scene
`scenes/singletons/Demo`); each scene says what it shows and its keys.

| Key | Scene | What it shows |
|---|---|---|
| 1 | A campfire | a four-stop color gradient, size and opacity curves, turbulence, warm up; smoke on a wind that rises and falls over a cycle; a **Burst** of embers where you click |
| 2 | Rain and snow | **collision**: rain bouncing once off a roof and the ground, snow sticking where it lands; **Even** against **Normal** randomness; wind each flake feels its own way |
| 3 | Sparks that hit | **On particle hit** picking the crates the sparks land on; bounce spin and a bounce count; **hitCount** |
| 4 | Magic | a ring shape, outward direction, push and swirl, a Peak size curve; particles carried with the emitter against left in the world |
| 5 | Animated particles | each particle playing the sprite's animation, across its life or at its own pace; a box's edge |
| 6 | A geyser and fireworks | a hand-drawn **rate over time** curve on a repeating cycle; a burst whose speed eases to a stop, with a late fade |

The sprites are drawn by `tools/make-effects-demo.py`, which makes the
whole project from nothing.
