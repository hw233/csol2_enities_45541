# -*- coding: gb18030 -*-
# MonsterTrap.py
# 可以攻击的陷阱

from Monster import Monster

class MonsterTrap( Monster ):
	"""
	可以攻击的陷阱
	"""
	def __init__(self):
		Monster.__init__(self)
