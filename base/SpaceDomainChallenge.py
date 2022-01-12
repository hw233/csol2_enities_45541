# -*- coding: gb18030 -*-
import BigWorld

from SpaceDomainCopy import SpaceDomainCopy
import csdefine
SPACE_KEY_FROMAT = "%s_%d"

class SpaceDomainChallenge( SpaceDomainCopy ):
	"""
	华山阵法( 挑战副本 )
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS	
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		#define method.
		#传送一个entity到指定的space中
		BigWorld.globalData[ "SpaceChallengeMgr" ].playerRequestEnter( self, position, direction, baseMailbox, params )
			
	def onChallengeSpaceEnter( self, position, direction, baseMailbox, params ):
		# define method
		# 玩家请求进入副本
		spaceItem = self.findSpaceItem( params, True )
		try:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )
			
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "SpaceChallengeMgr" ].playerRequestLogin( self, baseMailbox, params )
		
	def onChallengeSpaceLogin( self, baseMailbox, params ):
		# define method.
		# 挑战副本管理器回调进入
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
			baseMailbox.cell.challengeSpaceIsTimeOut()
	
	def createSpaceItem( self, enterKeyDict ):
		# 创建一个新的space item
		challengeKey = SPACE_KEY_FROMAT%( enterKeyDict[ "spaceChallengeKey" ], enterKeyDict[ "spaceChallengeGate" ] )
		
		spaceItem = SpaceDomainCopy.createSpaceItem( self, enterKeyDict )
		self.keyToSpaceNumber[ challengeKey ] = spaceItem.spaceNumber

		return spaceItem