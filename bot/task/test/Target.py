# -*- coding: gb18030 -*-

import random
from Position import Position

class Target:

	def __init__(self, name="bot"):
		self.name = name
		self.id = name
		self.targetID = 0
		self.profession = random.choice((16, 32, 48, 64))
		self.position = Position()

	def flySpace(self, spaceLabel, position):
		""""""
		print "%s fly to space %s, %s" % (self.name, spaceLabel, position)

	def moveToPos(self, position):
		""""""
		print "%s move to position %s" % (self.name, position)

	def sendMessage(self, channel, content, target=""):
		""""""
		print "%s send message %s in channel %s, target is %s" %\
			(self.name, content, channel, target)

	def wizCommand(self, strCmd):
		"""
		GM指令
		"""
		print "%s send gm cmd %s." % (self.name, strCmd)

	def entities_nearest_by_class_names(self, class_names):
		return None

	def enemy_nearest_by_class_names(self, class_names):
		return None

	def enemy_nearest(self):
		return None

	def bind_target(self, target):
		self.targetID = target.id
		print "%s bind target to %i" % (self.name, target.id)

	def get_target(self):
		return None

	def spell_target(self, target_id, skill_id):
		print "%s spell kill %d to target %d" % (self.name, skill_id, target_id)

	def getClass(self):
		return self.profession
