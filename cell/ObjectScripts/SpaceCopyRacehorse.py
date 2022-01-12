# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyTianguan.py,v 1.5 2008-08-20 01:23:37 zhangyuxing Exp $

"""
"""

from SpaceCopyTemplate import SpaceCopyTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess
from CopyContent import CCWait
from CopyContent import CCEndWait
import BigWorld
import time
import csdefine

WAIT_FOR_RACE	= 760014001	# �ȴ�����BUFF
RACE_START		= 1			# ����ʼ
RACE_WAIT_TIME	= 120		# ����ȴ�ʱ��(120��)
RACE_HORSE_TIME = 1200		# ����ʱ��

class CCRacehorse( CopyContent ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		"""
		self.key = "raceContent"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( RACE_HORSE_TIME, 0, NEXT_CONTENT )

	def endContent( self, spaceEntity ):
		"""
		��������
		"""
		BigWorld.globalData["RacehorseManager"].closeRacehorseMap( spaceEntity.params["spaceKey"] )
		CopyContent.endContent( self, spaceEntity )

	def onTeleportReady( self, spaceEntity, baseMailbox ):
		"""
		�������ң�������ȴ�BUFF
		"""
		baseMailbox.cell.spellTarget( WAIT_FOR_RACE, baseMailbox.id )


class SpaceCopyRacehorse( SpaceCopyTemplate ):
	"""
	����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
			
	def initContent( self ):
		"""
		"""
		self.contents.append( CCRacehorse() )
		self.contents.append( CCKickPlayersProcess() )
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		�뿪����ң��ı�ģ�ͣ���������������
		"""
		baseMailbox.cell.onBecomeNonRacer()
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.remoteCall( "removeFlag", ( csdefine.ROLE_FLAG_AREA_SKILL_ONLY, ) )
	
	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		"""
		baseMailbox.cell.onBecomeRacer()
		SpaceCopyTemplate.onTeleportReady( self, selfEntity, baseMailbox )
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		enterList = selfEntity.queryTemp( "enterPlayerIDs", [] )
		enterList.append( baseMailbox.id )
		selfEntity.setTemp( "enterPlayerIDs", enterList )
		baseMailbox.cell.remoteCall( "addFlag", ( csdefine.ROLE_FLAG_AREA_SKILL_ONLY, ) )

