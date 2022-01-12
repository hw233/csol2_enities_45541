# -*- coding: gb18030 -*-

from Monster import Monster
import csdefine
from gbref import rds

class ConvoyMonster( Monster ):
	def __init__( self ):
		Monster.__init__( self )



	def queryRelation( self, entity ):
		"""
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		return csdefine.RELATION_NOFIGHT


	def handleMouseShape( self ):
		"""
		处理鼠标动画
		"""
		rds.ccursor.set( "normal" )