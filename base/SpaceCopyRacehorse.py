# -*- coding: gb18030 -*-
#
# $Id: Exp $




from SpaceCopy import SpaceCopy
import Love3
import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs


class SpaceCopyRacehorse( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.winers = {}														#���� { 1:dbid, ...}


	def closeRacehorseSpace( self ):
		"""
		"""
		self.cell.closeRacehorseSpace()



	def raceWin( self, playerBaseMB, playerName, dbid, level, raceType ):
		"""
		define method
		"""
		if len( self.winers.keys() ) < 40:
			self.winers[len( self.winers.keys() ) + 1] = dbid

			if len( self.winers.keys() ) <= 20:
				if raceType:	# ����ǰ������
					msg = cschannel_msgs.BCT_SMHD_CELEBRATE %( playerName,len(self.winers.keys() ) )
					playerBaseMB.sendMessage2Tong( playerBaseMB.id, playerName, msg, [] )
				else:			# �������ͨ����
					Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_SMHD_CELEBRATE %( playerName,len(self.winers.keys() ) ), [] )
			playerBaseMB.cell.addRaceRewards( len( self.winers.keys() ) )
