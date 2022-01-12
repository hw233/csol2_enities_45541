# -*- coding: gb18030 -*-
#
# $Id: Monster_Potential.py,v 1.5 2008-04-15 06:19:17 kebiao Exp $

"""
����NPC����
"""
import BigWorld
from Monster import Monster
from bwdebug import *
import csconst
import csdefine

class MonsterPotentialMeleeBoss(Monster):
	"""
	Ǳ���Ҷ�����NPC��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		Monster.onLoadEntityProperties_( self, section )
		
	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ����selfEntity��die()������ʱ������
		"""
		spaceBase = selfEntity.queryTemp( "space", None )
		spaceEntity = None
		
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			
		try:
			killer = BigWorld.entities[ killerID ]
		except KeyError:
			DEBUG_MSG( "not find the Entity! %i" % killerID )
			killer = None
			
		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onMeleeDie( spaceEntity, killer, tuple( selfEntity.spawnPos ) )
		elif spaceBase:
			spaceBase.cell.remoteScriptCall( "onMeleeDie", ( killer, tuple( selfEntity.spawnPos ), ) )

#
# $Log: not supported by cvs2svn $
#
#
