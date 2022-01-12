# -*- coding: gb18030 -*-
#

import BigWorld
from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
import Const

GOD_WEAPON_QUEST_XL = 40202003

class SpaceCopyXieLongDongXue( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	邪龙洞穴副本
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		self.addTimer( 3600, 0, 3600 )		# 3600s后，副本自动关闭

	def onGodWeaponXL( self ):
		"""
		define method
		完成神器任务
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_XL, 1 )
			
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
		
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			skills = {}
			if self.className in player.mapSkills:
				skills = player.mapSkills[self.className]
			player.client.showPGControlPanel( skills )

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
		
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.resetAccumPoint()							# 气运值置0
			player.removeTemp( "callPGDict" )						# 将召唤列表清空
			player.removeTemp( "pg_formation" )
			player.client.closePGControlPanel()					# 关闭召唤守护界面
			player.removeTemp( "ROLE_CALL_PGNAGUAL_LIMIT" )
	
	def checkSpaceIsFull( self ):
		return SpaceCopyYeWaiInterface.checkSpaceIsFull( self )