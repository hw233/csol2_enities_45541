# -*- coding:gb18030 -*-

from SpaceCopy import SpaceCopy
from bwdebug import *
import BigWorld
import Const

class SpaceCopyTeachKillMonster( SpaceCopy ):
	"""
	"""
	def bossDead( self, spawnPointBaseMB ):
		"""
		Define method.
		boss挂掉了
		"""
		bossCount = self.queryTemp( "bossCount" )
		if bossCount > 0:
			self.setTemp( "bossCount", bossCount - 1  )
			spawnPointBaseMB.cell.createEntity()
		else:	# 生成传送门
			self.getScript().createDoor( self )
			#door = BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, otherDict["position"], (0, 0, 0), {} )
			#if otherDict.has_key( 'modelScale' ) and otherDict[ 'modelScale' ] != 0.0:
			#	door.modelScale = otherDict[ 'modelScale' ]
			
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
		if len( self._players ) == 0:
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )
			
	def showDetails( self ):
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
		]
		"""
		return [ 0, 1 ]
		