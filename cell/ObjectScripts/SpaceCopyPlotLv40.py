# -*- coding: gb18030 -*-

# 40�����鸱��
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
	"""�ɼ���ɫʯ"""
	NVWA_AI_CMD_REVERT = 200										# �������ݻָ���ָ��

	def __init__( self ) :
		CopyContent.__init__( self )
		self.key = "gatherStones"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		��ʼִ�и�������
		"""
		print "Enter gathering stones!"

	def doConditionChange( self, spaceEntity, params ) :
		"""
		"""
		if params.get( "questCommitted", False ) :					# �������
			return True
		return False

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ�뿪
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
	"""�����������"""
	GOBACK_DELAY_ON_STOVE_DESTROYED = 10					# ¯����������ý���Ҵ��ͻ�Ů洴�
	TIMER_FLAG_GOBACK = 9999								# ������ҵ�Ů���ߵ�timer���
	TIMER_FLAG_NORMAL_SPAWN = 9998							# ˢ��ͨ�����timer���
	TIMER_FLAG_SPECIAL_SPAWN = 9997							# ˢ��������timer���
	STOVE_AI_CMD_REVERT = 1001								# ֪ͨ¯���ָ���AIָ��
	MONSTER_SPAWN_POINTS = ( ( -130.606628, 29.588463, 77.502335 ),( -106.610931, 27.464495, -15.115790 ),\
							( -10.589441, 26.883312, -8.456800 ),( 33.722370, 24.513050, 74.922943 ),\
							( -20.158178, 28.333944, 136.145157 ), )	# ���ˢ�ֵ�
	MONSTER1 = {'id':'20151006', 'killAmount':40, 'spawnAmount':60}		# ����ID 20151006	ħ��
	MONSTER2 = {'id':'20152009', 'killAmount':20, 'spawnAmount':40}		# ����ID 20152009	ͷ��
	MONSTER3 = {'id':'20142029', 'killAmount':5, 'spawnAmount':10}		# ����ID 20142029	����
	PATROL_BUFF_ID = 299032									# ���Ϸ�˷����BuffID
	END_PATROL_SKILL_ID = 322506001							# �Ƴ����Ѳ��buff�ļ���ID
	#ASSIST_QUEST_ID = 20302022								# �����������ID
	ASSIST_STOVE_TASK_INDEX = 18207							# ����¯��������Ŀ��ID

	def __init__( self ) :
		CopyContent.__init__( self )
		self.key = "assistingNvwa"
		self.val = 1
		self.time_flag = []
		self.intervalTimeDict = {}

	def onContent( self, spaceEntity ):
		"""
		��ʼִ�и�������
		"""
		print "Start assisting nvwa!"

	#def startSpawningMonsters( self, spaceEntity ) :
		#"""
		#��ʼˢ��
		#"""
		#spaceEntity.bt_initSpawningMonsters()									# ֪ͨ����ʵ����ʼˢ��
		#spaceEntity.bt_addNormalSpawnTimer( self.TIMER_FLAG_NORMAL_SPAWN )		# ��ͨ��20���ʼˢ����֮����εݼ�2��ˢ��
		#spaceEntity.bt_addSpecialSpawnTimer( self.TIMER_FLAG_SPECIAL_SPAWN )	# �����20���ʼˢ����֮��ˢ���Ĺ��������˸�20����ˢ��һ��

	def startSpawningMonsters( self, spaceEntity ) :
		"""
		��ʼˢ��
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
		��ȡ��������ͺ�����
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
		ˢ��ͨ����
		"""
		stoveID = spaceEntity.queryTemp( "stoveEntityID", -1 )					# ���¯����ID��¼����¯����AI�����ģ��ڽű����Ҳ�����
		if stoveID == -1 :
			ERROR_MSG( "----->>> Stove hasn't recorded to space when creating normal monster!", spaceEntity.id )
			return
		continueSpawn = False
		spawnPos = random.sample( self.MONSTER_SPAWN_POINTS, 3 )
		# ˢ����ħ��
		if spaceEntity.bt_getMonsterSpawned( self.MONSTER1['id'] ) < self.MONSTER1['spawnAmount'] :	# �ж��Ƿ��Ѿ��������ˢ������
			continueSpawn = True
			spaceEntity.bt_spawnMonsters( stoveID, self.MONSTER1['id'], spawnPos[:2], 2 )
		# ˢħ��ͷ��
		if spaceEntity.bt_getMonsterSpawned( self.MONSTER2['id'] ) < self.MONSTER2['spawnAmount'] :	# �ж��Ƿ��Ѿ��������ˢ������
			continueSpawn = True
			spaceEntity.bt_spawnMonsters( stoveID, self.MONSTER2['id'], spawnPos[-1:] )
		if continueSpawn :																			# �����Ҫ����ˢ�֣����ټ�Timer
			spaceEntity.bt_addNormalSpawnTimer( self.TIMER_FLAG_NORMAL_SPAWN )

	def spawnSpecialMonster( self, spaceEntity ) :
		"""
		ˢ����ɸ����˺��Ĺ���
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
		ɱ�����
		"""
		self.stopSpawning( spaceEntity )
		self.notifyPlayer( spaceEntity, csstatus.PLOT_LV40_ON_ASSIST_SUCCESS )
		spaceEntity.addTimer( self.GOBACK_DELAY_ON_STOVE_DESTROYED, 0, self.TIMER_FLAG_GOBACK )
		for playerMB in spaceEntity._players :						# ������ұ���¯��������Ŀ�����
			player = BigWorld.entities[ playerMB.id ]
			player.client.plotLv40_hideNpcHP()
			if player.has_quest( QUEST_ASSIST_NVWA ) :
				player.questTaskIncreaseState( QUEST_ASSIST_NVWA, self.ASSIST_STOVE_TASK_INDEX )
			else :
				WARNING_MSG( "Kill is completed, but player dosen't have quest %s" % QUEST_ASSIST_NVWA )

	def onStoveDestroyed( self, spaceEntity ) :
		"""
		¯������
		"""
		self.stopSpawning( spaceEntity )
		self.notifyPlayer( spaceEntity, csstatus.PLOT_LV40_ON_STOVE_DESTROYED )
		spaceEntity.addTimer( self.GOBACK_DELAY_ON_STOVE_DESTROYED, 0, self.TIMER_FLAG_GOBACK )
		for playerMB in spaceEntity._players :						# ������ұ���¯��������Ŀ��ʧ��
			player = BigWorld.entities[ playerMB.id ]
			if player.has_quest( QUEST_ASSIST_NVWA ) :
				for taskIndex in player.getQuestTasks( QUEST_ASSIST_NVWA ).getTasks().iterkeys() :
					player.questTaskFailed( QUEST_ASSIST_NVWA, taskIndex )
			else :
				WARNING_MSG( "Stove is destroyed, but player dosen't have quest %s" % QUEST_ASSIST_NVWA )

	def onQuestAbandoned( self, spaceEntity ) :
		"""
		��ҷ�������
		"""
		self.revertContent( spaceEntity )
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if player:
				player.client.plotLv40_hideNpcHP()

	def revertContent( self, spaceEntity ) :
		"""
		�ָ��������ݵ�����ʼǰ��״̬
		"""
		self.stopSpawning( spaceEntity )
		stove = BigWorld.entities.get( spaceEntity.queryTemp( "stoveEntityID", -1 ) )
		if stove :													# ֪ͨ¯���ָ�
			stove.onAICommand( stove.id, stove.className, self.STOVE_AI_CMD_REVERT )

	def doConditionChange( self, spaceEntity, params ):
		"""
		�����ı�֪ͨ
		"""
		CopyContent.doConditionChange( self, spaceEntity, params )
		if params.has_key( "monsterKilled" ) :
			if spaceEntity.bt_isKillCommitted() : return False		# ���λ�ɱ�Ѿ����
			className = params.get( "monsterKilled" )
			spaceEntity.bt_onMonsterKilled( className )
			if self.isKillCompleted( spaceEntity ) :				# ��ɱ���
				spaceEntity.bt_commitKill()
				self.onKillCompleted( spaceEntity )
			#elif className == self.MONSTER3["id"] :					# һ����������������ˢ����һ��
				#spaceEntity.bt_addSpecialSpawnTimer( self.TIMER_FLAG_SPECIAL_SPAWN )
		elif params.get( "createProtectCover",False ):				# ����������
			self.onCreateProtectCover( spaceEntity )
		elif params.get( "stoveHPChange",False ):					# ¯��Ѫ���ı�
			self.onStoveHPChange( spaceEntity )
		elif params.get( "protectCoverHPChange",False ):			# ������Ѫ���ı�
			self.onProtectCoverHPChange( spaceEntity )
		elif params.get( "stoveDestroyed", False ) :				# ¯�����٣�����ʧ��
			self.onStoveDestroyed( spaceEntity )
		elif params.get( "abandonQuest", False ) :					# ��ҷ���������
			self.onQuestAbandoned( spaceEntity )
		elif params.get( "spawnMonsters", False ) :					# ��ʼˢ��
			self.startSpawningMonsters( spaceEntity )
		elif params.get( "questCommitted", False ) :				# �������
			return True												# ������һ���ؿ�
		return False

	def onCreateProtectCover( self, spaceEntity ):
		"""
		�����ֱ�����ʱ�ÿͻ�����ʾ����¯����Ѫ��
		"""
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if player:
				player.client.plotLv40_showNpcHP()
				self.updateStoveHP( spaceEntity )
				self.updateProtectCoverHP( spaceEntity )

	def onStoveHPChange( self, spaceEntity ):
		"""
		¯��Ѫ���ı�
		"""
		self.updateStoveHP( spaceEntity )

	def onProtectCoverHPChange( self, spaceEntity ):
		"""
		������Ѫ���ı�
		"""
		self.updateProtectCoverHP( spaceEntity )

	def updateStoveHP( self, spaceEntity ):
		# ���¿ͻ���¯����Ѫ����ʾ
		stove = BigWorld.entities.get( spaceEntity.queryTemp( "stoveEntityID", -1 ) )
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if stove and player:
				HP = stove.HP
				HP_Max = stove.HP_Max
				player.client.plotLv40_stoveHPChange( HP, HP_Max )

	def updateProtectCoverHP( self, spaceEntity ):
		# ���¿ͻ��˱����ֵ�Ѫ����ʾ
		protectCover = BigWorld.entities.get( spaceEntity.queryTemp( "protectCover", -1 ) )
		for playerMB in spaceEntity._players:
			player = BigWorld.entities[ playerMB.id ]
			if protectCover and player:
				HP = protectCover.HP
				HP_Max = protectCover.HP_Max
				player.client.plotLv40_protectCoverHPChange( HP, HP_Max )

	def isKillCompleted( self, spaceEntity ) :
		"""
		��ɱĿ���Ƿ����
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
		����ʧ�ܻ�����ɺ����ùؿ�
		"""
		spaceEntity.bt_stopSpawnTimer()
		spaceEntity.bt_destroyMonsters()

	def playerGoback( self, spaceEntity ) :
		"""
		��Ҵ��ͻ�Ů洴�
		"""
		for playerMB in spaceEntity._players :						# ��Ҵ��ͻ�Ů洴����Ƴ����Buff
			player = BigWorld.entities[ playerMB.id ]
			if player.findBuffByBuffID( self.PATROL_BUFF_ID ) :
				player.spellTarget( self.END_PATROL_SKILL_ID, player.id )

	def notifyPlayer( self, spaceEntity, statusID ) :
		"""
		֪ͨ���
		"""
		for playerMB in spaceEntity._players :						# ��������״̬֪ͨ���
			player = BigWorld.entities[ playerMB.id ]
			player.statusMessage( statusID )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ�뿪
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
		ˢ��ͨ����
		"""
		stoveID = spaceEntity.queryTemp( "stoveEntityID", -1 )					# ���¯����ID��¼����¯����AI�����ģ��ڽű����Ҳ�����
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
				# �ٻ������ʱ��Ե��������ײ����������������
				collide = BigWorld.collide( spaceEntity.spaceID, ( position[0], position[1] + 10, position[2] ), ( position[0], position[1] - 10, position[2] ) )
				if collide != None:
					monsterPosition = ( position[0], collide[0].y, position[2] )
				monster = g_objFactory.getObject( str(className) ).createEntity( spaceEntity.spaceID,\
						monsterPosition, (0,0,0), { "spawnPos" : monsterPosition } )
				monster.changeAttackTarget( stoveID )
				recorder.append( monster.id )
				num = num + 1


class CCKillGonggong( CopyContent ) :
	"""��ɱ����"""
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
		ˢ������
		"""
		nvwaID = spaceEntity.queryTemp( "nvwaEntityID", -1 )		# ���Ů洵�ID��¼����Ů洵�AI�����ģ��ڽű����Ҳ�����
		if nvwaID == -1 :
			ERROR_MSG( "----->>> Nvwa hasn't recorded to space when creating gonggong!" )
			return
		monster = g_objFactory.getObject( self.MONSTER_GONGGONG ).createEntity( spaceEntity.spaceID,\
			self.MONSTER_SPAWN_POS, self.MONSTER_SPAWN_DIRECTION, { "spawnPos" : self.MONSTER_SPAWN_POS } )

	def onGonggongKilled( self, spaceEntity ) :
		"""
		������ɱ����
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
		ʹ�ÿռ似��
		"""
		return True

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		SpaceCopyTemplate.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "monsterPositions", section.readString("monsterPositions").split(":") )
		self.setEntityProperty( "startTime", section.readString("startTime").split(":") )
		self.setEntityProperty( "intervalTime", section.readString("intervalTime").split(":") )
		self.setEntityProperty( "monsterNumLists", section.readString("monsterNumLists").split(":") )
		self.setEntityProperty( "monsterIDLists", section.readString("monsterIDLists").split(":") )


	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopyTemplate.load( self, section )
		#self._playerAoI = section.readFloat( "playerAoI", csconst.ROLE_AOI_RADIUS ) # �Ѿ���Ϊ�ռ��ͨ�����ã���space�н�������
		#self.onLoadEntityProperties_( section )			# �˴�Ϊ�ظ����ã�����ע�� add by chenweilan

	def initContent( self ) :
		self.contents.append( CCGatherStones() )
		self.contents.append( CCAssistingNvwa())
		self.contents.append( CCKillGonggong() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )

	def onConditionChange( self, selfEntity, params ) :
		"""
		�����ı�
		"""
		if params.has_key( "copyContentIndex" ) :							# ���ø����ĵ�ǰ����
			selfEntity.setTemp( "contentIndex", int( params[ "copyContentIndex" ] ) )
		SpaceCopyTemplate.onConditionChange( self, selfEntity, params )

	def onEnterCommon( self, selfEntity, baseMailbox, params ) :
		"""
		��ҽ��븱��
		"""
		if self.getEntityProperty("monsterPositions") != None:
			selfEntity.monsterPositions = self.getEntityProperty("monsterPositions")
			selfEntity.startTime = self.getEntityProperty("startTime")
			selfEntity.intervalTime = self.getEntityProperty("intervalTime")
			selfEntity.monsterNumLists = self.getEntityProperty("monsterNumLists")
			selfEntity.monsterIDLists = self.getEntityProperty("monsterIDLists")
		player = BigWorld.entities.get( baseMailbox.id )
		if selfEntity.queryTemp("firstPlayer", 0 ) == 0 :					# ��һ�ν��븱��������������������ø�������
			if player.has_quest( QUEST_GATHER_STONES ) :
				selfEntity.setTemp( "contentIndex", 0 )
			elif player.has_quest( QUEST_ASSIST_NVWA ) :
				selfEntity.setTemp( "contentIndex", 1 )
			elif player.has_quest( QUEST_KILL_GONGGONG ) :
				selfEntity.setTemp( "contentIndex", 2 )
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ) :
		"""
		����뿪����
		"""
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
