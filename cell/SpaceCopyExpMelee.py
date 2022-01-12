# -*- coding: gb18030 -*-
#


from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus
import Const

class SpaceCopyExpMelee( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.addTimer( 2400, 0, 2400 )		# 经验乱斗副本，40min后自动关闭

	def onOverMelee( self ):
		"""
		define method.
		通知活动结束
		"""
		self.getScript().onOverMelee( self, False )

	def onMeleeMsg( self, timeVal ):
		"""
		define method.
		通知活动结束
		"""
		if timeVal == 300: # 5分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 5 )
		elif timeVal == 240: # 4分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 4 )
		elif timeVal == 180: # 3分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 3 )
		elif timeVal == 120: # 2分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 2 )
		elif timeVal == 60: # 1分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 1 )
		elif timeVal < 60: # 30秒以后
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE2, timeVal )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if cbID == 2400:
			self.addTimer( 60, 0, 4*60 )
		elif cbID == 4*60:
			self.onMeleeMsg( 4*60 )
			self.addTimer( 60, 0, 3*60 )
			return
		elif cbID == 3*60:
			self.onMeleeMsg( 3*60 )
			self.addTimer( 60, 0, 2*60 )
			return
		elif cbID == 2*60:
			self.onMeleeMsg( 2*60 )
			self.addTimer( 60, 0, 1*60 )
			return
		elif cbID == 1*60:
			self.onMeleeMsg( 60 )
			self.addTimer( 30, 0, 30 )
			return
		elif cbID == 30:
			self.onMeleeMsg( 30 )
			self.addTimer( 10, 0, 10 )
			return
		elif cbID <= 0:
			self.onOverMelee()
			return
		elif cbID <= 10:
			self.onMeleeMsg( cbID )
			self.addTimer( 1, 0, cbID - 1 )
			return
		# 脚本的onTimer
		SpaceCopy.onTimer( self, timerID, cbID )

	def setLeaveTeamPlayerMB( self, baseMailbox ):
		"""
		define method
		"""
		self.setTemp( 'leavePMB', baseMailbox )
	
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
		# 显示剩余批次，剩余BOSS，剩余时间。
		return [ 0, 2, 3 ]