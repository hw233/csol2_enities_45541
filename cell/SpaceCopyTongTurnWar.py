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
	��ᳵ��ս�ռ�
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
	
	def startNextWar( self):
		"""
		define method
		��ʼ��һ�Ծ�
		"""
		INFO_MSG("Begin next war!")
		self.getScript().startNextWar( self )
		
	def allWarOver( self ):
		"""
		define method
		�������ж�ս����
		"""
		INFO_MSG( "SpaceCopyTongTurnWar all war over!" )
		self.getScript().allWarOver( self )
		
	def onActivityOver( self ):
		"""
		define method
		�ʱ�����
		"""
		self.getScript().onActivityOver( self )
		
	def revert_HpMp( self, player ):
		"""
		��Ѫ����
		"""
		player.addMP( player.MP_Max - player.MP )
		
		# ��15%Ѫ
		tempHP = player.HP_Max * 0.15
		if player.HP + tempHP > player.HP_Max:
			player.addHP( player.HP_Max - player.HP )
		else:
			player.addHP( tempHP )
