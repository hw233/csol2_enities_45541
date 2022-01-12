# -*- coding: gb18030 -*-
#



from SpaceCopy import SpaceCopy
import Const


class SpaceCopyGumigong( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )


	def addSpawnPoint( self, spawnPointBaseMB, group ):
		"""
		"""
		spawnPointBaseMBList = self.queryTemp( group, [] )
		spawnPointBaseMBList.append( spawnPointBaseMB )
		self.setTemp( group, spawnPointBaseMBList )
		if group == -1:					#-1 是刷BOSS
			return
		groupSet = self.queryTemp( 'groupCount', set() )
		groupSet.add( group )
		self.setTemp( 'groupCount', groupSet )



	def onMonsterDie( self ):
		"""
		define method
		"""
		self.getScript().onMonsterDie( self )


	def onLeave( self, baseMailbox, params ):
		"""
		退出
		"""
		print "onLeave racehorse!"
		SpaceCopy.onLeave( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )