# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

class SpaceCopyTongTurnWar_FS( SpaceCopy ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.left_watchPoint = None
		self.left_fightPoint = None
		self.right_watchPoint = None
		self.ritht_fightPoint = None

	def load( self, section ):
		"""
		从配置中加载数据

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		spaceData = section[ "Space" ]
		
		# 队伍1出场位置
		self.left_watchPoint = eval( spaceData[ "leftTeam_watchPoint" ].asString )
		self.left_fightPoint = eval( spaceData[ "leftTeam_fightPoint" ].asString )
		
		# 队伍2出场位置
		self.right_watchPoint = eval( spaceData[ "rightTeam_watchPoint" ].asString )
		self.right_fightPoint = eval( spaceData[ "rightTeam_fightPoint" ].asString )
		
		# 战败观战区
		self.loser_watchPoint = eval( spaceData[ "loser_watchPoint" ].asString )
		self.centerPoint = eval( spaceData[ "centerPoint" ].asString )
	
	def packedDomainData( self, entity ):
		"""
		virtual method.
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'databaseID' : entity.databaseID, "teamID": entity.teamID, "spaceKey":entity.teamID }
