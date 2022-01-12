# -*- coding: gb18030 -*-
from bwdebug import *
from SpaceCopy import SpaceCopy


class SpaceCopyTemplate( SpaceCopy ):
	"""
	副本模板
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.contents = []
		self.initContent()


	def initContent( self ):
		"""
		"""
		pass

	def doNextContent( self, selfEntity ):
		"""
		"""
		index = selfEntity.queryTemp( "contentIndex", -1 )
		index += 1
		selfEntity.setTemp( "contentIndex", index )
		if len( self.contents ) > index:
			self.contents[index].doContent( selfEntity )
			INFO_MSG( selfEntity.className, self.contents[index].key )


	def getCurrentContent( self, selfEntity ):
		"""
		"""
		index = selfEntity.queryTemp( "contentIndex", -1 )
		return self.contents[index]


	def onStartContent( self, selfEntity, baseMailbox, params ):
		"""
		"""
		self.doNextContent( selfEntity )


	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		if selfEntity.queryTemp("firstPlayer", 0 ) == 0:
			selfEntity.setTemp('firstPlayer', 1 )
			self.onStartContent( selfEntity, baseMailbox, params )
			return

		currentContent = self.getCurrentContent( selfEntity )
		currentContent.onEnter( selfEntity, baseMailbox, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		currentContent = self.getCurrentContent( selfEntity )
		currentContent.onLeave( selfEntity, baseMailbox, params )
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def onConditionChange( self, selfEntity, params ):
		"""
		define method
		"""
		index = selfEntity.queryTemp( "contentIndex" )
		self.contents[index].onConditionChange( selfEntity, params )


	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		self.getCurrentContent( selfEntity ).onTimer(  selfEntity, id, userArg )


	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		"""
		SpaceCopy.onTeleportReady( self, selfEntity, baseMailbox )
		self.getCurrentContent( selfEntity ).onTeleportReady( selfEntity, baseMailbox )