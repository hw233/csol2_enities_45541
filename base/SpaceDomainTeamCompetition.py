# -*- coding: gb18030 -*-


from SpaceDomainCopy import SpaceDomainCopy
import csdefine

class SpaceDomainTeamCompetition( SpaceDomainCopy ):
	"""
	组队竞赛
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
		模板方法；删除spaceItem
		"""
		self.keyToSpaceNumber.clear()
		SpaceDomainCopy.removeSpaceItem( self, spaceNumber )

