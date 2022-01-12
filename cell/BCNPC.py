# -*- coding: gb18030 -*-
#
# 变身大赛NPC 2009-01-17 SongPeifang
#

from bwdebug import *
from NPC import NPC
import random
import csdefine
import csconst
import csstatus
import cschannel_msgs

SAY_CHANGE_MODEL	= 0
CHANGE_TO_MODEL		= 1
CHANGE_LIE_MODEL	= 2
WAIT_TO_CHECK		= 3
CHECK_MEMBERS 		= 4

class BCNPC( NPC ):
	"""
	变身大赛NPC
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_NPC )
		self._canLogin	= False	# 能否报名
		self._members	= {}	# 变身大赛参赛者{参赛者databaseID:成功完成次数}
		self._passMembers = []	# 用来记录过关的玩家的领奖情况
		self._currentCount = 0	# 当前是第几次变身
		self._animals = cschannel_msgs.BCNPC_S_1
		self.modelNumberStored = self.modelNumber
		self.modelScaleStored = self.modelScale

	def loginBCGame( self, player ):
		"""
		报名参加变身大赛
		"""
		self._members[ player.databaseID ] = 0
		self.base.getLoginMembers( len( self._members ) )

	def getLoginState( self, loginState ):
		"""
		Define Method.
		从base上取得是否可以报名
		"""
		self._canLogin = loginState

	def isPlayerLogin( self, player ):
		"""
		取得玩家报名状态
		"""
		return self._members.has_key( player.databaseID )

	def canLogin( self ):
		"""
		是否可以报名
		"""
		return self._canLogin

	def hasMembers( self ):
		"""
		是否有玩家参加
		"""
		return len( self._members ) != 0

	def bcGameStart( self ):
		"""
		Define Method.
		变身大赛正式开始！
		"""
		self.say( cschannel_msgs.BCNPC_1 )
		self.addTimer( 2, 0, SAY_CHANGE_MODEL )

	def sayChangeModel( self ):
		"""
		NPC告诉玩家自己要变成什么
		"""
		self._currentCount += 1
		if len( self._members ) <= 0:
			self.say( cschannel_msgs.BCNPC_2 )
			self._canLogin	= False
			self._currentCount = 0
			return
		elif self._currentCount > 20:
			count = 0
			for i in self._members:
				if self._members[i] == 20:
					self._passMembers.append( i )
					count += 1
			self.say( cschannel_msgs.BCNPC_3 % count )
			
			self._members.clear()
			self._canLogin	= False
			self._currentCount = 0
			return
		animalIndex = random.randint( 0, len( self._animals ) - 1 )
		self._animalKey = self._animals.keys()[ animalIndex ]
		animal = self._animals[ self._animalKey ]
		self.say( cschannel_msgs.BCNPC_4 % animal )
		sayWait = self.afterSayWaitTime()
		honest = 0.7	# 诚实几率是70%,说谎几率是30%
		r = random.random()
		if r <= honest:
			self.addTimer( sayWait, 0, CHANGE_TO_MODEL )
		else:
			newIndex = self.getDiffIndex( animalIndex )
			self._animalKey = self._animals.keys()[ newIndex ]
			self.addTimer( sayWait, 0, CHANGE_LIE_MODEL )

	def changeBody( self ):
		"""
		NPC变成某模型
		"""
		self.modelScale = 2.0
		self.modelNumber = self._animalKey
		changeCheckWaitTime = self.afterChangeCheckTime()
		members = self.entitiesInRangeExt( 50, "Role", self.position )
		for p in members:
			if p.databaseID in self._members:
				p.client.playIntonateBar( changeCheckWaitTime )
				p.statusMessage( csstatus.SKILL_BODY_CHANGING_CHECK )
		self.addTimer( changeCheckWaitTime, 0, WAIT_TO_CHECK )

	def changeLieBody( self ):
		"""
		NPC说谎的变成某模型
		"""
		self.say( cschannel_msgs.BCNPC_5 )
		self.changeBody()

	def checkMembers( self ):
		"""
		NPC检查周围50米内玩家变身情况
		"""
		members = self.entitiesInRangeExt( 50, "Role", self.position )
		for p in members:
			if p.databaseID in self._members:
				if p.getCurrentBodyNumber() == self.modelNumber:
					self._members[p.databaseID] += 1
					p.addExp( self.getSuccessExpRwd( p.level, self._members[p.databaseID] ), csdefine.CHANGE_EXP_BCNPC )
					p.statusMessage( csstatus.BC_CHANGE_BODY_SUCCESSFUL )
				else:
					self._members[p.databaseID] = 0
					p.statusMessage( csstatus.BC_CHANGE_BODY_FAILED )
			if self._currentCount >= 20:
				p.statusMessage( csstatus.SKILL_BODY_CHANGE_FINISH )
				
		checkWaitTime = self.afterCheckWaitTime()		# 检查完之后休息多长时间进行下一次变身
		self.modelScale = self.modelScaleStored			# 检查完之后，恢复NPC的模型为原始尺寸
		self.modelNumber = self.modelNumberStored		# 检查完之后，恢复NPC的模型为原始模型
		self.addTimer( checkWaitTime, 0, SAY_CHANGE_MODEL )	# 在checkWaitTime时间后进行下一次变身

	def onTimer( self, id, userArg ):
		"""
		通知所有玩家变身大赛开始
		"""
		NPC.onTimer( self, id, userArg )
		if userArg == SAY_CHANGE_MODEL:
			# 说话告诉玩家“我要变成XXX”
			self.sayChangeModel()
		elif userArg == CHANGE_TO_MODEL:
			# NPC进行变身，换模型
			self.changeBody()
		elif userArg == CHANGE_LIE_MODEL:
			# NPC进行变身，换模型，但是换的模型并不是说话要变的模型
			self.changeLieBody()
		elif userArg == WAIT_TO_CHECK:
			# 检查哪些玩家通过，哪些玩家被淘汰
			self.checkMembers()

	def getDiffIndex( self, index ):
		"""
		取得一个不同的模型索引
		"""
		animalIndex = index
		while( animalIndex == index ):
			# 既然是说谎，那么一定要取出一个不同的模型
			animalIndex = random.randint( 0, len( self._animals ) - 1 )
		return animalIndex

	def afterSayWaitTime( self ):
		"""
		NPC发言后等待多长时间进行变身
		"""
		if self._currentCount >= 1 and self._currentCount <= 8:
			# 1-8次 发言后5秒可以变身
			return 5
		elif self._currentCount >= 9 and self._currentCount <= 15:
			# 9-15次 发言后5秒可以变身
			return 5
		else:
			# 16-20次 发言后2秒可以变身
			return 2

	def afterChangeCheckTime( self ):
		"""
		NPC变身后等待多长时间进行检查、淘汰玩家
		"""
		if self._currentCount >= 1 and self._currentCount <= 8:
			# 1-8次 变身后5秒开始检查玩家变身情况
			return 5
		elif self._currentCount >= 9 and self._currentCount <= 15:
			# 9-15次 变身后3秒开始检查玩家变身情况
			return 3
		else:
			# 16-20次 变身后3秒开始检查玩家变身情况
			return 3

	def afterCheckWaitTime( self ):
		"""
		NPC检查、淘汰完玩家后，等待多长时间进行下一次变身
		"""
		if self._currentCount >= 1 and self._currentCount <= 8:
			# 1-8次 检查后休息5秒开始下一次变身说话
			return 5
		elif self._currentCount >= 9 and self._currentCount <= 15:
			# 9-15次 检查后休息3秒开始下一次变身说话
			return 3
		else:
			# 16-20次 检查后休息1秒开始下一次变身说话
			return 1

	def clearPassMembers( self, player = None ):
		"""
		清除领取过奖励的玩家
		"""
		if player == None:
			self._passMembers = []
		elif player.databaseID in self._passMembers:
			self._passMembers.remove( player.databaseID )

	def getSuccessExpRwd( self, level, cCount ):
		"""
		每次变身变对，获得经验奖励
		(LV+23) * 变对轮数 * 5
		"""
		return csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_BIAN_SHEN_DA_SAI, level, cCount )