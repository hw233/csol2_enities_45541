# -*- coding: gb18030 -*-
#
from SpaceCopyMaps import SpaceCopyMaps

import csconst
import Const
import BigWorld

class SpaceCopyShenGuiMiJing( SpaceCopyMaps ):
	"""
	神鬼秘境副本
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopyMaps.__init__( self )
	
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
		]
		"""
		# 显示剩余小怪，蒙蒙，剩余BOSS，剩余时间。 
		return [ 0, 1, 3, 15, 16 ]
		
	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyMaps.onEnterCommon( self, baseMailbox, params )
		
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
		SpaceCopyMaps.onLeaveCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.resetAccumPoint()							# 玩家离开副本，气运值置0
			player.removeTemp( "callPGDict" )							# 将召唤列表清空
			player.removeTemp( "pg_formation" )
			player.client.closePGControlPanel()	
			player.removeTemp( "ROLE_CALL_PGNAGUAL_LIMIT" )
	
	def checkSpaceIsFull( self ):
		"""
		检查空间是否满员
		"""
		if self.getPlayerNumber() >= csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ self.getScript().difficulty ]:
			return True
			
		return False
	
	def onAINotifySpaceDied( self, className, entity ):
		"""
		define method.
		AI通知NPC死亡
		"""
		SpaceCopyMaps.onAINotifySpaceDied( self, className, entity )
		self.onHideAnger()
		
	def onZhainanHPChange( self, hp, hp_max ):
		"""
		define method.
		斋南血量改变
		"""
		self.getScript().onZhainanHPChange( self, hp, hp_max )
		
	def onShowAnger( self ):
		"""
		define method.
		显示怒气值界面
		"""
		self.getScript().onShowAnger( self )
		
	def onHideAnger( self ):
		"""
		define method.
		隐藏怒气值界面
		"""
		self.getScript().onHideAnger( self )