# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
��׼������Ҳ������Ϊ��������
"""

import BigWorld
import Language
from bwdebug import *
import time
import Const
import csstatus
import csdefine
import csconst
from SpaceCopy import SpaceCopy

SPACE_LAST_TIME  = 15*60

class SpaceCopyTongTerritory( SpaceCopy ):
	"""
	������
	@ivar domainMB:			һ�����������ԣ���¼����������ռ�mailbox������ĳЩ��Ҫ֪ͨ������ռ�Ĳ������˽ӿ����ΪNone���ʾ��ǰ����ʹ��
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.setTemp( "playerDatas", {} )
		
		self._isRobWarOn = False # ����Ӷ�ս�Ƿ����ڽ��еı�־
		self._enemyTongDBID = 0 # ����Ӷ�ս�еж԰���DBID
		
		# ���б���Ϊһ��self._players�����䣬��Ϊ�����ṩ����Ϣ̫���ޣ����ڰ����������и��ֻ�Ĺ����ռ�
		# ��Ӧ��Ҫ�Ƚ���ϸ�������Ϣ�����������������ֲ�ͬ�Ļ�������ض������̣�������б�����һ���ֵ䣬
		# ���ڱ���ÿ����ҵĸ�����Ϣ�����԰��趯̬��Ӹ�����Ϣ����Ҫ����ĳ��ͳ����Ϣʱ��ο�registerPlayer��
		# ��ʵ�֡� by mushuang
		self._detailedPlayerInfo = [] #[ { ���1����Ϣ },{ ���2����Ϣ }, ... ] 

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		self.queryTemp( "playerDatas" )[ baseMailbox.id ] = ( params[ "tongDBID" ], baseMailbox )
		SpaceCopy.onEnter( self, baseMailbox, params )
		
		## ����ڰ���Ӷ�ս���ڼ䣬�Զ�����ҵ�PKģʽ��Ϊ�����ģʽ�� �μ��� CSOL-9842
		playerTongDBID = params.get( "tongDBID", None )
		if not playerTongDBID:
			ERROR_MSG( "Can't find player tongDBID in params!" )
			return
		self.__setRobWarPkMode( playerTongDBID, baseMailbox )
		
	def __setRobWarPkMode( self, playerTongDBID, baseMailbox ):
		"""
		����ʵ������趨������Ӷ�ս�е�PKģʽ
		"""
		# if �����Ӷ�ս�� then return
		if not self._isRobWarOn: return
		
		
		spaceTongDBID = self.params.get( "tongDBID", None )
		if spaceTongDBID == None :
			ERROR_MSG( "Can't find space tongDBID in self.params!" )
			return
		
		# if ������Լ��� ���� ����ǵж԰�����
		if playerTongDBID == spaceTongDBID or playerTongDBID == self._enemyTongDBID:
			#������ҵ�ǰ��PKģʽ �� ����ҵ�PKģʽ�趨Ϊ�����ģʽ��
			baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG ) # ����Ĭ��PKģʽΪ���ģʽ
			baseMailbox.cell.lockPkMode()
			
	def __restoreRobWarPkMode( self, playerTongDBID, baseMailbox ):
		"""
		�ָ�����ڽ��븱��֮ǰ��PKģʽ
		"""
		# if �����Ӷ�ս�� then return
		if not self._isRobWarOn: return
			
		spaceTongDBID = self.params.get( "tongDBID", None )
		if not spaceTongDBID:
			ERROR_MSG( "Can't find space tongDBID in self.params!" )
			return
		
		# if ������Լ��� ���� ����ǵж԰�����
		if playerTongDBID == spaceTongDBID or playerTongDBID == self._enemyTongDBID:
			# ����ҵ�pkģʽ�ָ����������֮ǰ��״̬
			baseMailbox.cell.unLockPkMode()
			baseMailbox.cell.setSysPKMode( 0 ) # ȡ��Ĭ��PKģʽ����
			
	def registerPlayer( self, baseMailbox, params = {} ): # ���ڰ��������ֹ����ռ䣬��������N���Ķ��󣬶ౣ��һ����Ϣ�����ڶԲ�ͬ����б�� by mushuang
		"""
		ע������space��mailbox���������
		"""
		SpaceCopy.registerPlayer( self, baseMailbox, params )
		playerInfo = {}
		playerInfo[ "tongDBID" ] = params[ "tongDBID" ]
		playerInfo[ "id" ] = baseMailbox.id
		playerInfo[ "baseMailbox" ] = baseMailbox
		
		self._detailedPlayerInfo.append( playerInfo )
		
	def unregisterPlayer( self, baseMailbox, params = {} ):
		"""
		ȡ������ҵļ�¼
		"""
		SpaceCopy.unregisterPlayer( self, baseMailbox, params = {} )
		
		playerID = baseMailbox.id
		length = len( self._detailedPlayerInfo )
		for i in xrange( length ):
			id = self._detailedPlayerInfo[i].get( "id", 0 )
			if id == playerID:
				del self._detailedPlayerInfo[ i ]
				break
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeave( self, baseMailbox, params )
		self.queryTemp( "playerDatas" ).pop( baseMailbox.id )
		
		## ����ڰ���Ӷ�ս�ڼ䣬�Զ�����ҵ�PKģʽ��ԭ �μ��� CSOL-9842
		playerTongDBID = params.get( "tongDBID", None )
		if playerTongDBID == None :
			ERROR_MSG( "Can't find player tongDBID in params!" )
			return
		self.__restoreRobWarPkMode( playerTongDBID, baseMailbox )
	#------------------------------------�������� ��ҽ����������BUFF------------------------------------------

	def getNagualBuffID( self, nagualLevel, nagualType ):
		"""
		������޵Ķ�Ӧ�⻷BUFF����ID
		"""
		if nagualLevel <= 0:
			nagualLevel = 1

		if csdefine.TONG_SHENSHOU_TYPE_1 == nagualType:
			return 730017000 + nagualLevel
		elif csdefine.TONG_SHENSHOU_TYPE_2 == nagualType:# ��ë����
			return 730018000 + nagualLevel
		elif csdefine.TONG_SHENSHOU_TYPE_3 == nagualType:# ����ʥ��
			return 730015000 + nagualLevel
		elif csdefine.TONG_SHENSHOU_TYPE_4 == nagualType:# ������ȸ
			return 730016000 + nagualLevel

	def castNagualBuffToTongMember( self, nagualLevel, nagualType ):
		"""
		������ڵı�����Ա������޵Ĺ⻷BUFF
		"""
		self.setTemp( "nagualData", ( nagualLevel, nagualType ) )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			if tongDBID == self.params[ "tongDBID" ]:
				pMB.cell.setTemp( "nagualOver", 0 )
				pMB.cell.spellTarget( self.getNagualBuffID( nagualLevel, nagualType ), pMB.id )

	def onNagualCreated( self, nagualLevel, nagualType ):
		"""
		���ޱ�������
		"""
		self.castNagualBuffToTongMember( nagualLevel, nagualType )

	def onNagualUpdateLevel( self, nagualLevel, nagualType ):
		"""
		���޼��������
		"""
		self.castNagualBuffToTongMember( nagualLevel, nagualType )

	def onShenShouDestroy( self ):
		"""
		���ޱ�������
		"""
		self.removeTemp( "nagualData" )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			if tongDBID == self.params[ "tongDBID" ]:
				pMB.cell.setTemp( "nagualOver", 1 )

	#--------------------------------------������-----------------------------------------------------------------------

	def onStartTongFete( self ):
		"""
		define method.
		��ʼ�������ˣ�  ��ؿ���Ϊ�û��һЩ��Ӧ��׼��
		�磺Ͷ�źó����������
		"""
		self.setTemp( "feteData", 0 )

	def onOverTongFete( self ):
		"""
		define method.
		����������
		"""
		self.removeTemp( "feteData" )

	#--------------------------------------�������-----------------------------------------------------------------------
	def checkProtectTongStart( self ):
		"""
		��鱣�����ɻ�Ƿ��Ѿ���ʼ��
		�������������Ҫ����Ϊ���ܱ������ɿ�ʼ�ˣ�������������
		��û�м��أ� ��ô�����globaldata����һ����ǣ� ���а�����
		�����󶼻��������ǣ� �����ǵ�ֵ�����Լ�����id��ô˵��
		��λ���뱾����йء�
		"""
		tongDBID = 0
		if BigWorld.globalData.has_key( "AS_ProtectTong" ):
			tongDBID = BigWorld.globalData[ "AS_ProtectTong" ][ 0 ]

		if self.params[ "tongDBID" ] == tongDBID:
			self.base.onProtectTongStart( BigWorld.globalData[ "AS_ProtectTong" ][ 2 ] )

	#--------------------------------------ħ����Ϯ�-----------------------------------------------------------------------
	def startCampaign_monsterRaid( self ):
		"""
		ħ����Ϯ����
		"""
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		self.setTemp( "startCampaingnTime", time.time() )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			pMB.client.onOpenCopySpaceInterface( [ 0 ] )
	
	def endCampaign_monsterRaid( self ):
		"""
		ħ����Ϯ��������ʾ��ʱ����ô�鷳��
		"""
		self.removeTemp( "startCampaingnTime" )
		for tongDBID, pMB in self.queryTemp( "playerDatas" ).itervalues():
			pMB.client.onCloseCopySpaceInterface()

	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
		]
		"""
		if self.queryTemp( "startCampaingnTime", 0 ) > 0:	# ���startCampaingnTime>0��˵��������ħ����Ϯ����򿪸�������
			return [ 0 ]
		else:
			return []
			
	#--------------------------------------����Ӷ�ս--------------------------------------#
	def onStartRobWar( self, enemyTongDBID ):
		"""
		defined method
		Baseͨ���˽ӿ�֪ͨ�Ӷ�ս��ʼ
		"""
		self._isRobWarOn = True
		self._enemyTongDBID = enemyTongDBID
		
		# �������Ѿ��ڰ������е��ҷ���Ա�͵ж԰����Ա��pkģʽ����Ϊ���ģʽ
		self.__setAllPlayersPkModeOnRobWar()
		
	def onEndRobWar( self ):
		"""
		defined method
		Baseͨ���˽ӿ�֪ͨ�Ӷ�ս����
		"""
		# �����л��ڰ������е��ҷ���Ա�͵ж԰����Ա��pkģʽ��ԭ������
		self.__restoreAllPlayersPkModeAfterRobWar()
		
		self._isRobWarOn = False
		self._enemyTongDBID = 0
		
		
	def __setAllPlayersPkModeOnRobWar( self ):
		"""
		�ڰ���Ӷ�ս��ʼʱ��������е������ҷ���Ա�͵ж԰����Ա��pkģʽ����Ϊ���ģʽ
		"""
		
		# for player in �����ڴ���صĳ�Ա
		for playerInfo in self._detailedPlayerInfo:
			# ����������ҷ����ǵжԷ�����Ա����ô�ı���pkģʽΪ���ģʽ������
			playerTongDBID = playerInfo.get( "tongDBID", 0 )
			playerBaseMB = playerInfo.get( "baseMailbox", None )
			if not playerTongDBID: continue
			if not playerBaseMB: continue
			self.__setRobWarPkMode( playerTongDBID, playerBaseMB )
			
						
	def __restoreAllPlayersPkModeAfterRobWar( self ):
		"""
		�ڰ���Ӷ�ս����ʱ��������е������ҷ���Ա�͵ж԰����Ա��pkģʽ�������ָ�Ϊԭ�ȵ�ģʽ
		"""
		# for player in �����������Ա:
		for playerInfo in self._detailedPlayerInfo:
			# if player���ҷ���Ա�����ǵж԰����Ա then ���� �� �ָ���PKģʽ
			playerTongDBID = playerInfo.get( "tongDBID", 0 )
			playerBaseMB = playerInfo.get( "baseMailbox", None )
			if not playerTongDBID: continue
			if not playerBaseMB: continue
			self.__restoreRobWarPkMode( playerTongDBID, playerBaseMB )
		

#
# $Log: not supported by cvs2svn $
#
#