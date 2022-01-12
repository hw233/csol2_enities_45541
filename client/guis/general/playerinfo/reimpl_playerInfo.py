# -*- coding: gb18030 -*-

"""
实现不同语言版本的角色头像信息

"""
from guis import *
from AbstractTemplates import MultiLngFuncDecorator
from LabelGather import labelGather
from guis.controls.ContextMenu import DefMenuItem
import ItemTypeEnum

quality_filter = {ItemTypeEnum.CQT_BLUE: ( labelGather.getText( "PlayerInfo:main", "cqt_green"),( 33, 225, 25, 255 ) ),
				ItemTypeEnum.CQT_GOLD: ( labelGather.getText( "PlayerInfo:main", "cqt_blue"), ( 0, 229, 233, 255 ) ),
				ItemTypeEnum.CQT_PINK: ( labelGather.getText( "PlayerInfo:main", "cqt_purple"),( 192, 0, 192, 255 ) ),
				ItemTypeEnum.CQT_GREEN: ( labelGather.getText( "PlayerInfo:main", "cqt_orange"),( 255, 128, 0,255 ) )
				}

class deco_playerInfoInit( MultiLngFuncDecorator ) :
	"""
	初始化队伍品质分配菜单
	"""
	@staticmethod
	def locale_big5( SELF, pyParent ) :
		"""
		BIG5 版本
		"""
		for quality, quaTuple in quality_filter.iteritems():
			pyQuaItem = DefMenuItem( quaTuple[0], MIStyle.CHECKABLE)
			quaColor = quaTuple[1]
			pyQuaItem.commonForeColor = quaColor
			pyQuaItem.highlightForeColor = quaColor
			pyQuaItem.disableForeColor = quaColor
			pyQuaItem.quality = quality
			pyQuaItem.clickCheck = False
#			pyQuaItem.onLClick.bind( SELF.__qualityPickUp )
			pyParent.pySubItems.add( pyQuaItem )
	
	@classmethod
	def __qualityPickUp( SELF, pyQuaItem ):
		quality = pyItem.quality
		player = BigWorld.player()
		player.base.changePickUpQuality( quality )

class deco_playerInfoSet( MultiLngFuncDecorator ) :
	"""
	设置队伍品质分配菜单
	"""
	@staticmethod
	def locale_big5( SELF, pyCMenu, quality ) :
		"""
		BIG5 版本
		"""
		pyCMenu.pyItems[2].textValue = quality_filter[quality][0]
		pyCMenu.pyItems[2].textColor = quality_filter[quality][1]
