# -*- coding: gb18030 -*-

# 40 级剧情副本
# by ganjinxing

# bigworld
import BigWorld
# common
import csdefine
from bwdebug import *
# cell
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory


class SpaceCopyPlotLv40( SpaceCopy ) :

	def __init__( self ):
		SpaceCopy.__init__( self )
		self._bt_killCommit = False								# 用这个标记来防止重复完成杀怪( 护神补天任务相关的变量 ) bt == 补天（ bu tian ）
		self._bt_killDict = {}									# 保存已击杀怪物的数量( 护神补天任务相关的变量 )
		self._bt_spawnDict = {}									# 保存已创建怪物的数量( 护神补天任务相关的变量 )
		self._bt_normalTimerID = 0								# 刷普通怪的TimerID( 护神补天任务相关的变量 )
		self._bt_specialTimerID = 0								# 刷特殊怪的TimerID( 护神补天任务相关的变量 )
		self._bt_normalSpawnCounter = 20						# 普通怪20秒后开始刷出，之后逐次递减2秒刷出，因此使用一个计数器来记录
		self.monsterPositions = []
		self.startTime = []
		self.intervalTime = []
		self.monsterNumLists = []
		self.monsterIDLists = []
		self._bt_monsterTimerIDList = []
		self._bt_monsterDict = {}

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s enter copy plot lv40." % entity.getName() )
		else :
			INFO_MSG( "Something enter copy plot lv40." )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s leave copy plot lv40." % entity.getName() )
		else :
			INFO_MSG( "Something leave copy plot lv40." )

	# ----------------------------------------------------------------
	# 护神补天任务相关的方法
	# ----------------------------------------------------------------
	def bt_initSpawningMonsters( self ) :
		"""
		刷怪前准备
		"""
		self._bt_killCommit = False							# 重置击杀完成标记
		self._bt_killDict.clear()								# 重置杀怪计数
		self._bt_spawnDict.clear()								# 重置刷怪记录
		self._bt_normalSpawnCounter = 20						# 重置普通刷怪的计数器

	def bt_addNormalSpawnTimer( self, userData=0 ) :
		"""
		刷普通怪物，每次减少2秒刷怪时间
		"""
		self._bt_normalSpawnCounter = max( 6, self._bt_normalSpawnCounter )
		self._bt_normalTimerID = self.addTimer( self._bt_normalSpawnCounter, 0.0, userData )
		self._bt_normalSpawnCounter -= 2

	def bt_addSpecialSpawnTimer( self, userData=0 ) :
		"""
		刷特殊怪物，前一个死亡20秒后刷下一个，在script中控制
		"""
		self._bt_specialTimerID = self.addTimer( 20, 0.0, userData )

	def bt_stopSpawnTimer( self ) :
		"""
		停止刷怪的Timer
		"""
		#self.cancel( self._bt_normalTimerID )
		#self.cancel( self._bt_specialTimerID )
		for monsterTimerID in self._bt_monsterTimerIDList:
			self.cancel( monsterTimerID )

	def bt_spawnMonsters( self, enemyID, className, pos, amount = 1 ) :
		"""
		"""
		recorder = self._bt_spawnDict.get( className )
		if recorder is None :
			recorder = []
			self._bt_spawnDict[className] = recorder
		while amount > 0 :
			amount -= 1
			monster = g_objFactory.getObject( className ).createEntity( self.spaceID,\
				pos[amount], (0,0,0), { "spawnPos" : pos[amount] } )
			monster.changeAttackTarget( enemyID )
			recorder.append( monster.id )

	def bt_getMonsterSpawned( self, className ) :
		"""
		获取创建的怪物数量
		"""
		return len( self._bt_spawnDict.get( className, [] ) )

	# -------------------------------------------------
	def bt_getMonsterKilled( self, className ) :
		"""
		获取某个怪物的当前击杀数量
		"""
		return self._bt_killDict.get( className, 0 )

	def bt_onMonsterKilled( self, className ) :
		"""
		某个怪物被杀死后通知副本
		"""
		self._bt_killDict[className] = self._bt_killDict.get( className, 0 ) + 1

	def bt_isKillCommitted( self ) :
		"""
		击杀是否已经完成
		"""
		return self._bt_killCommit

	def bt_commitKill( self ) :
		"""
		标记当前为击杀完成状态
		"""
		self._bt_killCommit = True

	# -------------------------------------------------
	def bt_destroyMonsters( self ) :
		"""
		销毁所有刷出来的怪物
		"""
		for monsters in self._bt_spawnDict.itervalues() :
			for m_id in monsters :
				monster = BigWorld.entities.get( m_id )
				if monster : monster.destroy()
