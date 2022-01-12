# -*- coding: gb18030 -*-

# 60级剧情副本
# by hezhiming

# python
import random
# bigworld
import BigWorld
# common
import csdefine
from bwdebug import ERROR_MSG
# cell
from CopyContent import CopyContent, CCEndWait, CCKickPlayersProcess
from SpaceCopyTemplate import SpaceCopyTemplate
from GameObjectFactory import g_objFactory

QUEST_PRODUCE_BOW = 20302025
QUEST_STRANGLE_GOLD_BIRD = 20302026

class CCProduceBow( CopyContent ) :
	"""制作神弓"""
	#MONSTER_SPAWN_POINT = ( -2.375, 9.01, 16.637)
	#MONSTER1 = "20321001"
	def __init__( self ) :
		CopyContent.__init__( self )
		self.key = "ProduceBow"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		开始执行副本内容
		"""
		print "Enter produce bow!"
		#g_objFactory.getObject( self.MONSTER1 ).createEntity( spaceEntity.spaceID,\
				#self.MONSTER_SPAWN_POINT, (0,0,0), {} )

	def doConditionChange( self, spaceEntity, params ) :
		"""
		"""
		if params.get( "questCommitted", False ) :					# 任务完成
			return True
		return False
		
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		player = BigWorld.entities[ baseMailbox.id ]
		if player.has_quest( QUEST_PRODUCE_BOW ) and not player.questTaskIsCompleted( QUEST_PRODUCE_BOW ):
			for taskIndex in player.getQuestTasks( QUEST_PRODUCE_BOW ).getTasks().iterkeys():
				player.questTaskFailed( QUEST_PRODUCE_BOW, taskIndex )
		

class CCStrangleGoldBird( CopyContent ):
	"""
	绞杀金乌
	"""
	MONSTER1 = {'id':'20654009', 'killAmount':1, 'spawnAmount':1}
	MONSTER2 = {'id':'20654009', 'killAmount':3, 'spawnAmount':3}
	MONSTER3 = {'id':'20654009', 'killAmount':5, 'spawnAmount':5}
	MONSTER4 = {'id':'20654009', 'killAmount':1, 'spawnAmount':1}
	SPAWN_POSITIONS = [ (28.279804, 19.691992, -12.520078), (28.279804, 19.691992, -12.520078), (28.279804, 19.691992, -12.520078),\
						(28.279804, 19.691992, -12.520078), (28.279804, 19.691992, -12.520078), (28.279804, 19.691992, -12.520078),\
						(28.279804, 19.691992, -12.520078),(28.279804, 19.691992, -12.520078),(28.279804, 19.691992, -12.520078),\
						(28.279804, 19.691992, -12.520078)]
	def __init__( self ):
		CopyContent.__init__( self )
		self.key = "StrangleGoldBird"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		"""
		开始执行副本内容
		"""
		print "Start strangle gold bird!"
		
	def spawnOneMonster( self, spaceEntity ):
		g_objFactory.getObject( self.MONSTER1["id"] ).createEntity( spaceEntity.spaceID, self.SPAWN_POSITIONS[0], (0, 0, 0), {} )
		pass
		
	def spawnTwoMonster( self, spaceEntity ):
		amount = 0
		index = self.MONSTER1["spawnAmount"]
		while amount < self.MONSTER2["killAmount"]:
			g_objFactory.getObject( self.MONSTER2["id"] ).createEntity( spaceEntity.spaceID, self.SPAWN_POSITIONS[index], (0, 0, 0), {} )
			amount = amount + 1
			index = index + 1
		pass
		
	def spawnThreeMonster( self, spaceEntity ):
		amount = 0
		index = self.MONSTER1["spawnAmount"] + self.MONSTER1["spawnAmount"]
		while amount < self.MONSTER3["killAmount"]:
			g_objFactory.getObject( self.MONSTER3["id"] ).createEntity( spaceEntity.spaceID, self.SPAWN_POSITIONS[index], (0, 0, 0), {} )
			amount = amount + 1
			index = index + 1
		pass
		
	def spawnFourMonster( self, spaceEntity ):
		index = self.MONSTER1["spawnAmount"] + self.MONSTER1["spawnAmount"] + self.MONSTER3["spawnAmount"]
		g_objFactory.getObject( self.MONSTER4["id"] ).createEntity( spaceEntity.spaceID, self.SPAWN_POSITIONS[index], (0, 0, 0), {} )
			
	def doConditionChange( self, spaceEntity, params ):
		"""
		"""
		CopyContent.doConditionChange( self, spaceEntity, params )
		if params.get( "spawnMonsters", False ) :					# 开始刷怪
			self.spawnOneMonster(spaceEntity)
		elif params.has_key( "monsterKilled" ) :
			className = params.get( "monsterKilled" )
			spaceEntity.jinwu_onMonsterKilled( className )
			if spaceEntity.jinwu_getMonsterKilled( self.MONSTER3["id"] ) == self.MONSTER1["killAmount"] + self.MONSTER2["killAmount"] + self.MONSTER3["killAmount"]:
				self.spawnFourMonster( spaceEntity )
			elif spaceEntity.jinwu_getMonsterKilled( self.MONSTER2["id"] ) == self.MONSTER1["killAmount"] + self.MONSTER2["killAmount"]:
				self.spawnThreeMonster( spaceEntity )
			elif spaceEntity.jinwu_getMonsterKilled( self.MONSTER1["id"] ) == self.MONSTER1["killAmount"]:
				self.spawnTwoMonster( spaceEntity )
		elif params.get( "questCommitted", False ) :				# 任务完成
			return True												# 进入下一个关卡
		return False
		
	def onTimer( self, spaceEntity, id, userArg ):
		#if userArg == JINWU_SPAWN_1:
			#g_objFactory.getObject( MONSTERID ).createEntity( spaceEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {} )
		#elif userArg == JINWU_SPAWN_2:
			#g_objFactory.getObject( MONSTERID ).createEntity( spaceEntity.spaceID, REWARD_POSITION_3, (0, 0, 0), {} )
		pass
		
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		player = BigWorld.entities[ baseMailbox.id ]
		if player.has_quest( QUEST_PRODUCE_BOW ) and not player.questTaskIsCompleted( QUEST_PRODUCE_BOW ):
			for taskIndex in player.getQuestTasks( QUEST_PRODUCE_BOW ).getTasks().iterkeys():
				player.questTaskFailed( QUEST_PRODUCE_BOW, taskIndex )

class SpaceCopyPlotLv60( SpaceCopyTemplate ) :
	# QUEST_GATHER_STONES = 20302021
	# QUEST_ASSISTING_NVWA = 20302022
	# QUEST_KILL_GONGGONG = 20302023

	def __init__( self ) :
		SpaceCopyTemplate.__init__( self )

	def canUseSkill( self, playerEntity, skillID ) :
		"""
		使用空间机能
		"""
		return True

	def initContent( self ) :
		self.contents.append( CCProduceBow() )
		self.contents.append( CCStrangleGoldBird())
		#self.contents.append( CCKillGonggong() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )

	def onConditionChange( self, selfEntity, params ) :
		"""
		条件改变
		"""
		if params.has_key( "copyContentIndex" ) :							# 设置副本的当前进度
			selfEntity.setTemp( "contentIndex", int( params[ "copyContentIndex" ] ) )
		SpaceCopyTemplate.onConditionChange( self, selfEntity, params )
		
	def onEnterCommon( self, spaceEntity, baseMailbox, params ) :
		"""
		玩家进入副本
		"""
		if spaceEntity.queryTemp("firstPlayer", 0 ) == 0 :					# 第一次进入副本，根据任务情况来设置副本进度
			player = BigWorld.entities.get( baseMailbox.id )
			if player.has_quest( QUEST_PRODUCE_BOW ) :
				spaceEntity.setTemp( "contentIndex", 0 )
			elif player.has_quest( QUEST_STRANGLE_GOLD_BIRD ) :
				spaceEntity.setTemp( "contentIndex", 1 )
		SpaceCopyTemplate.onEnterCommon( self, spaceEntity, baseMailbox, params )

