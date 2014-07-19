opensmac
========

Hacked together implementation of smac/smax. 

Early stage. If you're looking for playability come back in a year or so. At pres

running
-------

I use python 2.7 and have no idea if any other version works.

opensmac needs some files from the orignal game, SMAX in particular. As of now
it uses alphax.txt. By default the .txt files need to sit in opensmac/txt
directory and pcx files in opensmac/pcx. This can be changed by editing the
value of `pcx_dir` variable in img.py file. There is `txt_dir` in the txt.py
file as well but as opesmac needs its own compat.txt file in the same directory
so it requires some copying. 

code overview
-------------

**rules.py**

Modules for keeping and accessing original SMAC/SMAX text file data in pythonic form.

**txt.py**

Parsing the original txt files.

**img.py**

Accessing for orignal images.

**state.py**

The root of the game state hierarchy and its manipulation.

**map.py** **square.py** **base.py** **faction.py**

Implementation of game state and logic. I know map methods naming is messy.

**interface.py**

UI implementation, very messy as thats what I'm working on now.

**detailed.py**

Now there's just DetailedInt - a class to keep int value with information where the value comes from.

**main.py**

Main loop, nothing interesting.

**ctrl.py**

Copied from other project, nothing of note.

**render.py**

Copied from other project, was intended for ease of porting to openGL. Might now just be piece of cruft. I'm aware of font sizes issue.

**widget.py**

Widget primitives. I hope to make it standalone lib (LGPL) in the future, time will tell.

**Note**

There are no units yet.

authors
-------

Sadly, I'm alone.

 * Dominik Sidorek <dsidorek@gmail.com>
