opensmac
========

Hacked together implementation of smac/smax. 

Early stage. If you're looking for playability come back in a year or so.

running
-------

I use python 2.7 and have no idea if any other version works.

opensmac needs some files from the orignal game, SMAX in particular. As of now
it uses alphax.txt. By default the .txt files need to sit in opensmac/txt
directory and pcx files in opensmac/pcx. This can be changed by editing the
value of `pcx_dir` variable in img.py file. There is `txt_dir` in the txt.py
file as well but as opesmac needs its own compat.txt file in the same directory
so it requires some copying. 

authors
-------

Sadly, I'm alone.

 * Dominik Sidorek <dsidorek@gmail.com>
