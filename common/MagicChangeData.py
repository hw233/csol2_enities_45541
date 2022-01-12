# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
	
class MagicChangeData:
	"""
	变身数据
	"""
	def __init__( self ):
		self.avatarObj = None
		
	def getDictFromObj( self, obj ):
		return getDictFromObj( obj )
		
	def createObjFromDict( self, dict ):
		return createObjFromDict( dict )
	
	def isSameType( self, obj ):
		return isSameType( obj )
	
	def getAvatarObj( self ):
		return self.avatarObj
	
	def startMagicChange( self, owner, typeObj ):
		self.avatarObj = typeObj
		self.avatarObj.onInit( owner )
		self.avatarObj.magicChange()
	
	def stopMagicChange( self, owner ):
		if not self.avatarObj:
			return
			
		self.avatarObj.onInit( owner )
		self.avatarObj.resetChange()
		self.avatarObj = None

instance = MagicChangeData()

if BigWorld.component == "cell":	
	import MagicChangeAvatar
	def getDictFromObj( obj ):
		dict = {}
		if obj.getAvatarObj():
			dict[ "avatarType" ] = obj.avatarObj.getType()
			dict[ "avatarPro" ] = obj.avatarObj.getProDict()
		else:
			dict[ "avatarType" ] = ""
			dict[ "avatarPro" ] = []
		return dict
	
	def createObjFromDict( dict ):
		avatarType = dict[ "avatarType" ]
		avatarObj = MagicChangeAvatar.AvatarType.get( avatarType, None )
		obj = MagicChangeData()
		if avatarObj:
			obj.avatarObj = avatarObj()
			obj.avatarObj.resetObj( dict )
			
		return obj
	
	def isSameType( obj ):
		return isinstance( obj, MagicChangeData )
	
else:
	def getDictFromObj( obj ):
		return obj
	
	def createObjFromDict( dict ):
		return dict
	
	def isSameType( obj ):
		return True