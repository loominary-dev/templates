# Menus demo

Three screens built from the engine's own UI objects — **Panel**, **Label**,
**Button**, **Checkbox** and **Slider** — placed under a screen-fixed
**Layer** so they sit on the view whatever the camera does, and driven by
rules on each scene's root Type:

- **Title**: Play, Options and Quit. Tab, the arrows or a pad's D-pad move the
  focus; Enter, Space or the pad's bottom button press.
- **Options**: a volume slider whose value a label follows, a checkbox that
  rumbles the pad, and a rebind row per command — *Change* listens for the
  next input, *An input was captured* binds it and saves the controls, and the
  labels show each command's first binding.
- **Game**: a block that walks and jumps; P or Start opens a pause menu
  over it, with Resume, Options and the title screen.

Made by `tools/make-menus-demo.py`.
