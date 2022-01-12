# -*- coding: gb18030 -*-
#
# $Id: BuffItem.py,v 1.6 2008-08-25 11:00:05 qilan Exp $

import GUIFacade
from guis import *
from guis.controls.BuffItem import BuffItem as BaseBuffItem
from guis.controls.CircleCDCover import CircleCDCover as Cover

class BuffItem( BaseBuffItem ) :
	__cg_item = None

	def __init__( self ) :
		if BuffItem.__cg_item is None :
			BuffItem.__cg_item = GUI.load( "guis/general/petswindow/petinfo/buffitem.gui" )

		item = util.copyGuiTree( BuffItem.__cg_item )
		uiFixer.firstLoadFix( item )
		BaseBuffItem.__init__( self, item )
		self.__pyCover = Cover( item.cdCover )
		self.__pyCover.reverse = True								# 反色显示，亮色表示剩余时间
		self.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BaseBuffItem.update( self, itemInfo )
		if itemInfo is None :										# 信息为None，buff不显示
			self.visible = False
			self.__pyCover.reset( 0 )
		elif itemInfo.endTime - 0 < 0.001 :							# 结束时间是零，这个是持续显示的buff
			self.visible = True
			self.__pyCover.reset( 0 )
			self.__pyCover.visible = False
		elif itemInfo.persistent > 0 :								# 有持续时间而且还没结束
			self.visible = True
			leaveTime = itemInfo.leaveTime							# 剩余时间
			percent = leaveTime / itemInfo.persistent				# 计算启动计时的位置
			self.__pyCover.unfreeze( leaveTime, percent )			# 启用 counddown 覆盖膜
			self.__pyCover.visible = True
		else:
			self.visible = False
			self.__pyCover.reset( 0 )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	"""
	def _getIcon( self ) :
		return ( self.texture, self.mapping )

	def _setIcon( self, icon ) :
		assert isinstance( icon, ( tuple, str ) )
		isTuple = type( icon ) is tuple
		gui = self.getGui().icon
		gui.textureName = ( isTuple and [icon[0]] or [icon] )[0]
		if not isTuple or icon[1] is None :
			gui.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )
		else :
			gui.mapping = icon[1]

	icon = property( _getIcon, _setIcon )								# 获取/设置 Item 的图标：( 此乃重写的属性 )
	"""
