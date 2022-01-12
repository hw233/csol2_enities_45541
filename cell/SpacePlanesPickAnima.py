# -*- coding: gb18030 -*-
from SpacePlanes import SpacePlanes

import Const
REPEAT_HAS_ADDITION_TIME = 5.0	#重复拾取有加成时间
REPEAT_REWARD_POTENTIAL = 2

class SpacePlanesPickAnima( SpacePlanes ):
	"""
	单人地图
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpacePlanes.__init__( self )
	
	def onTriggerTrap( self, planesID, pickRole, pickTime, rewardPotential ):
		"""
		define method
		记录玩家陷发陷阱的时间
		"""
		self.pickAnimaData.pickAnima( planesID, pickRole, pickTime, rewardPotential )
	
	def resertAddition( self, planesID, role ):
		"""
		define method.
		去掉某位面的拾取加成叠加状态
		"""
		self.pickAnimaData.resertAddition( planesID, role )
		role.client.pickAnima_triggerZhaDan()
	
	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpacePlanes.onEnter( self, baseMailbox, params )
		baseMailbox.client.pickAnima_enterSpace()
		baseMailbox.cell.systemCastSpell( Const.ACTIVITY_STOP_MOVE_SKILL ) #给玩家一个定身BUFF
	
	def onGameOver( self, planesID, role ):
		"""
		define method.
		游戏结束,发放奖励，暂时没有奖励内容
		"""
		r = self.pickAnimaData.getPlanesRecord( planesID )
		if r:
			role.client.pickAnima_overReport( len( r.pickAnimaList ), r.potentialCount)