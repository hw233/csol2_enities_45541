# -*- coding: gb18030 -*-

import BigWorld

from bwdebug import *
from ChallengeAvatarProperty import *

class ChallengeAvatarBase( object ):
	def __init__( self ):
		self.avatarType = ""
		self.modelNumber = ( "", "" )
		self.avatarPropertyObj = None
		self.owner = None
	
	def onInit( self, player ):
		self.owner =  player
		if self.avatarPropertyObj:
			self.avatarPropertyObj.onInit( player )
		
	def getType( self ):
		return self.avatarType
	
	def getProDict( self ):
		# 数据打包
		propList = []
		if self.avatarPropertyObj:
			propDict = self.avatarPropertyObj.asDict()
			for key, value in propDict.iteritems():
				propList.append( { "pKey" : key, "pVal" : value } )
			
		return propList
			
	def resetObj( self, dict ):
		# 数据恢复
		propDict = {}
		propList = dict[ "avatarPro" ]
		for pInfo in propList:
			propDict[ pInfo["pKey"] ] = pInfo["pVal"]
			
		if self.avatarPropertyObj:
			self.avatarPropertyObj.resetObj( propDict )

	def magicChange( self ):
		assert self.avatarPropertyObj is not None
		gender = self.owner.getGender()
		self.owner.currentModelNumber = self.modelNumber[ gender ]
		self.owner.currentModelScale = 1.0
		#self.avatarPropertyObj.changeProperty()
	
	def resetChange( self ):
		#assert self.avatarPropertyObj is not None
		#self.avatarPropertyObj.resetProperty()
		self.owner.currentModelNumber = ""

class ChallengeAvatarChiyou( ChallengeAvatarBase ):
	def __init__( self ):
		super(ChallengeAvatarChiyou, self).__init__( )
		self.avatarType = "chiyou"
		self.modelNumber = ("npcm1000", "npcm1001")
		self.avatarPropertyObj = AvatarPropertyChiyou()

class ChallengeAvatarHuangdi( ChallengeAvatarBase ):
	def __init__( self ):
		super(ChallengeAvatarHuangdi, self).__init__( )
		self.avatarType = "huangdi"
		self.modelNumber = ("npcm1002", "npcm1003")
		self.avatarPropertyObj = AvatarPropertyHuangdi()

class ChallengeAvatarHouyi( ChallengeAvatarBase ):
	def __init__( self ):
		super(ChallengeAvatarHouyi, self).__init__( )
		self.avatarType = "houyi"
		self.modelNumber = ("npcm1004", "npcm1005")
		self.avatarPropertyObj = AvatarPropertyHouyi()

class ChallengeAvatarNuwo( ChallengeAvatarBase ):
	def __init__( self ):
		super(ChallengeAvatarNuwo, self).__init__( )
		self.avatarType = "nuwo"
		self.modelNumber = ("npcm1006", "npcm1007")
		self.avatarPropertyObj = AvatarPropertyNuwo()

AvatarType = {
	"chiyou" 	:  	ChallengeAvatarChiyou,
	"huangdi"	:	ChallengeAvatarHuangdi,
	"houyi"		:	ChallengeAvatarHouyi,
	"nuwo"		:	ChallengeAvatarNuwo,
}
