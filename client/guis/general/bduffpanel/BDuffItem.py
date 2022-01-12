# -*- coding: gb18030 -*-
#
# $Id: BDuffItem.py,v 1.8 2008-08-26 03:25:12 qilan Exp $

"""
"""

import math
from guis import *
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.BuffItem import BuffItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
import GUIFacade
import csstatus
from guis.tooluis.richtext_plugins.share import defParser
from Time import Time

# ----------------------------------------------------------------
# ������������ߴ�������
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_BuffResetPyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		����������µ���������������ĳߴ�
		"""
		SELF._BDuffItem__pyLeaveTime.fontSize = 11
		SELF._BDuffItem__pyLeaveTime.charSpace = -1


class BDuffItem( Control ) :

	__BUFF_ITEM = None

	def __init__( self, pyBinder = None ) :
		if BDuffItem.__BUFF_ITEM is None :
			BDuffItem.__BUFF_ITEM = GUI.load( "guis/general/bduffpanel/item.gui" )
		buffGui = util.copyGuiTree( BDuffItem.__BUFF_ITEM )
		uiFixer.firstLoadFix( buffGui )
		Control.__init__( self, buffGui, pyBinder )

		self.focus = True
		self.visible = False
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"

		self.__pyItem = BuffItem( buffGui.item.icon )
		self.__pyLeaveTime = StaticText( buffGui.lbLeaveTime )
		self.__pyLeaveTime.fontSize = 11 			# �����С
		self.__pyCover = CDCover( buffGui.item.cdCover )
		self.__pyCover.reverse = True				# ��ɫ��ʾ����ɫ��ʾʣ��ʱ��
		self.__pyCover.reset( 1 )
		self.__pyLeaveTime.visible = True

		self.__fader = buffGui.item.fader
		self.__fader.speed = 0.5

		self.__detectCBID = 0						# ��� buff ������ callback ID��ԭ���� Timer ���ڸ�Ϊֱ���� callback( hyw -- 2008.06.24 )

		self.__resetPyItems()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@deco_BuffResetPyItems
	def __resetPyItems( self ) :
		"""
		���貿��UIԪ�ص�λ�á���С�����������
		"""
		pass											# ����汾�����޸�

	def __detect( self ) :
		if self.itemInfo is None : return
		endTime = self.itemInfo.endTime
		if endTime <= 0 :
			self.__pyLeaveTime.color = defParser.tranColor( "c4" ) 			# ��ɫ
			self.__pyLeaveTime.text = "N/A"
			self.__fader.value = 1
		else :
			leavingTime = endTime - Time.time() 
			if leavingTime > 0 :
				min = leavingTime/60.0
				sec = leavingTime % 60
				cbInterval = 1
				if min >= 1 :
					cbInterval = max( sec, cbInterval )
					self.__pyLeaveTime.color = defParser.tranColor( "c1" ) 		# ��ɫ
					if min > 999 :
						hour = leavingTime/3600.0
						self.__pyLeaveTime.text = "%ih" % int( math.ceil( hour ) )
					else :
						self.__pyLeaveTime.text = "%im" % int( math.ceil( min ) )
				else :  #�߻�Ҫ��BUFFʣ��ʱ����ʾN��1��
					if sec > 59:
						self.__pyLeaveTime.color = defParser.tranColor( "c1" ) 	# ��ɫ
						self.__pyLeaveTime.text = "%im" % int( math.ceil( min ) )
					elif sec > 30:
						self.__pyLeaveTime.color = defParser.tranColor( "c6" ) 	# ��ɫ
						self.__pyLeaveTime.text = "%is" % int( math.ceil( sec ) )
					else :
						self.__pyLeaveTime.color = defParser.tranColor( "c3" ) 	# ��ɫ
						self.__pyLeaveTime.text = "%is" % int( math.ceil( sec ) )

				if leavingTime <= GUIFacade.getWarningTime() :
					#cbInterval = 0.2
					self.__fader.value = not self.__fader.value
				else :
					self.__fader.value = 1

				self.__detectCBID = BigWorld.callback( cbInterval, self.__detect )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self,mods ):
		if self.itemInfo :
			GUIFacade.removeBuff( self.itemInfo )
		return True

	def onLClick_( self, mods ):
		# ����Ƿ�����BUFF���򵯳���Ӧ��ʾ��Ϣ��
		if self.itemInfo.baseItem.getBuffID() == "299010":
			BigWorld.player().statusMessage( csstatus.ANTI_INDULGENCE_STATE_SICK )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BigWorld.cancelCallback( self.__detectCBID )
		self.__pyItem.update( itemInfo )
		self.__pyCover.reset( 0 )
		if itemInfo is not None :
			self.visible = True
			self.__detect()

	def dispose( self ) :
		BigWorld.cancelCallback( self.__detectCBID )
		self.__pyItem.update( None )
		self.__pyItem.dispose()
		self.__pyLeaveTime.dispose()
		self.__pyCover.dispose()
		Control.dispose( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemInfo( self ) :
		return self.__pyItem.itemInfo

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemInfo = property( _getItemInfo )
