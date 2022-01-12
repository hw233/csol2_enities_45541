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
		self.__pyCover.reverse = True								# ��ɫ��ʾ����ɫ��ʾʣ��ʱ��
		self.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BaseBuffItem.update( self, itemInfo )
		if itemInfo is None :										# ��ϢΪNone��buff����ʾ
			self.visible = False
			self.__pyCover.reset( 0 )
		elif itemInfo.leaveTime  >= 0 :								# �г���ʱ����һ�û����
			self.visible = True
			leaveTime = itemInfo.leaveTime							# ʣ��ʱ��
			percent = leaveTime / itemInfo.persistent				# ����������ʱ��λ��
			self.__pyCover.unfreeze( leaveTime, percent )			# ���� counddown ����Ĥ
			self.__pyCover.visible = True
		else:
			self.visible = True
			self.__pyCover.reset( 0 )

	def dispose( self ):
		toolbox.infoTip.hide( self )										# ����BUFF��Ϣ
		BaseBuffItem.dispose( self )
