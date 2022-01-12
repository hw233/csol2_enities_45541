# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPrison.py,v 1.2 2008-08-28 00:52:47 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csdefine
import random
import time
import Const
from bwdebug import *
from SpaceMultiLine import SpaceMultiLine
from ObjectScripts.GameObjectFactory import g_objFactory


class SpaceCopyPrison( SpaceMultiLine ):
	"""
	����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceMultiLine.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceMultiLine.load( self, section )
		data = section[ "Space" ][ "NPCPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )

		self.funcNPCData = ( section[ "Space" ][ "NPCClassID" ].asString, pos, direction )

		self.guards = []
		datas = section[ "Space" ][ "GuardData" ]
		for data in datas.values():
			pos 	  = tuple( [ float(x) for x in data[ "position" ].asString.split() ] )
			direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.guards.append( ( data[ "NPCClassID" ].asString, pos, direction ) )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		# ˢ����NPC
		selfEntity.createNPCObject( self.funcNPCData[0], self.funcNPCData[1], self.funcNPCData[2], { "tempMapping" : {} } )

		# ˢ����
		for item in self.guards:
			params = { "spawnPos" : item[1], "tempMapping" : {} }
			selfEntity.createNPCObject( item[0], item[1], item[2], params )

	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		# ֻ��ϵͳץ����ʱ��Ż����������ǣ� �κ�����;�����޷�����
		if not entity.popTemp( "gotoPrison", False ):
			return csstatus.SPACE_MISS_ENTER_PRISON
		return csstatus.SPACE_OK

	def checkDomainLeaveEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		# ֻ��ϵͳץ����ʱ��Ż����������ǣ� �κ�����;�����޷�����
		if not entity.popTemp( "leavePrison", False ):
			return csstatus.SPACE_MISS_LEAVE_PRISON
		return csstatus.SPACE_OK

	def packedMultiLineDomainData( self, entity ):
		"""
		virtual method.
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		return {}

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		return SpaceMultiLine.packedSpaceDataOnEnter( self, entity )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		ʱ�������
		"""
		pass

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceMultiLine.onEnter( self, selfEntity, baseMailbox, params )
		DEBUG_MSG( "%i enter prison params=%s" % ( baseMailbox.id, params ) )
		entity = BigWorld.entities.get( baseMailbox.id )
		entity.endPkValueTimer()
		entity.startPkValueTimer( Const.PK_VALUE_PRISON_LESS_TIME, Const.PK_VALUE_PRISON_LESS_TIME )

		# ��������ӦƵ������
		prison_cant_channels = [
			csdefine.CHAT_CHANNEL_TEAM,						# ����
			csdefine.CHAT_CHANNEL_TONG,						# ���
			csdefine.CHAT_CHANNEL_WORLD,					# ����
			]
		entity.base.chat_lockMyChannels( prison_cant_channels, csdefine.CHAT_FORBID_JAIL, 0 )

		# �����ɫ�Ѿ��������ȸ��������и���������Ѿ�ľ��ǲ��ͱ��ˣ� by ����
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			entity.reviveOnOrigin()

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceMultiLine.onLeave( self, selfEntity, baseMailbox, params )
		DEBUG_MSG( "%i leave prison params=%s" % ( baseMailbox.id, params ) )
		entity = BigWorld.entities.get( baseMailbox.id )
		entity.endPkValueTimer()
		if len( entity.findBuffsByBuffID( 99018 ) ) == 0 and entity.pkValue > 0:
			entity.startPkValueTimer()

		# ����������ӦƵ���Ľ���
		prison_cant_channels = [
			csdefine.CHAT_CHANNEL_TEAM,						# ����
			csdefine.CHAT_CHANNEL_TONG,						# ���
			csdefine.CHAT_CHANNEL_WORLD,					# ����
			]
		entity.base.chat_unlockMyChannels( prison_cant_channels, csdefine.CHAT_FORBID_JAIL )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		pass


