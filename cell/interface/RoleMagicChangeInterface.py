# -*- coding: gb18030 -*-

import random

import csconst
import csdefine
import MagicChangeAvatar
from bwdebug import *
# ��ս������Ӣ���б�


class RoleMagicChangeInterface:
	def __init__( self ):
		pass
		
	def startMagicChange( self, avatarType ):
		"""
		define mothods
		��ʼ����
		"""
		self.magicChangeObj.stopMagicChange( self )
			
		avaterObj = MagicChangeAvatar.AvatarType.get( avatarType, None )
		if avaterObj is not None:
			self.magicChangeObj.startMagicChange( self, avaterObj() )

	def stopMagicChange( self ):
		"""
		define mothods
		��������
		"""			
		self.magicChangeObj.stopMagicChange( self )
	
	def startMagicChangeChallenge( self ):
		"""
		define mothods
		"""
		challengeAvatar = csconst.CHALLENGE_AVATAR_LIST.get( self.getClass() )
		self.startMagicChange( challengeAvatar )
	
	def stopMagicChangeChallenge( self ):
		"""
		define mothods
		"""
		self.stopMagicChange( )
