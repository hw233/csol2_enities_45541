# -*- coding: gb18030 -*-


import time
from SpaceCopy import SpaceCopy
from SpaceCopy import SpaceCopy
from bwdebug import *
import cschannel_msgs
import Love3
import csdefine
import csstatus
import BigWorld

class SpaceCopyTongTurnWar( SpaceCopy ):
	"""
	帮会车轮战空间
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
	
	def startNextWar( self):
		"""
		define method
		开始下一对局
		"""
		INFO_MSG("Begin next war!")
		self.getScript().startNextWar( self )
		
	def allWarOver( self ):
		"""
		define method
		副本所有对战结束
		"""
		INFO_MSG( "SpaceCopyTongTurnWar all war over!" )
		self.getScript().allWarOver( self )
		
	def onActivityOver( self ):
		"""
		define method
		活动时间结束
		"""
		self.getScript().onActivityOver( self )
		
	def revert_HpMp( self, player ):
		"""
		回血回蓝
		"""
		player.addMP( player.MP_Max - player.MP )
		
		# 加15%血
		tempHP = player.HP_Max * 0.15
		if player.HP + tempHP > player.HP_Max:
			player.addHP( player.HP_Max - player.HP )
		else:
			player.addHP( tempHP )
