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

class SpaceCopyCampTurnWar( SpaceCopy ):
	"""
	��ᳵ��ս�ռ�
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		
	def allWarOver( self ):
		"""
		define method
		�������ж�ս����
		"""
		INFO_MSG( "SpaceCopyTongTurnWar(id: %s) all war over!" % self.id )
		self.getScript().allWarOver( self )
		
	def onActivityOver( self ):
		"""
		define method
		�ʱ�����
		"""
		self.getScript().onActivityOver( self )
		
	def telportPlayer( self, playerDBID, position ):
		"""
		define method
		������ҵ���ս��
		"""
		self.getScript().telportPlayer( self, playerDBID, position )
		