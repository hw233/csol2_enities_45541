# -*- coding: gb18030 -*-
from bwdebug import *
import BigWorld
import Math
from SpaceCopy import SpaceCopy
import random
from TimeString import TimeString


class SpaceCopyLiuWangMu( SpaceCopy ):
	# 六王墓
	def __init__( self ):
		SpaceCopy.__init__( self )
	#	self.base.spawnMonster()
			

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		if self.getScript().isViewer( params ):
			self.onEnterViewer( baseMailbox, params)
		else:
			self.onEnterCommon( baseMailbox, params )
 		DEBUG_MSG("player %d enter liuwangmu"%baseMailbox.id)
		baseMailbox.cell.lockPkMode()
		baseMailbox.cell.setTemp( "copy_space_lock_pkmode", 4 ) #帮会pk模式
		
		#	baseMailbox.gotoSpace( baseMailbox.reviveSpace, baseMailbox.revivePosition, baseMailbox.reviveDirection )

	def rankList(self, msg):
		"""
		define method
		"""
		for player in self._players:
			#msg = [self.getMaxDamagePlayers(10), self.getMaxDamageTongs(3), self.playerNameTotongName]
			player.client.showRankList(msg)
			INFO_MSG("LIU_WANG_MU_ACTIVITY_RESULT is %s",msg)		
		
	def activityClosed(self):
		"""
		define method
		boss被打死，就不会走到这里
		只有活动结束，boss没死，才会由副本空间的base调用
		"""
		INFO_MSG("liuwangmu space get notice activity is over!")
		bossID = self.queryTemp( "liuwangmuBossEntityID", -1 )					# 这个六王墓的bossID记录是在六王墓的bossAI中做的，在脚本是找不到的
		if bossID == -1:
			ERROR_MSG( "----->>> liuwangmuBossEntityID hasn't recorded to space when creating normal monster!" )
			return
		if BigWorld.entities.get(bossID, None):  #如果boss死亡则不会走下面的
			DEBUG_MSG("liuwangmu boss: %d not dead, but activity is over!"%bossID)
			BigWorld.entities[bossID].onActivityClosed()
			
	def readyToClosed(self):
		"""
		defined method
		"""
		INFO_MSG("liuwangmu space ready to close!")
		for player in self._players:
			area = random.random() * 10 * 2 - 10
			player.gotoSpace("zly_bi_shi_jian", Math.Vector3(-457.0 + area, 60.0, -841.0 + area), Math.Vector3(0, 0, 0))
		
