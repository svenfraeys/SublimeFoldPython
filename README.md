# Fold Python
#### Intelligent Folding System for Python

![alt tag](https://dl.dropboxusercontent.com/u/1652825/code/sublime/foldpython/foldpython_basics.gif)

## Intro
You can fold, navigate, extend python code in a very fast and easy way.
instant fold all methods, leaving docstrings visible, extending your current code.

## Features
* Folding code, fold and unfold contents where the cursor exists
* Smart selecting, selecting needed pieces of code
* Smart folding getters and setters, getters and setters will be folded as one
* Easy navigation trough code structure : Go upwards in code blocks, go inside children
* Documentation folding, folding all python code except documentation strings
* Extending code, creating new siblings putting keywords correct so Sublime autocomplete can take over the rest

## Installation
* Use [Sublime Package Control](http://wbond.net/sublime_packages/package_control "Sublime Package Control")
* `ctrl+shft+p` then select `Package Control: Install Package`
* install `Fold Python`

Alternatively, download the package from [GitHub](https://github.com/svenfraeys/SublimeFoldPython "SublimeFoldPython") into your `Packages` folder

## Key Bindings
Fold Python is only accesible and useful when used trough shortcuts.

All key bindings are using following pattern `Ctrl+Alt+Shift+Key`

* Ctrl+Alt+Shift+Up : Move up in code / Go to parent
* Ctrl+Alt+Shift+Down : Move down in code / Go to adult
* Ctrl+Alt+Shift+Left : Fold Code / Go to Parent
* Ctrl+Alt+Shift+Right : Unfold Code / Go to Child
* Ctrl+Alt+Shift+PageUp : Go to First Sibling / Go to Parent
* Ctrl+Alt+Shift+PageDown : Go to Last Sibling / Go to next Adult
* Ctrl+Alt+Shift+Home : Go to parent
* Ctrl+Alt+Shift+End : Go to all children
* Ctrl+Alt+Shift+Space : Select all siblings
* Ctrl+Alt+Shift+H : Help mode, Fold content but not docstrings
* Ctrl+Alt+Shift+I : Invert selection, Select all other siblings
* Ctrl+Alt+Shift+0 : Fold to depth 0 starting from selection
* Ctrl+Alt+Shift+1 : Fold to depth 1 starting from selection
* Ctrl+Alt+Shift+2 : Fold to depth 2 starting from selection
* Ctrl+Alt+Shift+N : Create a new sibling starting from selection

## What's new?
25 march 2014
* Folding Getters and Setters as one
* Create new sibling will apply an autocomplete command

## Settings
you can edit Key Binding and Settings in `Preferences > Package Settings > Fold Python` 

* fold_getters_setters : fold getter and matching setter together as one
