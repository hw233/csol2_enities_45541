# -*- coding: gb18030 -*-

#$Id: IconsSoundLoader.py,v 1.2 2008-09-03 06:42:47 yangkai Exp $

from bwdebug import *
import Language
import Const
from config.client.SkillEffect import IconsSound
from config.client.roleHeadTexture import Datas
# ----------------------------------------------------------------------------------------------------
# 图标对应声音配置加载
# ----------------------------------------------------------------------------------------------------

class IconsSoundLoader:
	"""
	图标对应声音表
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：{...}}
	@type _data: dict
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert IconsSoundLoader._instance is None, "instance already exist in"
		self._datas = IconsSound.Datas # { icon : {"sound_up": ui/.., "sound_down": "ui/..."}...}
		self._hdatas = Datas # { headTextureID : pathString, ... }

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = IconsSoundLoader()
		return self._instance

	def _convertIcon( self, iconPath ):
		"""
		"""
		if type( iconPath ) != str: iconPath = ""
		iconPath = iconPath.lower()
		return iconPath[6:-4]

	def getDragUpSound( self, icon ):
		"""
		根据图标名获取拖起该图标的声音
		@param icon	:	图标名
		@type icon	:	String
		@return		:	"ui/..." 声音事件
		"""
		icon = self._convertIcon( icon )
		try:
			return self._datas[icon]["sound_up"]
		except KeyError:
			ERROR_MSG( "Can't find IconSound Config by %s" % icon )
			return "ui/default"

	def getDragDownSound( self, icon ):
		"""
		根据图标名获取放下该图标的声音
		@param icon	:	图标名
		@type icon	:	String
		@return		:	"ui/..." 声音事件
		"""
		icon = self._convertIcon( icon )
		try:
			return self._datas[icon]["sound_down"]
		except KeyError:
			ERROR_MSG( "Can't find IconSound Config by %s" % icon )
			return "ui/default"
			
	def getHeadTexturePath( self, headTextureID ):
		"""
		获得角色头像贴图路径信息 by姜毅
		"""
		try:
			return self._hdatas[headTextureID]
		except KeyError:
			ERROR_MSG( "Can't find headTexture Config by %s" % str( headTextureID ) )
			return None

#$Log: not supported by cvs2svn $
#Revision 1.1  2008/05/30 09:16:19  yangkai
#no message
#
