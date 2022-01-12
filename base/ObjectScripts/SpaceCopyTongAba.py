# -*-coding: gb18030 -*-
#
#
"""
14:38 2008-9-12,by wangshufeng
"""
"""
2010.11
家族擂台移植为帮会擂台 by cxm
"""
import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus

from SpaceCopy import SpaceCopy


class SpaceCopyTongAba( SpaceCopy ):
	"""
	擂台赛副本空间全局实例脚本
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.right_playerEnterPoint = ()	# 擂台赛副本right方进入点
		self.left_playerEnterPoint = ()		# 擂台赛副本left方进入点
		self.right_chapmanPoint = ()		# ( position, direction )，right方商人的位置
		self.left_chapmanPoint = ()			# ( position, direction )，left方商人的位置
		self.left_relivePoints = []			# left方复活点
		self.right_relivePoints = []		# right方复活点
		
		
	def load( self, section ):
		"""
		从配置中加载数据
		
		@type section : PyDataSection
		@param section : python data section load from npc's config file
		"""
		SpaceCopy.load( self, section )
		
		# right方复活点
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.right_playerEnterPoint = ( pos, direction )
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.left_playerEnterPoint = ( pos, direction )
		
		
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
		return { 'tongDBID' : entity.cellData[ "tong_dbID" ] }
		