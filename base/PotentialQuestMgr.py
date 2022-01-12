# -*- coding: gb18030 -*-
#
# Ͷ�����˹����� 2008-12-25 SongPeifang
#
import Love3
import csdefine
import BigWorld
import random
import Math
import time
import cschannel_msgs
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class PotentialQuestMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "PotentialQuestMgr", self._onRegisterManager )
		self._npcs = {}
		
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register PotentialQuestMgr Fail!" )
			self.registerGlobally( "PotentialQuestMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["PotentialQuestMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("PotentialQuestMgr Create Complete!")

	def onRegisterPotentialObject( self, playerDBID, npcBaseMailbox ):
		"""
		define method.
		ע��ĳ����ҽ�Ǳ�������NPC
		"""
		DEBUG_MSG( playerDBID, npcBaseMailbox )
		if playerDBID in self._npcs:
			npc = self._npcs.pop( playerDBID )
			if hasattr( npc, "cell" ) and npc.cell:
				npc.cell.remoteScriptCall( "onDestroySelf", () )
				
		self._npcs[ playerDBID ] = npcBaseMailbox
	
	def onUnRegisterPotentialObject( self, playerDBID ):
		"""
		define method.
		��ע��ĳ����ҽ�Ǳ�������NPC
		"""
		DEBUG_MSG( playerDBID )
		if playerDBID in self._npcs:
			npc = self._npcs.pop( playerDBID )
			if hasattr( npc, "cell" ) and npc.cell:
				npc.cell.remoteScriptCall( "onDestroySelf", () )
