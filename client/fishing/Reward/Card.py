# -*- coding:gb18030 -*-

import math
from gbref import rds
from ..FishingDataMgr import FishingDataMgr
from ..Elements.Elements import MovableElement
from ..utils.accelerator import linear_accelerate

CARD_2 = 1
CARD_5 = 2
CARD_10 = 3

CARD_SET = {
	CARD_2 : {"model":"gw7241", "scale":2.0, "speed":3},
	CARD_5 : {"model":"gw7241", "scale":3.0, "speed":4},
	CARD_10 : {"model":"gw7241", "scale":4.0, "speed":5},
	}


class Card(MovableElement):

	def __init__(self, type, spaceID, direction, path):
		#card_data = CARD_SET[type]
		card_data = FishingDataMgr.instance().getMultipleCardDataByType(type)
		MovableElement.__init__(self, "NPCObject", spaceID, path[0], direction,
			card_data["model"], card_data["scale"], "card", card_data["speed"], path)

		self._multiple = card_data["multiple"]

	def _initEntity( self, entity ):
		"""初始化entity"""
		MovableElement._initEntity(self, entity)
		self.playAction("play1")

	def scale(self, dstScale, duration, callback=None):
		def scale_inner():
			rds.effectMgr.scaleModel(self._ent.model, dstScale, duration, callback)
		return scale_inner

	def onTick( self, dt ):
		"""Every fishing tick"""
		MovableElement.onTick(self, dt)

		if not self.ready() or self.isDestroyed():
			return

		if self.travelFinished():
			self.destroy()
		else:
			self.updateSpeed(linear_accelerate(self.speed(), 100.0, dt))
