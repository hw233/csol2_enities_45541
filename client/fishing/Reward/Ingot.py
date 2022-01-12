# -*- coding:gb18030 -*-

from ..Elements.Elements import MovableElement

DEFAULT_MODEL = "gw0362_2"
DEFAULT_SCALE = 2
DEFAULT_SPEED = 3


class Ingot(MovableElement):

	def __init__(self, spaceID, direction, path):
		MovableElement.__init__(self, "NPCObject", spaceID, path[0], direction,
			DEFAULT_MODEL, DEFAULT_SCALE, "ingot", DEFAULT_SPEED, path)
