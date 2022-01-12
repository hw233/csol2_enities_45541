# -*- coding: gb18030 -*-

import re
from SpaceCopySingle import SpaceCopySingle


class SpaceCopyWM(SpaceCopySingle):

	def __init__(self):
		SpaceCopySingle.__init__(self)
		self._revive_space = None
		self._revive_position = None
		self._revive_direction = None

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopySingle.load( self, section )
		self._revive_space = section.readString("revive_space")
		self._revive_position = eval("(%s)" % re.sub(" +", ",", section.readString("revive_position")))
		self._revive_direction = eval("(%s)" % re.sub(" +", ",", section.readString("revive_direction")))

	def emplaceRoleOnLogon(self, role):
		"""
		virtual method.
		玩家登陆时设置正确的安放位置
		@param role: 玩家entity实体
		@type role : Role
		"""
		role.cellData[ "spaceType" ] = self._revive_space
		role.cellData[ "position" ] = self._revive_position
		role.cellData[ "direction" ] = self._revive_direction

		role.logonSpace()
