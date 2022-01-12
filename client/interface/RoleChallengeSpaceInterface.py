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
		self.enterType = 0		#����ģʽ��1:��ͨ��2���油ģʽ����
		self.challengeType = 0	# ������ս�������ͣ�1�����ˣ�2������
	
	def isInSpaceChallenge( self ):
		return "fu_ben_hua_shan" in BigWorld.getSpaceDataFirstForKey( self.spaceID,  csconst.SPACE_SPACEDATA_KEY )
	
	def challengeSpaceShow( self, type ):
		# ��ʾѡ��ҳ��, type:1��ͨ��2���油ģʽ����
		# define method 
		self.enterType = type
		ECenter.fireEvent( "EVT_ON_TOGGLE_CHALLENGE_COPY", type )
	
	def challengeSpaceReceivesSetAvatar( self, memberID, avatarType ):
		# ���ն���������ս��Ӣ��ְҵ
		# define method
		self.memberAvatars[ memberID ] = avatarType
		ECenter.fireEvent( "EVT_ON_MEMBER_SET_AVATAR", memberID, avatarType )
	
	def challengeSpaceEnter( self ):
		if self.enterType == csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT:
			for mid in self.teamMember.keys():
				if mid not in self.memberAvatars:
					# ���ж���ûѡ��Ӣ��
					self.statusMessage( csstatus.CHALLENGE_MEMBER_IS_NO_READY )
					return
		self.cell.challengeSpaceEnter()
	
	def challengeSpaceSetAvatar( self, avatar ):
		"""
		����Ӣ��
		"""
		BigWorld.player().cell.challengeSpaceSetAvatar( avatar )
	
	def challengeSpaceOnEnter( self, challengeSpaceAvatar, challengeType ):
		# define method.
		# ������ս����
		self.challengeType = challengeType
		if challengeSpaceAvatar:
			self.avatarType = challengeSpaceAvatar
			self.weaponType = Define.WEAPON_TYPE_CHALLENGE[ challengeSpaceAvatar ]
		# lock camera
		self.changeWorldCamHandler( 2 )
	
	def challengeSpaceOnEnd( self, params ):
		# define method.
		# �뿪��ս����
		self.resetWeaponType()
		# unlock camera
		self.changeWorldCamHandler( 1 )
		self.avatarType = ""
		self.enterType = 0
		self.memberAvatars = {}
		ECenter.fireEvent( "EVT_ON_LEAVE_CHALLENGE_COPY" )
