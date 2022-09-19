#Sources on creating modules: https://docs.python.org/dev/tutorial/modules.html
from .face_tracking import telloGetFrame,findfaceyolo,findfacehaar,findfaceSVM,trackface,initialisetello
from .body_tracking import findpeople, trackbodies
from .keyboardControl import init
from .behaviours import search_for_target, loop_in_a_square, patrol
from .mapping import main

print("Resources imported:\n 1.Face_tracking\n 2.body tracking\n 3.keyboard control\n 4.Autonomous behaviours\n 5.Mapping")