# -*- coding: gb18030 -*-

"""
2013-8-22,writen by chenweilan
"""

import BigWorld
import time
import random
import Love3
import csdefine
import csconst
import cschannel_msgs
from bwdebug import *
from csconst import g_maps_info
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from config.server.CampActivityConfig import Datas as ActivityData

from CampActivityControl import CAMP_ACTIVITY_CONTROL

TIMER_ARG_ACT_CLOSE			= 1
TIMER_ARG_ACT_START			= 2
TIMER_REFRESH_DAILY_QUEST	= 3
TIMER_NOTICE				= 4

MGR_STATE_NONE	= 0
MGR_STATE_START	= 1

OPEN_STYLE_SPACE_ONE 	= 0	#�������һ�ŵ�ͼ
OPEN_STYLE_SPACE_ALL	= 1	#���е�ͼ����

#----------------------------------
# �ݵ�
#----------------------------------
class Locations( object ):
	"""
	��ݵ�
	"""
	def __init__( self, camp, space, spaceMB ):
		self.space = ""
		self.camp = 0
		self.spaceMB = spaceMB
		self.locationsSpawnPoint = []
		self.locationsEntities = {}
		self.locationsRemain = 0	#�ݵ�ʣ�����
		self.locationsSpawnNums = 0
		self.isOccued = False
	
	def registerEntity( self, className, spMB, spawnNum ):
		self.locationsSpawnPoint.append( spMB )
		if not self.locationsEntities.has_key( className ):
			self.locationsEntities[ className ] = spawnNum
		else:
			self.locationsEntities[ className ] += spawnNum
		
		self.locationsSpawnNums += spawnNum
		self.locationsRemain = self.locationsSpawnNums
	
	def isOccupy( self ):
		return self.locationsRemain <= 0
	
	def occupy( self ):
		#�ݵ㱻����
		self.isOccued = True
		for sp in self.locationsSpawnPoint:
			sp.cell.onLocationOccuped()
		
		enemyCamp = 0
		if self.camp == csdefine.ENTITY_CAMP_TAOISM:
			enemyCamp = csdefine.ENTITY_CAMP_DEMON
		elif self.camp == csdefine.ENTITY_CAMP_DEMON:
			enemyCamp = csdefine.ENTITY_CAMP_TAOISM
		self.spaceMB.allPlayersRemoteCall( "camp_systemCastSpell", ( enemyCamp, csconst.CAMP_OCCUPED_SPELL_ID, ) )		# �����buff
	
	def entityDie( self, className ):
		"""
		�ݵ�entity����ɱ
		"""
		if self.locationsEntities.has_key( className ):
			self.locationsRemain -= 1
		
		if self.isOccupy():
			if not self.isOccued:
				self.occupy()
	
	def entityRedivious( self, className, num ):
		"""
		�ݵ�entity����
		"""
		if className in self.locationsEntities.keys():
			self.locationsRemain += num
			
		if self.locationsRemain > self.locationsSpawnNums:
			ERROR_MSG( "remain mosnter number > location mosnter number" )
		
	def resert( self ):
		"""
		���þݵ�
		"""
		self.isOccued = False
		self.locationsRemain = self.locationsSpawnNums
		for sp in self.locationsSpawnPoint:
			sp.cell.recoverLocation()

class LocationsMgr( object ):
	"""
	�ݵ������
	"""
	def __init__( self, mgr ):
		self._data = {}
		self.mgr = mgr
	
	def isOccupy( self, camp = 0, space = "" ):
		"""
		�жϾݵ��Ƿ�ռ��
		"""
		if camp == 0 and space == "":
			for l in self._data.values():
				if not l.isOccupy():
					return False
					
		elif camp == 0 and space:
			for l in self._data.values():
				if l.space == space:
					if not l.isOccupy():
						return False
		
		elif camp and space == "":
			for l in self._data.values():
				if l.camp == camp:
					if not l.isOccupy():
						return False
						
		elif camp and space:
			if self._data.has_key( ( camp, space ) ):
				return self._data[ ( camp, space ) ].isOccupy()
		
		return True
	
	def resert( self, camp = 0, space = "" ):
		"""
		���þݵ�
		"""
		if camp == 0 and space == "":
			for l in self._data.values():
				l.resert()
		
		elif camp == 0 and space:
			for l in self._data.values():
				if l.space == space:
					l.resert()
		
		elif camp and space == "":
			for l in self._data.values():
				if l.camp == camp:
					l.resert()
		
		elif camp and space:
			if self._data.has_key( ( camp, space ) ):
				self._data[ ( camp, space ) ].resert()
	
	def resertAllLocation( self ):
		"""
		�ָ����оݵ�
		"""
		for l in self._data.values():
			l.resert()
	
	def registerSpawnPoint( self, camp, space, className, spMB, spaceMB, spawnNum ):
		if not self._data.has_key( ( camp, space ) ):
			self._data[ ( camp, space ) ] = Locations( camp, space, spaceMB )
		
		self._data[ ( camp, space ) ].registerEntity( className, spMB, spawnNum )
	
	def entityDie( self, camp, space, className ):
		if self._data.has_key( ( camp, space ) ):
			self._data[ ( camp, space ) ].entityDie( className )
			
	def entityRedivious( self, camp, space, className, num ):
		if self._data.has_key( ( camp, space ) ):
			self._data[ ( camp, space ) ].entityRedivious( className, num )

class CampActivityMgr:
	"""
	��Ӫ�������
	"""
	def __init__( self ):
		self.activityMgrState = MGR_STATE_NONE		#��ǰ������״̬
		self.monsterSpawnPoints = {}				#����ˢ�µ� ����{ (camp,'fengming'):{ className: [sp1,sp2] }, ... }
		self.dailyQuestNpcs = []					#�ճ����񷢲�NPC
		self.activityData = {}
		self.loadActData()
		self.activityMgr = None
		self.countTimer = 0							# �ˢ��timer
		self.campLocationMgr = LocationsMgr( self )

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"CampActivity_notice": "onNotice",
						"CampActivity_start" : "onStart",
						"CampActivity_end" : "onEnd",
						}
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
	
	# ------------------------------------
	# ���ݳ�ʼ��
	# ------------------------------------
	def loadActData( self ):
		"""
		���ػ����
		"""
		for item in ActivityData:
			type = item[ "activityTypes" ]
			spaces = item[ "spaceName" ].split( ";" )
			openStyle = int( item[ "openStyle" ] )
			activityTime = int( item[ "activityTime" ] )
			self.activityData[ type ] = ( spaces, openStyle, activityTime )
	
	#-------------------------------------
	# �����
	#-------------------------------------
	def onNotice( self ):
		"""
		define method.
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_ACT_NOTICE_1, [] )
		self.addTimer( 5 * 60, 0, TIMER_NOTICE )
	
	# ------------------------------------
	# �����
	# ------------------------------------
	def onStart( self ):
		"""
		define method.
		���ʼ
		"""
		if self.activityMgrState: # ��������ο���
			return 
			
		self.activityMgrState = MGR_STATE_START
		self.randomSartAct()
	
	def start( self, activity, spaces, camp ):			# camp ��������ָ��С������Ĺ�����Ӫ��������˲���Ĭ��Ϊ0
		"""
		define method.
		ָ�������ĸ��
		"""
		openSpaces = spaces
		if not len( spaces ):
			allSpaces = self.activityData[ activity ][ 0 ]
			if self.activityData[ activity ][ 1 ] == OPEN_STYLE_SPACE_ONE:
				openSpaces = [ random.choice( allSpaces ), ]
			else:
				openSpaces = allSpaces
		
		self.activityMgr = CAMP_ACTIVITY_CONTROL[ activity ]()
		self.activityMgr.init( self, openSpaces, camp, self.activityData[ activity ][ 2 ] )
		BigWorld.globalData["CampActivityCondition"] = ( self.activityMgr.openSpaces, self.activityMgr.activity )
		
		self.activityMgr.start( self )
		persistSecond = g_CrondDatas.getTaskPersist( "CampActivity_start" ) * 60
		if persistSecond == 0:
			persistSecond = 8 * 60 * 60
		BigWorld.globalData["CampActivityEndTime"] = time.time() + persistSecond 
		
		INFO_MSG( "Camp activity start !", self.activityMgr.activity, self.activityMgr.openSpaces )
	
	def randomSartAct( self ):
		"""
		�������һ���
		"""
		if self.activityMgr and self.activityMgrState == MGR_STATE_NONE:
			return
			
		activity = random.choice( CAMP_ACTIVITY_CONTROL.keys() )
		
		self.start( activity, [], 0 )

	def onEnd( self ):
		"""
		�����
		"""
		if BigWorld.globalData.has_key( "CampActivityCondition" ):
			del BigWorld.globalData["CampActivityCondition"]
		if BigWorld.globalData.has_key( "CampActivityEndTime" ):
			del BigWorld.globalData["CampActivityEndTime"]
		self.activityMgrState = MGR_STATE_NONE
		if not self.activityMgr:
			return
			
		self.activityMgr.close( self )
		self.activityMgr = None
		if self.countTimer != 0:
			self.delTimer( self.countTimer )
			self.countTimer = 0
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_ACTIVITY_NOTICE_3, [] )
		INFO_MSG( "Camp activity end !" )
	
	def startActivityCountDown( self ):
		"""
		�������ʱ
		"""
		self.countTimer = self.addTimer( self.activityMgr.activityTime, 0, TIMER_ARG_ACT_CLOSE )
	
	# ------------------------------------
	# �ݵ�
	# ------------------------------------
	def addLocationSpawnPoint( self, camp, spaceName, className, spMB, spaceMB, spawnNum ):
		"""
		define method
		��¼�ݵ�NPCˢ�µ�
		"""
		self.campLocationMgr.registerSpawnPoint( camp, spaceName, className, spMB, spaceMB, spawnNum )
	
	def onLocationMonsterDie( self, camp, spaceName, className ):
		"""
		define method.
		�ݵ��������
		"""
		self.campLocationMgr.entityDie( camp, spaceName, className )
		
	def onLocationMonsterRedivious( self, camp, spaceName, className, num ):
		"""
		define method
		�ݵ���︴��
		"""
		self.campLocationMgr.entityRedivious( camp, spaceName, className, num )
	
	# ------------------------------------
	# ����&����ˢ��
	# ------------------------------------
	def addDailyQuestNpcBases( self, npcMB ):
		"""
		define method
		��¼�ճ����񷢲�NPC��base�����ڷ����ճ�����
		"""
		if npcMB.id not in [ i.id for i in self.dailyQuestNpcs ]:
			self.dailyQuestNpcs.append( npcMB )
			
	def dailyQuest( self ):
		"""
		ˢ������
		"""
		for base in self.dailyQuestNpcs:
			base.cell.remoteScriptCall( "filtrateDailyQuest", () )
	
	def addActivityMonsterSpawnPoint( self, spaceName, className, spawnPointMailBox, camp ):
		"""
		define method
		"""
		key = ( camp, spaceName )
		if not self.monsterSpawnPoints.has_key( key ):
			self.monsterSpawnPoints[ key ] = {}

		if not self.monsterSpawnPoints[ key ].has_key( className ):
			self.monsterSpawnPoints[ key ][ className ] = []

		self.monsterSpawnPoints[key][className].append( spawnPointMailBox )
			
	def spawnMonster( self, spaces, camp = 0, className = "" ):
		"""
		ˢ������
		"""
		if camp:
			keys = []
			for s in spaces:
				keys.append( ( camp, s ) )
			
			for key, spaceSpawnPoints in self.monsterSpawnPoints.iteritems():
				if key in keys:
					for cls, spawnPointList in spaceSpawnPoints.iteritems():
						if cls == className or className == "":
							for sp in spawnPointList:
								sp.cell.createEntityNormal()
		else:
			for key, spaceSpawnPoints in self.monsterSpawnPoints.iteritems():
				if key[1] in spaces:
					for cls, spawnPointList in spaceSpawnPoints.iteritems():
						if cls == className or className == "":
							for sp in spawnPointList:
								sp.cell.createEntityNormal()
	
	def destroyMonster( self ):
		"""
		����ˢ������
		"""
		for key, spaceSpawnPoints in self.monsterSpawnPoints.iteritems():
			for cls, spawnPointList in spaceSpawnPoints.iteritems():
				for sp in spawnPointList:
					sp.cell.onActivityEnd()

	# ------------------------------------
	# public
	# ------------------------------------
	def checkSpaceAndType( self, spaceName, activityType ):
		"""
		����ͼ�ͻ����
		"""
		if not g_maps_info.has_key( spaceName ):
			ERROR_MSG( "Camp activity space is wrong��space: %s" % spaceName )
			return False
			
		if activityType not in csconst.CAMP_ACTIVITY_TYPES:
			ERROR_MSG( "Camp activity type is wrong��type: %s" % activityType )
			return False
		return True
	
	def onTimer( self, tid, userArg ):
		if TIMER_NOTICE == userArg:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_ACT_NOTICE_2, [] )
			
		if TIMER_ARG_ACT_CLOSE == userArg:
			self.activityMgr.close( self )
			self.addTimer( 3, 0, TIMER_ARG_ACT_START )
		
		if TIMER_ARG_ACT_START == userArg:
			self.activityMgr.start( self )
			
		if TIMER_REFRESH_DAILY_QUEST == userArg:
			self.dailyQuest()
