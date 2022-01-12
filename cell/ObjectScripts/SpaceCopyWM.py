# -*- coding: gb18030 -*-

import re
from SpaceCopySingle import SpaceCopySingle


class SpaceCopyWM(SpaceCopySingle):

	def __init__(self):
		SpaceCopySingle.__init__(self)

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopySingle.load( self, section )
		self._spaceConfigInfo["revive_space"] = section.readString("revive_space")
		self._spaceConfigInfo["revive_position"] =\
			eval("(%s)" % re.sub(" +", ",", section.readString("revive_position")))
		self._spaceConfigInfo["revive_direction"] =\
			eval("(%s)" % re.sub(" +", ",", section.readString("revive_direction")))

	def onRoleRevive(self, role):
		"""
		玩家在位面复活时调用此接口
		@type	role:	Role Entity
		@param	role:	cell端Role实体
		"""
		space_label = self._spaceConfigInfo["revive_space"]
		position = self._spaceConfigInfo["revive_position"]
		direction = self._spaceConfigInfo["revive_direction"]

		role.reviveOnSpace(space_label, position, direction)

	def telportRoleToEntry(self, role):
		"""
		玩家在位面复活时调用此接口
		@type	role:	Role Entity
		@param	role:	cell端Role实体
		"""
		space_label = self._spaceConfigInfo["revive_space"]
		position = self._spaceConfigInfo["revive_position"]
		direction = self._spaceConfigInfo["revive_direction"]

		role.gotoSpace(space_label, position, direction)
	
	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		pickDict = {}
		pickDict[ "planesID" ] = entity.planesID
		pickDict[ "databaseID" ] = entity.databaseID
		pickDict[ "playerName" ] = entity.playerName
		return pickDict
	
	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopySingle.onLeave( self, selfEntity, baseMailbox, params )
		selfEntity.base.onLeave( baseMailbox, { "planesID":params["planesID"] } )
