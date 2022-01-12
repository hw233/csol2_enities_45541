# -*- coding: gb18030 -*-
import time
import random
import BigWorld

from bwdebug import *
import csstatus
import csdefine
import csconst
import cschannel_msgs

import Love3
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from ObjectScripts.GameObjectFactory import GameObjectFactory

ACTIVITY_STATE_START 	= 1
ACTIVITY_STATE_END 		= 2

TIMER_ARG_READY = 1
TIMER_ARG_END = 2

GET_ENTER_SPACE_NUMBER_FULL 			= -1
GET_ENTER_SPACE_NUMBER_LEVEL_CLOSED 	= -2

SPACE_CLASS_NAME = "fu_ben_ye_zhan_feng_qi"

class YeZhanFengQiMgr( BigWorld.Base ):
	# �����̨������
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "YeZhanFengQiMgr", self._onRegisterManager )
		self.spaceType = SPACE_CLASS_NAME
		self.activityState = ACTIVITY_STATE_END
		self.activityStarTime = 0.0
		
		self.battlefieldInfos = {}
		self.spaceNumberEnters = {}
		
		self.minLevel = 0
		self.maxLevel = 0
		self.intervalLevel = 0
		self.minPlayer = 0
		self.maxPlayer = 0
		self.maxExit = 0
		self.minLevelPlayer = 0
		
		self.spaceLife = 0
		
		self.itemRequestInfos = {}
		self.waitListInfos = {}
		self.initConfigData( self.getScript() )
	
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register YeZhanFengQiMgr Fail!" )
			self.registerGlobally( "YeZhanFengQiMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["YeZhanFengQiMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("YeZhanFengQiMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"YeZhanFengQi_notice" : "onNotice",
						"YeZhanFengQi_start" : "onStart",
						"YeZhanFengQi_end" : "onEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
	
	def getScript( self ):
		return GameObjectFactory.instance().getObject( self.spaceType )
	
	def initConfigData( self, objScript ):
		"""
		��ʼ������
		"""
		self.maxExit = objScript.maxExit
		self.minLevel = objScript.minLevel
		self.maxLevel = objScript.maxLevel
		self.intervalLevel = objScript.intervalLevel
		self.minPlayer = objScript.minPlayer
		self.maxPlayer = objScript.maxPlayer
		self.minLevelPlayer = objScript.minLevelPlayer
		self.prepareTime = objScript.prepareTime
		self.spaceLife = objScript.spaceLife
		
	def initBattlefieldData( self, minLevel, maxLevel, intervalLevel ):
		"""
		��ʼ��ս������
		"""
		cLevel = minLevel
		nextLevel = minLevel + intervalLevel
		while nextLevel < maxLevel:
			self.battlefieldInfos[ ( cLevel, nextLevel  ) ] = [ 0 for i in xrange( self.maxExit ) ]
			cLevel = nextLevel + 1
			nextLevel += intervalLevel
		self.battlefieldInfos[ ( cLevel, maxLevel  ) ] = [ 0 for i in xrange( self.maxExit ) ]
		
		self.spaceNumberEnters = {}
		
		# Ϊ�˰�ȫ��������Ŷӽ�����ϢҲ���������Ϸ��Ա��Ҫ�ڱ��˽����ʱ�����GMָ��ͺã�
		self.itemRequestInfos = {}
		self.waitListInfos = {}
	
	def getBattlefieldItemKey( self, level ):
		"""
		��ȡkey
		"""
		for k in self.battlefieldInfos.iterkeys():
			if k[ 0 ] <= level and k[ 1 ] >= level:
				return k
		
		return None
	
	def onNotice( self ):
		"""
		define method
		����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WIZCOMMAND_YE_ZHAN_FENG_QI_NOTICE, [] )
		INFO_MSG( "YeZhanFengQiMgr", "notice", "" )
	
	def onStart( self ):
		"""
		define method.
		���ʼ
		"""
		self.initBattlefieldData( self.minLevel, self.maxLevel, self.intervalLevel ) # ��ʼ��ս������
		self.activityState = ACTIVITY_STATE_START
		self.addTimer( self.prepareTime * 60, 0, TIMER_ARG_READY )
		self.addTimer( self.spaceLife * 60, 0,	 TIMER_ARG_END )
		self.activityStarTime = time.time()
		INFO_MSG( "YeZhanFengQiMgr", "start", "" )
	
	def onEnd( self ):
		"""
		define method.
		�����
		"""
		if self.activityState != ACTIVITY_STATE_START:
			return 
			
		self.activityState = ACTIVITY_STATE_END
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.spaceType, "activityEnd", [] )
		self.activityStarTime = 0
		INFO_MSG( "YeZhanFengQiMgr", "end", "" )
	
	def requestEnterSpace( self, domainBase, position, direction, baseMailbox, params ):
		"""
		define method
		����������ս��
		"""
		if self.activityState == ACTIVITY_STATE_END: # ���ڻʱ��
			baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_ACTIVITY_END, "" )
			return
			
		level = params[ "level" ] 
		enterNumber = self._getEnterSpaceNumber( level, [], 0 )
		k = self.getBattlefieldItemKey( level )
		if not self.battlefieldInfos.has_key( k ):
			baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_CANNOT_ENTER, "" )
			return
			
		levelSpaceNumbers = self.battlefieldInfos[ k ]
		params[ "spaceKey" ] = enterNumber
		if enterNumber < 0:
			if enterNumber == GET_ENTER_SPACE_NUMBER_FULL:
			# �õȼ��ε�����ս����������ȫ��
				baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_ENTER_FULL, "" )
			elif enterNumber == GET_ENTER_SPACE_NUMBER_LEVEL_CLOSED:
				baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_LEVEL_CLOSE, "" )
			return
		elif enterNumber != 0:
			self.spaceNumberEnters[ enterNumber ] += 1
		else:
			if self.itemRequestInfos.has_key( k ):
				if len( list( set( levelSpaceNumbers ) ^ set( [0] ) ) ) + self.itemRequestInfos[ k ] >= self.maxExit: # һ���ȼ���������ս������
					self.waitListInfos.append( [domainBase, position, direction, baseMailbox, params] )
					return
				else:
					self.itemRequestInfos[ k ] += 1
			else:
				self.itemRequestInfos[ k ] = 1
		
		params[ "spaceLevel" ] = k[1]
		params[ "actStartTime" ] = self.activityStarTime
		domainBase.teleportEntityMgr( position, direction, baseMailbox, params )
	
	def playerExit( self, spaceNumber, pMB ):
		"""
		define method
		����˳�����
		"""
		if self.spaceNumberEnters.has_key( spaceNumber ):
			self.spaceNumberEnters[ spaceNumber ] -= 1
	
	def _getEnterSpaceNumber( self, level, exceptNum = [] , rep = 0 ):
		# ��ȡ����ID
		if rep > self.maxExit: # �õȼ��ε�����ս����������ȫ��
			return GET_ENTER_SPACE_NUMBER_FULL
		
		k = self.getBattlefieldItemKey( level )
		levelSpaceNumbers = self.battlefieldInfos[ k ]
		canEnterNumbers = list( set( levelSpaceNumbers) ^ set( exceptNum ) )
		if not len( canEnterNumbers ):
			return GET_ENTER_SPACE_NUMBER_LEVEL_CLOSED
			
		enterNumber = random.choice( canEnterNumbers )
		if enterNumber:
			if self.spaceNumberEnters[ enterNumber ] >= self.maxPlayer:
				exceptNum.append( enterNumber )
				return self._getEnterSpaceNumber( level, exceptNum, rep + 1 )
				
		return enterNumber
	
	def addNewSpaceNumber( self, level, spaceNumber ):
		"""
		define method
		������һ���µ�ս��
		"""
		k = self.getBattlefieldItemKey( level )
		idx = self.battlefieldInfos[ k ].index( 0 )
		self.battlefieldInfos[ k ][ idx ] = spaceNumber
		self.spaceNumberEnters[ spaceNumber ] = 1
		copyList  = self.waitListInfos
		self.waitListInfos = []
		for wInf in copyList:
			self.requestEnterSpace( *wInf )
	
	def removeSpaceNumber( self, spaceNumber ):
		"""
		define method
		ɾ��һ��ս��
		"""
		for key, value in self.battlefieldInfos.iteritems():
			if spaceNumber in value:
				idx = value.index( spaceNumber )
				value[ idx ] = 0
				break
	
	def checkEnter( self ):
		"""
		׼��ʱ������������������Ƿ����
		"""
		closeNumber = []
		for k, v in self.spaceNumberEnters.iteritems():
			if v < self.minPlayer:
				closeNumber.append( k )
		
		for v in self.battlefieldInfos.itervalues():
			c = 0
			for num in v:
				if num in self.spaceNumberEnters:
					c += self.spaceNumberEnters[ num ]
				
			if c < self.minLevelPlayer: # �����ǰ�ȼ��ε�����ս��������������������������ս��ȫ�ر�
				for num in v:
					if num not in closeNumber:
						closeNumber.append( num )
		
		closeNumber = list( set( closeNumber ) ^ set( [0] ) )
		for num in closeNumber:
			self.closeSpaceCopy( num )
	
	def closeSpaceCopy( self, spaceNumber ):
		"""
		�ر�ָ���ĸ���
		"""
		if self.spaceNumberEnters.has_key( spaceNumber ):
			del self.spaceNumberEnters[ spaceNumber ]
		
		for v in self.battlefieldInfos.itervalues():
			if spaceNumber in v:
				v.remove( spaceNumber )
				break
				
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.spaceType, "closeSpaceItem", [ spaceNumber ] )
	
	def onTimer( self, tid, arg ):
		# addTimer control
		if arg  == TIMER_ARG_READY:
			self.checkEnter()
		elif arg == TIMER_ARG_END:
			self.onEnd()
		