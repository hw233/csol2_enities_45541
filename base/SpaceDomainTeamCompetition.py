# -*- coding: gb18030 -*-


from SpaceDomainCopy import SpaceDomainCopy
import csdefine

class SpaceDomainTeamCompetition( SpaceDomainCopy ):
	"""
	��Ӿ���
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomainCopy.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS		

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()
		
	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		ģ�巽����ɾ��spaceItem
		"""
		self.keyToSpaceNumber.clear()
		SpaceDomainCopy.removeSpaceItem( self, spaceNumber )

