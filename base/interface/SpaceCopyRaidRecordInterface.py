# -*- coding: gb18030 -*-

# 定义副本raid记录的接口，by ganjinxing
from bwdebug import INFO_MSG
from BaseSpaceCopyFormulas import spaceCopyFormulas


class SpaceCopyRaidRecordInterface :

	def __init__( self ) :
		self.bossesTotal = spaceCopyFormulas.totalBossesOf( self.className )	# boss总数
		self.bossesKilled = 0						# boss已击杀数量
		self.isRaidFinish = False					# 副本是否已经完成

	def queryBossesKilled( self, querist, userData ) :
		"""
		<Define method>
		查询boss的击杀数量
		@type	querist : BASE MAILBOX
		@param	querist : 查询者，必须带有定义方法onQueryBossesKilledCallback
		@type	userData : INT32
		@param	userData : 查询者回调的数据
		"""
		querist.onQueryBossesKilledCallback( userData, self.bossesKilled )

	def setBossesTotal( self, bossesTotal ) :
		"""
		"""
		self.bossesTotal = bossesTotal

	def incBossesKilled( self ) :
		"""
		<Define method>
		增加boss击杀记录
		"""
		self.bossesKilled = min( self.bossesKilled + 1, self.bossesTotal )

	def decBossesKilled( self ) :
		"""
		减少boss击杀记录
		"""
		self.bossesKilled = max( self.bossesKilled - 1, 0 )

	def setRaidFinish( self, finish ) :
		"""
		<Define method>
		设置副本Raid完成标记
		@type	finish : BOOL
		@param	finish : 副本是否已打完
		"""
		self.isRaidFinish = finish
		if finish and self.domainMB :
			self.domainMB.notifyTeamRaidFinished( self.spaceNumber )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间，需要根据副本boss的击杀情况给予玩家
		相应的提示，并让玩家选择是继续副本还是离开副本。
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		baseMailbox.cell.onEnterMatchedCopy( self.className, self.bossesKilled )

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		玩家离开空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onLeave时的一些额外参数
		@type params: py_dict
		"""
		pass
