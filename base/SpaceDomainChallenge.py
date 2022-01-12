# -*- coding: gb18030 -*-
import BigWorld

from SpaceDomainCopy import SpaceDomainCopy
import csdefine
SPACE_KEY_FROMAT = "%s_%d"

class SpaceDomainChallenge( SpaceDomainCopy ):
	"""
	��ɽ��( ��ս���� )
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS	
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		#define method.
		#����һ��entity��ָ����space��
		BigWorld.globalData[ "SpaceChallengeMgr" ].playerRequestEnter( self, position, direction, baseMailbox, params )
			
	def onChallengeSpaceEnter( self, position, direction, baseMailbox, params ):
		# define method
		# ���������븱��
		spaceItem = self.findSpaceItem( params, True )
		try:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )
			
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "SpaceChallengeMgr" ].playerRequestLogin( self, baseMailbox, params )
		
	def onChallengeSpaceLogin( self, baseMailbox, params ):
		# define method.
		# ��ս�����������ص�����
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
			baseMailbox.cell.challengeSpaceIsTimeOut()
	
	def createSpaceItem( self, enterKeyDict ):
		# ����һ���µ�space item
		challengeKey = SPACE_KEY_FROMAT%( enterKeyDict[ "spaceChallengeKey" ], enterKeyDict[ "spaceChallengeGate" ] )
		
		spaceItem = SpaceDomainCopy.createSpaceItem( self, enterKeyDict )
		self.keyToSpaceNumber[ challengeKey ] = spaceItem.spaceNumber

		return spaceItem