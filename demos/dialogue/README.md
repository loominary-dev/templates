# Dialogue demo

A conversation with a gate guard, written in `guard.yarn` (the Yarn
language) and shown by rules in a box of the engine's own UI objects: a
portrait, the speaker's name, the line, and a button per choice.

- **On line** puts the speaker and the words in the box; **Continue** goes on.
- **On options** shows a button per choice (**optionCount**, **optionText**),
  and each button's **On pressed** is **Choose option**.
- The file's commands do things in the game: `<<portrait cross>>` plays the
  portrait's animation, `<<give 5>>` adds to the purse.
- The guard remembers: `visited("Guard")` changes his greeting the second
  time, and a choice with `<<if $gold >= 5>>` opens the gate only once you
  have the gold.

Open `guard.yarn` on the Dialogue page to see the nodes as a map and try the
conversation without running the game.

Made by `tools/make-dialogue-demo.py`.
