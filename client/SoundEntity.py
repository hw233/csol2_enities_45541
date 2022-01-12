# -*- coding: gb18030 -*-

# $Id: SoundEntity.py,v 1.4 2008-07-02 02:36:26 zhangyuxing Exp $

import BigWorld
import Pixie
from interface.GameObject import GameObject
from Sound import Sound
import csdefine
from gbref import rds
import Define

"""
"""
class SoundEntity( GameObject ) :
	def __init__( self ) :
		GameObject.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC
		self.setSelectable( False )
		self.isSoundPlay = False
		self.trapID = None
		self.sound = None

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		return [ "particles/gxcone.model"]

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return
		self.model = BigWorld.Model( "particles/gxcone.model" )
		self.trapID = BigWorld.addPot(self.matrix, 20.0, self.onTrap )
		GameObject.onCacheCompleted( self )

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		GameObject.leaveWorld( self )
		if self.trapID is not None:
			self.onTrap( 0, 1 )
			BigWorld.delPot( self.trapID )
			self.trapID = None

	def onTrap( self, enteredTrap, handle ):
		"""
		"""
		if enteredTrap and not self.isSoundPlay:
			self.isSoundPlay = True
			if self.flags & Define.SOUND_END_BGMUSIC:
				rds.soundMgr.switchMusic( self.soundEvent )
				rds.soundMgr.lockBgPlay( True )
			else:
				self.sound = rds.soundMgr.playVocality( self.soundEvent, self.model )
		elif not enteredTrap and self.isSoundPlay:
			self.isSoundPlay = False
			if self.flags & Define.SOUND_END_BGMUSIC:
				currArea = rds.statusMgr.statusObjs[Define.GST_IN_WORLD].getCurrArea()
				if currArea is None:
					currAreaMusic = ""
				else:
					currAreaMusic = currArea.getMusic()
				rds.soundMgr.lockBgPlay( False )
				rds.soundMgr.switchMusic( currAreaMusic )
			else:
				#rds.soundMgr.stopVocality( self.soundEvent, self.model )
				rds.soundMgr.stopVocalitySound( self.sound )


	def __del__(self):
		pass

# SoundEntity.py
