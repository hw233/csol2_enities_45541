# -*- coding: gb18030 -*-
#

import BigWorld
from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
import Const

GOD_WEAPON_QUEST_XL = 40202003

class SpaceCopyXieLongDongXue( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	а����Ѩ����
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		self.addTimer( 3600, 0, 3600 )		# 3600s�󣬸����Զ��ر�

	def onGodWeaponXL( self ):
		"""
		define method
		�����������
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_XL, 1 )
			
	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			skills = {}
			if self.className in player.mapSkills:
				skills = player.mapSkills[self.className]
			player.client.showPGControlPanel( skills )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.resetAccumPoint()							# ����ֵ��0
			player.removeTemp( "callPGDict" )						# ���ٻ��б����
			player.removeTemp( "pg_formation" )
			player.client.closePGControlPanel()					# �ر��ٻ��ػ�����
			player.removeTemp( "ROLE_CALL_PGNAGUAL_LIMIT" )
	
	def checkSpaceIsFull( self ):
		return SpaceCopyYeWaiInterface.checkSpaceIsFull( self )