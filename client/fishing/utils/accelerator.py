# -*- coding: gb18030 -*-

import BigWorld
import weakref


class LinearAccelerator:

	def __init__(self, owner, acceleration):
		self._wref_owner = weakref.ref(owner)
		self._acceleration = acceleration
		self._active = False

	def active(self, active):
		self._active = active

	def onTick(self, dt):
		if not self._active:
			return

		owner = self._wref_owner()
		if owner is None:
			return

		v0 = owner.speed()
		vt = linear_accelerate(v0, self._acceleration, dt)
		owner.updateSpeed(vt)


def linear_accelerate(v0, a, t):
	"""calculate speed after accelerated by a of t seconds."""
	return v0 + a * t ** 2
