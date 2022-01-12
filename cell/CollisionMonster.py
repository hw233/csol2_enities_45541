# -*- coding: gb18030 -*-

"""
碰撞可控类型的怪物
"""


from Monster import Monster


class CollisionMonster( Monster ):
	"""
	CollisionMonster
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		Monster.__init__( self )
