# -*- coding: gb18030 -*-

# ˮ֮���ĵ�ͼ


import BigWorld
# common
import csdefine
from bwdebug import *
# cell
import ECBExtend
from SpaceCopy import SpaceCopy
from SpaceCopyTemplate import SpaceCopyTemplate
from GameObjectFactory import g_objFactory

BUFF_ID_1 = 62004

class SpaceCopyMercuryCoreMap( SpaceCopy ) :
	"""
	"""
	def __init__( self ) :
		SpaceCopy.__init__( self )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		DEBUG_MSG( "Role %i is killed by enemy." % role.id )
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		#role.addTimer( 7.0, 0, ECBExtend.ROLE_REVIVE_TIMER )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		�������ķ�ʽ�˳�����
		"""
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.removeAllBuffByBuffID( BUFF_ID_1, [ csdefine.BUFF_INTERRUPT_NONE ] )


