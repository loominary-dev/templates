# Controls scene

A screen where the player rebinds the controls, ready to import into any
game: **Scene ▸ Import a scene…** in the editor, then open a way to it (a
button on your title screen whose rule changes the scene to `Controls`).

What it holds, as Object Types the game can restyle:

- **ControlsList**, on the engine's **RebindList**: a row per input command
  of the game it is in, read from the project's own table when the scene
  starts — the command's name, the inputs it has, **Change** (listen for the
  next input and put it in the old one's place) and **Add** (keep the old
  one too). A change is saved for next time; **Reset the controls** at the
  bottom goes back to the project's own table.
- **ControlsScreen**, a screen-fixed Layer, so the screen sits on the view
  whatever the camera does; **ControlsHeading** and **ControlsHelp**, Labels;
  **ControlsBack**, a Button whose rule changes to the scene that opened
  this one (`previousScene`), and **ControlsScenes**, the Scene Manager
  that rule uses, in a singleton scene.

Made by `tools/make-rebind-scene.py`.
