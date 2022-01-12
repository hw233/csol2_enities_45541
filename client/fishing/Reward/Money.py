# -*- coding:gb18030 -*-

from ..Elements.Elements import MovableElement
from ..utils import effect
from ..utils.accelerator import linear_accelerate

MOVE_EFFECT_ID = 7

DEFAULT_MODEL = "gw0362_2"
DEFAULT_SCALE = 2
DEFAULT_SPEED = 3

MONEY_SET = {
	"coin":{"model":"gw7238", "scale":1, "speed":8},
	"ingot":{"model":"gw7237", "scale":0.7, "speed":8},
}

class Currency(MovableElement):

	def __init__(self, type, spaceID, direction, path):
		moneyData = MONEY_SET[type]
		MovableElement.__init__(self, "NPCObject", spaceID, path[0], direction,
			moneyData["model"], moneyData["scale"], type, moneyData["speed"], path)
		self._missing = False

	def _initEntity( self, entity ):
		"""初始化entity"""
		MovableElement._initEntity(self, entity)
		effect.applyEffect(entity.model, MOVE_EFFECT_ID)

	def onTick( self, dt ):
		"""Every fishing tick"""
		MovableElement.onTick(self, dt)

		if not self.ready() or self.isDestroyed() or self._missing:
			return

		if self.travelFinished():
			self._missing = True
			self.fadeOut(1.0, self.destroy)
			#self.destroy()
		else:
			self.updateSpeed(linear_accelerate(self.speed(), 150.0, dt))


class Money(Currency):

	def _initEntity( self, entity ):
		"""初始化entity"""
		Currency._initEntity(self, entity)
		self.playAction("play")


class Silver(Currency):

	def _initEntity( self, entity ):
		"""初始化entity"""
		Currency._initEntity(self, entity)
		self.playAction("random")
