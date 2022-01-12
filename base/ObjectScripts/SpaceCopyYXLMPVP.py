# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

class SpaceCopyYXLMPVP( SpaceCopy ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
	
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
		d = { 'dbID' : entity.databaseID }
		d["teamID"] = entity.teamID		# 取得上线时的队伍ID（如果有则值不为0）
		d["spaceKey"] = entity.teamID
		# 注：这里以后可能还需要取队友的dbid，但现在还没决定要怎么做，因此暂时留下注释
		return d