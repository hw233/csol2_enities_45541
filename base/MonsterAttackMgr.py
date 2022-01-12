# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import cschannel_msgs
from Content import Content
import Love3
import random
import csdefine
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

from config.server import MonsterAttackConfig

MONSTER_GROUP = 4							#4������

DROP_BOX_RATE = 0.7							#���䱦�����


monsterAttackConfig = MonsterAttackConfig.Datas


class MonsterAttackContent( Content ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.val1 = 0
		self.val2 = 0
		self.spawns = []

	def init( self, obj, spawns ):
		"""
		"""
		setattr( obj, self.key, 0 )
		self.spawns = spawns
		self.val1 = 0
		self.val2 = 1

	def onContent( self, obj ):
		"""
		����ִ��
		"""
		for i in self.spawns:
			i.cell.createEntityNormal()

class firstContent( MonsterAttackContent ):
	"""
	#ˢ��һ������
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "firstContent"




	def beginContent( self, obj ):
		"""
		���ݿ�ʼ
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_ONE_NOTICE_01%smallBossName, [] )



	def doConditionChange(  self, obj, params ):
		"""
		���������д���
		"""
		if "monsterType" in params:
			if params["monsterType"] == 1:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_ONE_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				return True
		return False


class SecondContent( MonsterAttackContent ):
	"""
	#ˢ�ڶ�������
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "secondContent"


	def beginContent( self, obj ):
		"""
		���ݿ�ʼ
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_TWO_NOTICE_01%smallBossName, [] )


	def doConditionChange(  self, obj, params ):
		"""
		���������д���
		"""
		if "monsterType" in params:
			if params["monsterType"] == 1:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_TWO_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_01 ] )
				return True
		return False


class ThirdContent( MonsterAttackContent ):
	"""
	#ˢ����������
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "thirdContent"




	def beginContent( self, obj ):
		"""
		���ݿ�ʼ
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_THREE_NOTICE_01%smallBossName, [] )

	def doConditionChange(  self, obj, params ):
		"""
		���������д���
		"""
		if "monsterType" in params:
			if params["monsterType"] == 1:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_THREE_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_02 ] )
				return True
		return False


class NormalFourthContent( MonsterAttackContent ):
	"""
	#��ͨ���Ĳ�����
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "NormalFourthContent"


	def beginContent( self, obj ):
		"""
		���ݿ�ʼ
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_01%smallBossName, [] )


	def doConditionChange(  self, obj, params ):
		"""
		���������д���
		"""
		if "monsterType" in params:
			if params["monsterType"] == 2:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_03 ] )
				obj.spawnBuffs[obj.curArea].cell.remoteCallScript( "addAreaPlayerBuff", [] )
				return True
		return False


class FengmingFourthContent( MonsterAttackContent ):
	"""
	#�������Ĳ�����
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "FengmingFourthContent"
		self.val2 = 2

	def init( self, obj, spawns ):
		"""
		"""
		setattr( obj, self.key, 0 )
		self.spawns = spawns
		self.val1 = 0
		self.val2 = 2

	def beginContent( self, obj ):
		"""
		���ݿ�ʼ
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_01%smallBossName, [] )


	def doConditionChange(  self, obj, params ):
		"""
		���������д���
		"""
		if "monsterType" in params:
			if params["monsterType"] == 2:
				self.val1 += 1
				if self.val1 < self.val2:
					return False
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_03 ] )
				obj.spawnBuffs[obj.curArea].cell.remoteCallScript( "addAreaPlayerBuff", [] )
				return True
		return False


class MonsterAttackMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "MonsterAttackMgr", self._onRegisterManager )
		self.activityConfigs 		= monsterAttackConfig
		self.curArea				= ""
		self.curGroup				= 1
		self.spawns 				= {}		#such as {	"feilaishi"	:{1:[],2:[],3:[],4:[],},"banquanxiang"	:{}, ... }
		self.spawnBuffs				= {}
		self.spawnBoxs				= {}
		#������﹥������
		self.normalContents			= {
										1:firstContent(),
										2:SecondContent(),
										3:ThirdContent(),
										4:NormalFourthContent(),
									}
		#�������﹥������
		self.fengmingContents		= {
										1:firstContent(),
										2:SecondContent(),
										3:ThirdContent(),
										4:FengmingFourthContent(),
									}
		self.contents = {}


	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register MonsterAttackMgr Fail!" )
			# again
			self.registerGlobally( "MonsterAttackMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["MonsterAttackMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("MonsterAttackMgr Create Complete!")

			self.registerCrond()


	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"MonsterAttackMgr_start_notice" : "onStartNotice",
					  	"MonsterAttackMgr_start" : "onStart",
					  	"MonsterAttackMgr_end" : "onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		


	def addSpawnPoint( self, spawnPointMB, spaceLabel, group, part ):
		"""
		define method
		"""
		if spaceLabel not in self.spawns:
			self.spawns[spaceLabel] = {}

		if group not in self.spawns[spaceLabel]:
			self.spawns[spaceLabel][group] = {}

		if part not in self.spawns[spaceLabel][group]:
			self.spawns[spaceLabel][group][part] = []

		self.spawns[spaceLabel][group][part].append( spawnPointMB )

	def addSpawnPointBuff( self, spawnPointMB, spaceLabel ):
		"""
		define method
		"""
		if spaceLabel not in self.spawnBuffs:
			self.spawnBuffs[spaceLabel] = spawnPointMB


	def addSpawnPointBox( self, spawnPointMB, spaceLabel, group ):
		"""
		define method
		"""
		if spaceLabel not in self.spawnBoxs:
			self.spawnBoxs[spaceLabel] = {}

		if group not in self.spawnBoxs[spaceLabel]:
			self.spawnBoxs[spaceLabel][group] = spawnPointMB


	def initContent( self ):
		"""
		"""
		global MonsterContentList
		areaConfig = self.activityConfigs[self.curArea]
		areaSpawns = self.spawns[self.curArea]

		for i in xrange( 1, MONSTER_GROUP + 1 ):
			part = random.choice( areaSpawns[i].keys() )
			self.contents[i].init( self, areaSpawns[i][part] )


	def run( self ):
		"""
		"""
		self.initContent()
		self.contents[self.curGroup].doContent( self )




	def onStart( self ):
		"""
		define method.
		���ʼ
		"""
		if BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			curTime = time.localtime()
			ERROR_MSG( "���﹥�ǻ���ڽ��У�%i��%i����ͼ�ٴο�ʼ���﹥�ǡ�"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "AS_MonsterAttack" ] = True
		if self.curArea == "":
			self.onStartNotice()
		self.run()

	def onEnd( self ):
		"""
		define method.
		�����
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		if not BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			curTime = time.localtime()
			ERROR_MSG( "���﹥�ǻ�Ѿ�������%i��%i����ͼ�ٴν������﹥�ǡ�"%(curTime[3],curTime[4] ) )
			return
		if BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			del BigWorld.globalData[ "AS_MonsterAttack" ]
		if self.curGroup <= MONSTER_GROUP:
			bossName = self.activityConfigs[self.curArea]["bossName"]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_END_NOTICE_02%bossName, [] )
			for iContent in self.contents.values():
				for iSpawn in iContent.spawns:
					iSpawn.cell.remoteCallScript( "onAttackEnd", [] )
		self.contents = {}
		self.curArea = ""
		self.curGroup = 1

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		if self.curArea == "":
			self.curArea = random.choice( self.activityConfigs.keys() )
			if self.curArea == "fengming":
				self.contents = self.fengmingContents
			else:
				self.contents = self.normalContents
		spaceName = self.activityConfigs[self.curArea]["name"]
		bossName = self.activityConfigs[self.curArea]["bossName"]
		if self.curArea == "fengming":
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_FENGMING_NOTICE_01, [] )
		else:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_NOTICE_01%( bossName, spaceName, spaceName ), [] )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_NOTICE_02, [] )


	def onMonsterDied( self, params ):
		"""
		"""
		if BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			if self.curGroup in self.contents:
				self.contents[self.curGroup].onConditionChange( self, params )


	def onContentFinish( self ):
		"""
		"""
		self.curGroup += 1
		if self.curGroup > MONSTER_GROUP:
			spaceName = self.activityConfigs[self.curArea]["name"]
			bossName = self.activityConfigs[self.curArea]["bossName"]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_END_NOTICE_01%( spaceName, bossName, spaceName ), [] )
		else:
			self.contents[self.curGroup].doContent( self )



def test():
	"""
	"""
	ma = BigWorld.entities[BigWorld.globalData["MonsterAttackMgr"].id]
	ma.onStartNotice()
	ma.onStart()
	return ma