# -*- coding: gb18030 -*-


from SpaceCopyTeam import SpaceCopyTeam

class SpaceCopyTongCompetition( SpaceCopyTeam ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeam.__init__( self )


	def onSpaceTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData ):
		"""
		domain�ҵ���Ӧ��spaceNormal��spaceNormal��ʼ����һ��entity������space��ʱ��֪ͨ
		"""
		if selfEntity.checkSpaceFull():
			baseMailbox.statusMessage( csstatus.TONG_COMPETITION_FULL )
			return
		baseMailbox.cell.teleportToSpace( position, direction, selfEntity.cell, selfEntity.spaceID )