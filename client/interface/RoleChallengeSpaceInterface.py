# -*- coding: gb18030 -*-
import event.EventCenter as ECenter
import BigWorld
import csconst

import csstatus
import Define

class RoleChallengeSpaceInterface:
	def __init__( self ):
		self.memberAvatars = {}
		self.avatarType = ""
		self.enterType = 0		#进入模式，1:普通，2：替补模式进入
		self.challengeType = 0	# 进入挑战副本类型，1：单人，2：多人
	
	def isInSpaceChallenge( self ):
		return "fu_ben_hua_shan" in BigWorld.getSpaceDataFirstForKey( self.spaceID,  csconst.SPACE_SPACEDATA_KEY )
	
	def challengeSpaceShow( self, type ):
		# 显示选择页面, type:1普通，2：替补模式进入
		# define method 
		self.enterType = type
		ECenter.fireEvent( "EVT_ON_TOGGLE_CHALLENGE_COPY", type )
	
	def challengeSpaceReceivesSetAvatar( self, memberID, avatarType ):
		# 接收队友设置挑战的英雄职业
		# define method
		self.memberAvatars[ memberID ] = avatarType
		ECenter.fireEvent( "EVT_ON_MEMBER_SET_AVATAR", memberID, avatarType )
	
	def challengeSpaceEnter( self ):
		if self.enterType == csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT:
			for mid in self.teamMember.keys():
				if mid not in self.memberAvatars:
					# 还有队友没选择英雄
					self.statusMessage( csstatus.CHALLENGE_MEMBER_IS_NO_READY )
					return
		self.cell.challengeSpaceEnter()
	
	def challengeSpaceSetAvatar( self, avatar ):
		"""
		设置英雄
		"""
		BigWorld.player().cell.challengeSpaceSetAvatar( avatar )
	
	def challengeSpaceOnEnter( self, challengeSpaceAvatar, challengeType ):
		# define method.
		# 进入挑战副本
		self.challengeType = challengeType
		if challengeSpaceAvatar:
			self.avatarType = challengeSpaceAvatar
			self.weaponType = Define.WEAPON_TYPE_CHALLENGE[ challengeSpaceAvatar ]
		# lock camera
		self.changeWorldCamHandler( 2 )
	
	def challengeSpaceOnEnd( self, params ):
		# define method.
		# 离开挑战副本
		self.resetWeaponType()
		# unlock camera
		self.changeWorldCamHandler( 1 )
		self.avatarType = ""
		self.enterType = 0
		self.memberAvatars = {}
		ECenter.fireEvent( "EVT_ON_LEAVE_CHALLENGE_COPY" )
