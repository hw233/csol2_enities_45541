# -*- coding: gb18030 -*-
#
# 玩家变身系统	2009-01-10 SongPeifang & LinQing
#

import BigWorld
import GUIFacade
import csstatus
import csdefine
import Const
from gbref import rds
from NPCModelLoader import NPCModelLoader as NPCModel

class RoleChangeBody:
	"""
	玩家变身系统
	"""
	def __init__( self ):
		"""
		"""
		pass

	def canChangeBody( self ):
		"""
		检查玩家是否允许变身
		"""
		return True

	def begin_body_changing( self, modelNumber, modelScale ):
		"""
		玩家变身的接口
		"""
		if not self.canChangeBody():
			return
		# 通知服务器要变成什么
		self.cell.begin_body_changing( modelNumber, modelScale )

	def set_currentModelNumber( self, old = '' ):
		"""
		模型编号发生改变
		"""
		player = BigWorld.player()
		if self.currentModelNumber == "":
			self.createEquipModel()
		else:
			self.createChangeModel()

	def end_body_changing( self, modelNumber ):
		"""
		玩家取消变身的接口
		"""
		player = BigWorld.player()
		if player.id == self.id:
			self.cell.end_body_changing( modelNumber )

	def isFishing( self ):
		"""
		是否是钓鱼
		"""
		return self.currentModelNumber == "fishing"

	def endFishing( self ):
		"""
		取消钓鱼
		"""
		self.end_body_changing( "" )