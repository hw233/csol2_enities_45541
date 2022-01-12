# -*- coding: gb18030 -*-
#


from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus

class SpaceCopyProtectTong( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		
	def onProtectTongEnd( self ):
		"""
		define method.
		通知活动结束
		"""
		self.getScript().onProtectTongEnd( self, False )
	
	def onTeamDismiss( self ):
		"""
		define method.
		队伍被解散
		"""
		self.setTemp( "destroyTimer", self.addTimer( 10, 0, 0  ) )
		self.getScript().statusMessageAllPlayer( self, csstatus.PROTECT_TONG_OVER1 )
		
	def onProtectTongMsg( self, timeVal ):
		"""
		define method.
		通知活动结束
		"""
		if timeVal == 300: # 5分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 5 )
		elif timeVal == 240: # 4分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 4 )
		elif timeVal == 180: # 3分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 3 )
		elif timeVal == 120: # 2分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 2 )
		elif timeVal == 60: # 1分钟
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 1 )	
		elif timeVal < 60: # 30秒以后
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE2, timeVal )

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
		# 显示剩余小怪，剩余BOSS。 
		return [ 1, 3 ]