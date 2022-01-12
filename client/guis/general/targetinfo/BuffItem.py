# -*- coding: gb18030 -*-
#
# $Id: BuffItem.py,v 1.6 2008-08-25 11:00:05 qilan Exp $

import GUIFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.BuffItem import BuffItem as BaseBuffItem
from guis.controls.CircleCDCover import CircleCDCover as Cover
class BuffItem( BaseBuffItem ) :

	def __init__( self, item = None ) :
		if item is None:
			item = GUI.load( "guis/general/targetinfo/common/buffItem.gui" )
		uiFixer.firstLoadFix( item )
		BaseBuffItem.__init__( self, item )
		self.__pyCover = Cover( item.cover )
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
		elif itemInfo.leaveTime  >= 0 :								# 有持续时间而且还没结束
			self.visible = True
			leaveTime = itemInfo.leaveTime							# 剩余时间
			percent = leaveTime / itemInfo.persistent				# 计算启动计时的位置
			self.__pyCover.unfreeze( leaveTime, percent )			# 启用 counddown 覆盖膜
			self.__pyCover.visible = True
		else:
			self.visible = True
			self.__pyCover.reset( 0 )

	def dispose( self ):
		toolbox.infoTip.hide( self )										# 隐藏BUFF信息
		BaseBuffItem.dispose( self )
