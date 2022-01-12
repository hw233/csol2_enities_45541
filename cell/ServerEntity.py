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
	���entityֻ�����ڷ������ϣ� �ͻ�����û��ʵ��ġ�
	�߻������ڵ�ͼ���������entity��������AI��һЩĻ�����֮�������
	"""
	def __init__( self ):
		"""
		"""
		Monster.Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SERVER_ENTITY )
		self.think( 2.0 )
		
	def calcDynamicProperties( self ):
		"""
		���¼������е�����
		"""
		pass

	def canThink( self ):
		"""
		virtual method.
		�ж��Ƿ����think
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD or self.isDestroyed: 		# ������ֹͣthink
			return False
		return True
		
	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		return csdefine.RELATION_FRIEND
