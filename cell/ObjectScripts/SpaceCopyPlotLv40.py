# -*- coding: gb18030 -*-

# 40级剧情副本
# by ganjinxing

# python
import random
# bigworld
import math
import time
import Math
import BigWorld
# common
import csdefine
import csstatus
from bwdebug import ERROR_MSG, WARNING_MSG
# cell
from CopyContent import CopyContent, CCEndWait, CCKickPlayersProcess
from SpaceCopyTemplate import SpaceCopyTemplate
from GameObjectFactory import g_objFactory

# global define
QUEST_GATHER_STONES = 20302021
QUEST_ASSIST_NVWA = 20302022
QUEST_KILL_GONGGONG = 20302023


class CCGatherStones( CopyContent ) :
	"""采集五色石"""
	NVWA_AI_CMD_REVERT = 200										# 副本内容恢复的指令

	def __init__( self ) :
		CopyContent.__init__( self )
		self.key = "gatherStones"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		开始执行副本内容
		"""
		print "Enter gathering stones!"

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
		if player.has_quest( QUEST_GATHER_STONES ) and not player.questTaskIsCompleted( QUEST_GATHER_STONES ) :
			for taskIndex in player.getQuestTasks( QUEST_GATHER_STONES ).getTasks().iterkeys() :
				player.questTaskFailed( QUEST_GATHER_STONES, taskIndex )
			nvwa = BigWorld.entities.get( spaceEntity.queryTemp( "nvwaEntityID", -1 ) )
			if nvwa is None :
				ERROR_MSG( "----->>> Nvwa hasn't recorded to space!", spaceEntity.id )
			else :
				nvwa.onAICommand( nvwa.id, nvwa.className, self.NVWA_AI_CMD_REVERT )


class CCAssistingNvwa( CopyContent ) :
	"""护神补天进行中"""
	GOBACK_DELAY_ON_STOVE_DESTROYED = 10					# 炉鼎被打碎后多久将玩家传送回女娲处
	TIMER_FLAG_GOBACK = 9999								# 传送玩家到女娲身边的timer标记
	TIMER_FLAG_NORMAL_SPAWN = 9998							# 刷普通怪物的timer标记
	TIMER_FLAG_SPECIAL_SPAWN = 9997							# 刷特殊怪物的timer标记
	STOVE_AI_CMD_REVERT = 1001								# 通知炉鼑恢复的AI指令
	MONSTER_SPAWN_POINTS = ( ( -130.606628, 29.588463, 77.502335 ),( -106.610931, 27.464495, -15.115790 ),\
							( -10.589441, 26.883312, -8.456800 ),( 33.722370, 24.513050, 74.922943 ),\
							( -20.158178, 28.333944, 136.145157 ), )	# 随机刷怪点
	MONSTER1 = {'id':'20151006', 'killAmount':40, 'spawnAmount':60}		# 怪物ID 20151006	魔军
	MONSTER2 = {'id':'20152009', 'killAmount':20, 'spawnAmount':40}		# 怪物ID 20152009	头领
	MONSTER3 = {'id':'20142029', 'killAmount':5, 'spawnAmount':10}		# 怪物ID 20142029	亲卫
	PATROL_BUFF_ID = 299032									# 骑上凤凰飞翔的BuffID
	END_PATROL_SKILL_ID = 322506001							# 移除玩家巡逻buff的技能ID
	#ASSIST_QUEST_ID = 20302022								# 护神补天任务的ID
	ASSIST_STOVE_TASK_INDEX = 18207							# 保护炉鼎的任务目标ID

	def __init__( self ) :
		CopyContent.__init__( self )
		self.key = "assistingNvwa"
		self.val = 1
		self.time_flag = []
		self.intervalTimeDict = {}

	def onContent( self, spaceEntity ):
		"""
		开始执行副本内容
		"""
		print "Start assisting nvwa!"

	#def startSpawningMonsters( self, spaceEntity ) :
		#"""
		#开始刷怪
		#"""
		#spaceEntity.bt_initSpawningMonsters()									# 通知副本实例开始刷怪
		#spaceEntity.bt_addNormalSpawnTimer( self.TIMER_FLAG_NORMAL_SPAWN )		# 普通怪20秒后开始刷出，之后逐次递减2秒刷出
		#spaceEntity.bt_addSpecialSpawnTimer( self.TIMER_FLAG_SPECIAL_SPAWN )	# 特殊怪20秒后开始刷出，之后刷出的怪物死亡了隔20秒再刷下一个

	def startSpawningMonsters( self, spaceEntity ) :
		"""
		开始刷怪
		"""
		for position in spaceEntity.monsterPositions:
			index1 = spaceEntity.monsterPositions.index( position )
			startTime = eval( spaceEntity.startTime[ index1 ] )
			intervalTimeList = list( eval( spaceEntity.intervalTime[ index1 ] ) )
			monsterNumList = eval( spaceEntity.monsterNumLists[ index1 ] )
			monsterIDList = eval( spaceEntity.monsterIDLists[ index1 ] )
			self.time_flag.append( index1 + 1 )
			monsterTimerID = spaceEntity.addTimer ( startTime, 0, self.time_flag[ index1 ] )
			spaceEntity._bt_monsterTimerIDList.append(monsterTimerID)
			totalTime = startTime
			if intervalTimeList == ():
				self.intervalTimeDict[ index1 ] = []
			else:
				self.intervalTimeDict[ index1 ] = intervalTimeList
		self.calMonsterIDAndNum( spaceEntity )
		pass

	def calMonsterIDAndNum( self, spaceEntity ):
		"""
		获取怪物的类型和数量
		"""
		for position in spaceEntity.monsterPositions:
			index = spaceEntity.monsterPositions.index( position )
			monsterNumList = eval( spaceEntity.monsterNumLists[ index ] )
			intervalTimeList = eval( spaceEntity.intervalTime[ index ] )
			monsterIDList = list( eval( spaceEntity.monsterIDLists[ index ] ) )
			length = len( intervalTimeList ) + 1
			for className in monsterIDList:
				index1 = monsterIDList.index( className )
				num = monsterNumList[ index1 ]
				if spaceEntity._bt_monsterDict.has_key( str( className ) ):
					spaceEntity._bt_monsterDict[ str( className ) ] = spaceEntity._bt_monsterDict[ str( className ) ] + num * length
				else:
					spaceEntity._bt_monsterDict[ str( className ) ] = num * length

	def spawnNormalMonster( self, spaceEntity ) :
		"""
		刷普通怪物
		"""
		stoveID = spaceEntity.queryTemp( "stoveEntityID", -1 )					# 这个炉鼎的ID记录是在炉鼎的AI中做的，在脚本是找不到的
		if stoveID == -1 :
			ERROR_MSG( "----->>> Stove hasn't recorded to space when creating normal monster!", spaceEntity.id )
			return
		continueSpawn = False
		spawnPos = random.sample( self.MONSTER_SPAWN_POINTS, 3 )
		# 刷混沌魔军
		if spaceEntity.bt_getMonsterSpawned( self.MONSTER1['id'] ) < self.MONSTER1['spawnAmount'] :	# 判断是否已经到达最大刷怪数量
			continueSpawn = True
			spaceEntity.bt_spawnMonsters( stoveID, self.MONSTER1['id'], spawnPos[:2], 2 )
		# 刷魔誓头领
		if spaceEntity.bt_getMonsterSpawned( self.MONSTER2['id'] ) < self.MONSTER2['spawnAmount'] :	# 判断是否已经到达最大刷怪数量
			continueSpawn = True
			spaceEntity.bt_spawnMonsters( stoveID, self.MONSTER2['id'], spawnPos[-1:] )
		if continueSpawn :																			# 如果需要继续刷怪，则再加Timer
			spaceEntity.bt_addNormalSpawnTimer( self.TIMER_FLAG_NORMAL_SPAWN )

	def spawnSpecialMonster( self, spaceEntity ) :
		"""
		刷能造成更大伤害的怪物
		"""
		stoveID = spaceEntity.queryTemp( "stoveEntityID", -1 )
		if stoveID == -1 :
			ERROR_MSG( "----->>> Stove hasn't recorded to space when creating special monster!", spaceEntity.id )
			return
		if spaceEntity.bt_getMonsterSpawned( self.MONSTER3['id'] ) < self.MONSTER3['spawnAmount'] :
			spawnPos = random.sample( self.MONSTER_SPAWN_POINTS, 1 )
			spaceEntity.bt_spawnMonsters( stoveID, self.MONSTER3['id'], spawnPos )

	def onKillCompleted( self, spaceEntity ) :
		"""
		杀怪完成
		"""
		self.stopSpawning( spaceEntity )
		self.notifyPlayer( spaceEntity, csstatus.PLOT_LV40_ON_ASSIST_SUCCESS )
		spaceEntity.addTimer( self.GOBACK_DELAY_ON_STOVE_DESTROYED, 0, self.TIMER_FLAG_GOBACK )
		for playerMB in spaceEntity._players :						# 触发玩家保护炉鼎的任务目标完成
			player = BigWorld.entities[ playerMB.id ]
			player.client.plotLv40_hideNpcHP()
			if player.has_quest( QUEST_ASSIST_NVWA ) :
				player.questTaskIncreaseState( QUEST_ASSIST_NVWA, self.ASSIST_STOVE_TASK_INDEX )
			else :
				WARNING_MSG( "Kill is completed, but player dosen't have quest %s" % QUEST_ASSIST_NVWA )

	def onStoveDestroyed( self, spaceEntity ) :
		"""
		炉鼎被毁
		"""
		self.stopSpawning( spaceEntity )
		self.notifyPlayer( spaceEntity, csstatus.PLOT_LV40_ON_STOVE_DESTROYED )
		spaceEntity.addTimer( self.GOBACK_DELAY_ON_STOVE_DESTROYED, 0, self.TIMER_FLAG_GOBACK )
		for playerMB in spaceEntity._players :						# 触发玩家保护炉鼎的任务目标失败
			player = BigWorld.entities[ playerMB.id ]
			if player.has_quest( QUEST_ASSIST_NVWA ) :
				for taskIndex in player.getQuestTasks( QUEST_ASSIST_NVWA ).getTasks().iterkeys() :
					player.questTaskFailed( QUEST_ASSIST_NVWA, taskIndex )
			else :
				WARNING_MSG( "Stove is destroyed, but player dosen't have quest %s" % QUEST_ASSIST_NVWA )

	def onQuestAbandoned( self, spaceEntity ) :
		"""
		玩家放弃任务
		"""
		self.revertContent( spaceEntity )
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if player:
				player.client.plotLv40_hideNpcHP()

	def revertContent( self, spaceEntity ) :
		"""
		恢复副本内容到任务开始前的状态
		"""
		self.stopSpawning( spaceEntity )
		stove = BigWorld.entities.get( spaceEntity.queryTemp( "stoveEntityID", -1 ) )
		if stove :													# 通知炉鼑恢复
			stove.onAICommand( stove.id, stove.className, self.STOVE_AI_CMD_REVERT )

	def doConditionChange( self, spaceEntity, params ):
		"""
		条件改变通知
		"""
		CopyContent.doConditionChange( self, spaceEntity, params )
		if params.has_key( "monsterKilled" ) :
			if spaceEntity.bt_isKillCommitted() : return False		# 本次击杀已经完成
			className = params.get( "monsterKilled" )
			spaceEntity.bt_onMonsterKilled( className )
			if self.isKillCompleted( spaceEntity ) :				# 击杀完成
				spaceEntity.bt_commitKill()
				self.onKillCompleted( spaceEntity )
			#elif className == self.MONSTER3["id"] :					# 一个共工亲卫死亡再刷出下一个
				#spaceEntity.bt_addSpecialSpawnTimer( self.TIMER_FLAG_SPECIAL_SPAWN )
		elif params.get( "createProtectCover",False ):				# 保护罩生成
			self.onCreateProtectCover( spaceEntity )
		elif params.get( "stoveHPChange",False ):					# 炉鼎血量改变
			self.onStoveHPChange( spaceEntity )
		elif params.get( "protectCoverHPChange",False ):			# 保护罩血量改变
			self.onProtectCoverHPChange( spaceEntity )
		elif params.get( "stoveDestroyed", False ) :				# 炉鼑被毁，任务失败
			self.onStoveDestroyed( spaceEntity )
		elif params.get( "abandonQuest", False ) :					# 玩家放弃了任务
			self.onQuestAbandoned( spaceEntity )
		elif params.get( "spawnMonsters", False ) :					# 开始刷怪
			self.startSpawningMonsters( spaceEntity )
		elif params.get( "questCommitted", False ) :				# 任务完成
			return True												# 进入下一个关卡
		return False

	def onCreateProtectCover( self, spaceEntity ):
		"""
		保护罩被创建时让客户端显示它和炉鼎的血条
		"""
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if player:
				player.client.plotLv40_showNpcHP()
				self.updateStoveHP( spaceEntity )
				self.updateProtectCoverHP( spaceEntity )

	def onStoveHPChange( self, spaceEntity ):
		"""
		炉鼎血量改变
		"""
		self.updateStoveHP( spaceEntity )

	def onProtectCoverHPChange( self, spaceEntity ):
		"""
		保护罩血量改变
		"""
		self.updateProtectCoverHP( spaceEntity )

	def updateStoveHP( self, spaceEntity ):
		# 更新客户端炉鼎的血条显示
		stove = BigWorld.entities.get( spaceEntity.queryTemp( "stoveEntityID", -1 ) )
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if stove and player:
				HP = stove.HP
				HP_Max = stove.HP_Max
				player.client.plotLv40_stoveHPChange( HP, HP_Max )

	def updateProtectCoverHP( self, spaceEntity ):
		# 更新客户端保护罩的血条显示
		protectCover = BigWorld.entities.get( spaceEntity.queryTemp( "protectCover", -1 ) )
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if protectCover and player:
				HP = protectCover.HP
				HP_Max = protectCover.HP_Max
				player.client.plotLv40_protectCoverHPChange( HP, HP_Max )

	def isKillCompleted( self, spaceEntity ) :
		"""
		击杀目标是否完成
		"""
		#for className in spaceEntity._bt_monsterDict.iterkeys():
			#if spaceEntity.bt_getMonsterKilled( className ) < spaceEntity._bt_monsterDict[ className ]:
				#return False
		#return True
		if spaceEntity.bt_getMonsterKilled( self.MONSTER1['id'] ) < self.MONSTER1['killAmount'] :
			return False
		if spaceEntity.bt_getMonsterKilled( self.MONSTER2['id'] ) < self.MONSTER2['killAmount'] :
			return False
		if spaceEntity.bt_getMonsterKilled( self.MONSTER3['id'] ) < self.MONSTER3['killAmount'] :
			return False
		return True

	def stopSpawning( self, spaceEntity ) :
		"""
		任务失败或者完成后重置关卡
		"""
		spaceEntity.bt_stopSpawnTimer()
		spaceEntity.bt_destroyMonsters()

	def playerGoback( self, spaceEntity ) :
		"""
		玩家传送回女娲处
		"""
		for playerMB in spaceEntity._players :						# 玩家传送回女娲处，移除凤凰Buff
			player = BigWorld.entities[ playerMB.id ]
			if player.findBuffByBuffID( self.PATROL_BUFF_ID ) :
				player.spellTarget( self.END_PATROL_SKILL_ID, player.id )

	def notifyPlayer( self, spaceEntity, statusID ) :
		"""
		通知玩家
		"""
		for playerMB in spaceEntity._players :						# 根据任务状态通知玩家
			player = BigWorld.entities[ playerMB.id ]
			player.statusMessage( statusID )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		player = BigWorld.entities[ baseMailbox.id ]
		if player.findBuffByBuffID( self.PATROL_BUFF_ID ) :
			player.removeBuffByBuffID( self.PATROL_BUFF_ID, ( csdefine.BUFF_INTERRUPT_NONE, ) )
		if player.has_quest( QUEST_ASSIST_NVWA ) and not player.questTaskIsCompleted( QUEST_ASSIST_NVWA ) :
			for taskIndex in player.getQuestTasks( QUEST_ASSIST_NVWA ).getTasks().iterkeys() :
				player.questTaskFailed( QUEST_ASSIST_NVWA, taskIndex )
				player.client.plotLv40_hideNpcHP()
		if len( spaceEntity._players ) == 0 :
			self.revertContent( spaceEntity )

	def onTimer( self, spaceEntity, timerID, userData ) :
		"""
		"""
		CopyContent.onTimer( self, spaceEntity, timerID, userData )
		#if userData == self.TIMER_FLAG_NORMAL_SPAWN :
			#self.spawnNormalMonster( spaceEntity )
		#elif userData == self.TIMER_FLAG_SPECIAL_SPAWN :
			#self.spawnSpecialMonster( spaceEntity )
		if userData == self.TIMER_FLAG_GOBACK :
			self.playerGoback( spaceEntity )
		elif userData in self.time_flag:
			index1 = self.time_flag.index( userData )
			monsterNumList = list( eval( spaceEntity.monsterNumLists[ index1 ] ) )
			monsterIDList = list( eval( spaceEntity.monsterIDLists[ index1 ] ) )
			position = list( eval( spaceEntity.monsterPositions[ index1 ] ) )
			self.spawnNormalMonsters( spaceEntity, monsterNumList, monsterIDList, position )
			if self.intervalTimeDict[ index1 ] != []:
				monsterTimerID = spaceEntity.addTimer( self.intervalTimeDict[ index1 ].pop( 0 ) , 0, userData )
				spaceEntity._bt_monsterTimerIDList.append(monsterTimerID)

	def spawnNormalMonsters( self, spaceEntity, monsterNumList, monsterIDList, position ):
		"""
		刷普通怪物
		"""
		stoveID = spaceEntity.queryTemp( "stoveEntityID", -1 )					# 这个炉鼎的ID记录是在炉鼎的AI中做的，在脚本是找不到的
		if stoveID == -1 :
			ERROR_MSG( "----->>> Stove hasn't recorded to space when creating normal monster!", spaceEntity.id )
			return
		for className in monsterIDList:
			index = monsterIDList.index( className )
			monsterNum = monsterNumList[ index ]
			num = 0
			recorder = spaceEntity._bt_spawnDict.get( str( className ) )
			if recorder is None :
				recorder = []
				spaceEntity._bt_spawnDict[ str( className ) ] = recorder
			while num < monsterNum :
				position[0] = position[0] + random.randint(-5,5)
				position[2] = position[2] + random.randint(-5,5)
				monsterPosition = ( position[0], position[1], position[2] )
				# 召唤怪物的时候对地面进行碰撞检测避免怪物陷入地下
				collide = BigWorld.collide( spaceEntity.spaceID, ( position[0], position[1] + 10, position[2] ), ( position[0], position[1] - 10, position[2] ) )
				if collide != None:
					monsterPosition = ( position[0], collide[0].y, position[2] )
				monster = g_objFactory.getObject( str(className) ).createEntity( spaceEntity.spaceID,\
						monsterPosition, (0,0,0), { "spawnPos" : monsterPosition } )
				monster.changeAttackTarget( stoveID )
				recorder.append( monster.id )
				num = num + 1


class CCKillGonggong( CopyContent ) :
	"""击杀共工"""
	MONSTER_GONGGONG = "20154013"
	MONSTER_SPAWN_POS = (67.571106, 4.680070, 15.905710)
	MONSTER_SPAWN_DIRECTION = (0.000000, 0.000000, -1.521709)

	def __init__( self ) :
		CopyContent.__init__( self )
		self.key = "killGonggong"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		print "Now commit the mission of killing gonggong!"

	def spawnGonggong( self, spaceEntity ) :
		"""
		刷出共工
		"""
		nvwaID = spaceEntity.queryTemp( "nvwaEntityID", -1 )		# 这个女娲的ID记录是在女娲的AI中做的，在脚本是找不到的
		if nvwaID == -1 :
			ERROR_MSG( "----->>> Nvwa hasn't recorded to space when creating gonggong!" )
			return
		monster = g_objFactory.getObject( self.MONSTER_GONGGONG ).createEntity( spaceEntity.spaceID,\
			self.MONSTER_SPAWN_POS, self.MONSTER_SPAWN_DIRECTION, { "spawnPos" : self.MONSTER_SPAWN_POS } )

	def onGonggongKilled( self, spaceEntity ) :
		"""
		共工被杀掉了
		"""
		print "Oh, my god! Gonggong is dead~!"

	def doConditionChange( self, spaceEntity, params ):
		"""
		"""
		CopyContent.doConditionChange( self, spaceEntity, params )
		if params.get( "spawnGonggong", False ) :
			self.spawnGonggong( spaceEntity )
		elif params.get( "gonggongKilled", False ) :
			self.onGonggongKilled( spaceEntity )
		elif params.get( "questCommitted", False ) :
			return True
		return False


class SpaceCopyPlotLv40( SpaceCopyTemplate ) :
	"""
	"""
	def __init__( self ) :
		SpaceCopyTemplate.__init__( self )

	def canUseSkill( self, playerEntity, skillID ) :
		"""
		使用空间技能
		"""
		return True

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		SpaceCopyTemplate.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "monsterPositions", section.readString("monsterPositions").split(":") )
		self.setEntityProperty( "startTime", section.readString("startTime").split(":") )
		self.setEntityProperty( "intervalTime", section.readString("intervalTime").split(":") )
		self.setEntityProperty( "monsterNumLists", section.readString("monsterNumLists").split(":") )
		self.setEntityProperty( "monsterIDLists", section.readString("monsterIDLists").split(":") )


	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTemplate.load( self, section )
		#self._playerAoI = section.readFloat( "playerAoI", csconst.ROLE_AOI_RADIUS ) # 已经作为空间的通用设置，在space中进行设置
		#self.onLoadEntityProperties_( section )			# 此处为重复调用，加以注释 add by chenweilan

	def initContent( self ) :
		self.contents.append( CCGatherStones() )
		self.contents.append( CCAssistingNvwa())
		self.contents.append( CCKillGonggong() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )

	def onConditionChange( self, selfEntity, params ) :
		"""
		条件改变
		"""
		if params.has_key( "copyContentIndex" ) :							# 设置副本的当前进度
			selfEntity.setTemp( "contentIndex", int( params[ "copyContentIndex" ] ) )
		SpaceCopyTemplate.onConditionChange( self, selfEntity, params )

	def onEnterCommon( self, selfEntity, baseMailbox, params ) :
		"""
		玩家进入副本
		"""
		if self.getEntityProperty("monsterPositions") != None:
			selfEntity.monsterPositions = self.getEntityProperty("monsterPositions")
			selfEntity.startTime = self.getEntityProperty("startTime")
			selfEntity.intervalTime = self.getEntityProperty("intervalTime")
			selfEntity.monsterNumLists = self.getEntityProperty("monsterNumLists")
			selfEntity.monsterIDLists = self.getEntityProperty("monsterIDLists")
		player = BigWorld.entities.get( baseMailbox.id )
		if selfEntity.queryTemp("firstPlayer", 0 ) == 0 :					# 第一次进入副本，根据任务情况来设置副本进度
			if player.has_quest( QUEST_GATHER_STONES ) :
				selfEntity.setTemp( "contentIndex", 0 )
			elif player.has_quest( QUEST_ASSIST_NVWA ) :
				selfEntity.setTemp( "contentIndex", 1 )
			elif player.has_quest( QUEST_KILL_GONGGONG ) :
				selfEntity.setTemp( "contentIndex", 2 )
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ) :
		"""
		玩家离开副本
		"""
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
