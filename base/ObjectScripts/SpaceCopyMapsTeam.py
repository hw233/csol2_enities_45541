# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceCopyMaps import SpaceCopyMaps

class SpaceCopyMapsTeam( SpaceCopyMaps ):
	"""
	多地图组队副本脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyMaps.__init__( self )

	def packedDomainData( self, entity ):
		"""
		virtual method.
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		d = SpaceCopyMaps.packedDomainData( self, entity )
		d["teamID"] = entity.teamID
		return d