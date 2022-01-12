# -*- coding: gb18030 -*-

import math


class Position:

	def __init__(self, *args):
		if len(args) == 1:
			self.value = tuple(args[0])
		elif len(args) == 3:
			self.value = tuple(args)
		else:
			self.value = (0, 0, 0)

	def __str__(self):
		return str(self.value)

	def __repr__(self):
		return "Position%s" % self.__str__()

	def __iter__(self):
		return self.value.__iter__()

	def __len__(self):
		return len(self.value)

	def __eq__(self, other):
		if len(other) != 3:
			return False
		else:
			x, y, z = self.value
			i, j, k = other
			return (x == i) and (y == j) and (z == k)

	def set(self, x, y, z):
		self.value = (x, y, z)

	def distTo(self, other):
		x, y, z = self.value
		i, j, k = other
		return math.sqrt((x - i) ** 2 + (y -j) ** 2 + (z - k) ** 2)
