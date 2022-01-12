# -*- coding: gb18030 -*-
# $Id: ServerEntity.py,v 1.11 2009-10-27 03:26:27 kebiao Exp $

import BigWorld
import Monster
from bwdebug import *
import csdefine
import csstatus
from ObjectScripts.GameObjectFactory import g_objFactory

class ServerEntity( Monster.Monster ):
	"""
	这个entity只存在于服务器上， 客户端是没有实体的。
	策划可以在地图上配置这个entity并且配置AI做一些幕后控制之类的事情
	"""
	def __init__( self ):
		"""
		"""
		Monster.Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SERVER_ENTITY )
		self.think( 2.0 )
		
	def calcDynamicProperties( self ):
		"""
		重新计算所有的属性
		"""
		pass

	def canThink( self ):
		"""
		virtual method.
		判定是否可以think
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD or self.isDestroyed: 		# 死亡了停止think
			return False
		return True
		
	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		return csdefine.RELATION_FRIEND
