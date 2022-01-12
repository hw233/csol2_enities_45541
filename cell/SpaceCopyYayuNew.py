# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const


DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#玩家全部离开副本后，隔多久副本才删除

GOD_WEAPON_QUEST_YAYU		 = 40202002	# 神器任务猰貐ID

class SpaceCopyYayuNew( SpaceCopy ):

	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.spawnDict = {}					# 已经创建的怪物ID { className: [id1, id2, …… ]， …… }

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.copyDataInit( baseMailbox, params )
			self.setTemp( "firstEnter", True )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )


	def copyDataInit( self, baseMailbox, params ):
		"""
		副本数据方面的初始化
		"""
		BigWorld.globalData['Yayu_%i' % params['teamID'] ] = True
		self.setTemp('globalkey','Yayu_%i' % params['teamID'])

		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YAYU_NEW_HP, 50 )				# 猰貐血量
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME, "" )			# 下一阶段剩余时间
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )				# 剩余Boss
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_BATCH, 0 )						# 当前阶段

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
			8: 猰貐血量百分比
			11:拯救猰貐当前阶段
			12:下一波怪物开始时间(新版猰貐)
			13:猰貐血量百分比
			14:圆环血条
		]
		"""
		# 显示剩余小怪，剩余BOSS。
		return [ 3,11, 12, 14, 13 ]

	def onYayuDie( self ):
		"""
		define method
		"""
		self.getScript().onYayuDie( self )


	def onYayuHPChange( self, hp, hp_Max ):
		"""
		define method
		"""
		self.getScript().onYayuHPChange( self, hp, hp_Max )

	def onYayuMonsterBorn( self, className, id ):
		"""
		define method
		"""
		if not self.spawnDict.has_key( className ):
			self.spawnDict[ className ] = []
		self.spawnDict[ className ].append( id )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )

		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]


	def onTimer( self, id, userArg ):
		"""
		覆盖底层的onTimer()处理机制
		"""
		SpaceCopy.onTimer( self, id, userArg )

	def onGodWeaponYayuFin( self ):
		"""
		define method
		完成神器任务，猰貐HP剩余90%以上
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_YAYU, 1 )

	def destroyMonsters( self ) :
		"""
		销毁所有刷出来的怪物
		"""
		for monsters in self.spawnDict.itervalues() :
			for m_id in monsters :
				monster = BigWorld.entities.get( m_id )
				if monster:
					monster.destroy()
		self.spawnDict.clear()
