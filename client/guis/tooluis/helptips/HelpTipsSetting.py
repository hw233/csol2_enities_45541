# -*- coding: gb18030 -*-
import Language
from bwdebug import *
import BigWorld
from cscustom import Rect
from config.client.help.OpIndications import Datas as OpIDTDatas

class TipsInfo( object ) :

	__slots__ = ( "style", "direct", "text", "bound", "unframe" )

	def __init__( self, data ) :
		self.text = ""
		if data.has_key("text"):
			self.text = data["text"]
		self.bound = Rect()
		self.style = data["style"]
		self.direct = data["direction"]
		self.unframe = data["unframed"]

	def updateFromSection( self, ds ) :
		if ds.has_key( "text" ) :
			self.text = ds.readString( "text" )
		if ds.has_key( "direct" ) :
			self.direct = ds.readInt( "direct" )
		if ds.has_key( "style" ) :
			self.style = ds.readInt( "style" )
		if ds.has_key( "bound" ) :
			v = ds.readVector4( "bound" )
			self.bound.update( v[:2], v[2:] )
		if ds.has_key( "unframe" ) :
			self.unframe = ds.readBool( "unframe" )


class HelpTipsSetting:

	_config_path = "config/client/help/HelpTipsSetting.xml"
	_instance = None

	def __init__( self ):
		assert HelpTipsSetting._instance is None
		self._tipInfos = {}
		HelpTipsSetting._instance = self
		self.loadCommonTips()
		self.loadCustomTips( self._config_path )

	def loadCommonTips( self ) :
		"""
		加载公共部分的指引数据
		"""
		for tips in OpIDTDatas.itervalues() :
			for tipId, tip in tips.iteritems() :
				self._tipInfos[tipId] = TipsInfo( tip["ui_data"] )

	def loadCustomTips( self, configPath ):
		section = Language.openConfigSection( configPath )
		if section is None:return
		for tipId, ds in section.items():
			tipId = int( tipId )
			tipsInfo = self.getTipInfo( tipId )
			if tipsInfo :
				tipsInfo.updateFromSection( ds )
			else :
				ERROR_MSG( "Indication(ID:%i) not found."%tipId )
		Language.purgeConfig( self._config_path )

	def getTipInfo( self, tipId ):
		return self._tipInfos.get( tipId, None )

	def hasTips( self, tipId ):
		return tipId in self._tipInfos

	@staticmethod
	def instance():
		"""
		"""
		if HelpTipsSetting._instance is None:
			HelpTipsSetting._instance = HelpTipsSetting()
		return HelpTipsSetting._instance

helpTipsSetting = HelpTipsSetting.instance()