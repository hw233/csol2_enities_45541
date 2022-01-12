# -*- coding: gb18030 -*-

# This window shows family challenge info such as
# enemy families name, leave time, name of tong which family
# belonges to,ect.
# written by ganjinxing 2009-7-6

import time
import GUIFacade
from guis import *
from guis.controls.ODListView import ODListView
from guis.common.Window import Window
from LabelGather import labelGather
from RowItem import RowItem

class FCStatusWindow( Window ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/general/familychallenge/fcstatus/fcswnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"

		self.__FCDatas = {}											# ����ת�������Ϣ
		self.__refreshCBID = 0										# ��Ϣ���µĻص�ID

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		class ListPanel( ODListView ) :
			def getViewItem_( self ) :
				return RowItem( self )
		self.__pyInfoPanel = ListPanel( wnd.lv )
		self.__pyInfoPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyInfoPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyInfoPanel.itemHeight = 24
		self.__pyInfoPanel.ownerDraw = True							# �����Զ������

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( wnd.lv.head_2.sText, "FamilyChallenge:FCStatusWindow", "head_2" )
		labelGather.setLabel( wnd.lv.head_1.sText, "FamilyChallenge:FCStatusWindow", "head_1" )
		labelGather.setLabel( wnd.lv.head_0.sText, "FamilyChallenge:FCStatusWindow", "head_0" )
		labelGather.setLabel( wnd.lbTitle, "FamilyChallenge:FCStatusWindow", "lbTitle" )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_FAMILY_CHALLENGING_STATUS"] = self.show
		self.__triggers["EVT_ON_FAMILY_CHALLENGE_STATE_CHANGE"] = self.__updateFCStatus
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __onInitItem( self, pyViewItem ) :
#		pyRowItem = RowItem( rowGui )
#		pyViewItem.pyRowItem = pyRowItem
#		pyViewItem.addPyChild( pyRowItem )
#		pyRowItem.left = 0
#		pyRowItem.top = 0
		pass

	def __onDrawItem( self, pyViewItem ) :
		familyName = pyViewItem.listItem
		rowInfo = self.__FCDatas[familyName]
		pyViewItem.refreshInfo( rowInfo )

	def __updateFCStatus( self, relatedFamily ) :
		"""
		��ʼ�����������ս
		@param	relatedFamily : ״̬�����仯�ĵļ�������
		@type	relatedFamily : str
		"""
		player = BigWorld.player()
		FCDatas = player.challengeFamilyData
		fcUnit = FCDatas.get( relatedFamily, None )
		if fcUnit is None :											# ��ս����
			if relatedFamily not in self.__FCDatas : return
			self.__pyInfoPanel.removeItem( relatedFamily )
			del self.__FCDatas[ relatedFamily ]
		else :														# ��ս��ʼ
			rowInfo = [ ( fcUnit[0], cscolors["c21"] ) ]			# ( ��������, ������ɫ����ɫ�� )
			lastTime = int( fcUnit[2] )
			timeText = self.__convertTimeText( lastTime )			# ת��ΪXXʱXX��XX��ĸ�ʽ
			rowInfo.append( timeText )								# ʣ��ʱ��
			rowInfo.append( ( fcUnit[1], cscolors["c6"] ) )			# ����������ᣨ��ɫ��
			rowInfo.append( time.time() + lastTime )				# �������ʱ��
			isNew = relatedFamily not in self.__FCDatas				# �ж��Ƿ��Ѵ���,��ֹ�����������
			self.__FCDatas[ relatedFamily ] = rowInfo
			if isNew :
				self.__pyInfoPanel.addItem( relatedFamily )
			else :
				index = self.__pyInfoPanel.items.index( relatedFamily )
				self.__pyInfoPanel.updateItem( index, relatedFamily )

	def __refresh( self ) :
		"""
		ˢ��ʣ��ʱ��
		"""
		items = self.__pyInfoPanel.items
		for index, familyName in enumerate( items ) :
			rowInfo = self.__FCDatas.get( familyName, None )		# ���ݼ������ƻ�ȡ��Ϣ
			if rowInfo is None : continue
			lastTime = rowInfo[3] - time.time()						# ��ȡʣ��ʱ��
			timeText = self.__convertTimeText( int( lastTime ) )
			rowInfo[1] = timeText
			self.__pyInfoPanel.updateItem( index, familyName )
		self.__refreshCBID = BigWorld.callback( 1.0, self.__refresh )

	def __cancelCallback( self ) :
		if self.__refreshCBID :
			BigWorld.cancelCallback( self.__refreshCBID )
			self.__refreshCBID = 0

	def __convertTimeText( self, lastTime ) :
		hour = lastTime / 3600
		min = lastTime / 60 - hour * 60
		sec = lastTime - hour * 3600 - min * 60
		timeText = ""
		color = cscolors["c4"]										# ����Ĭ����ɫ(��ɫ)
		if hour == 0 and min == 0 :									# ʣ��ʱ�䲻����1����
			if sec :
				timeText += labelGather.getText( "FamilyChallenge:FCStatusWindow", "secs" ) % sec
			else :
				timeText = labelGather.getText( "FamilyChallenge:FCStatusWindow", "fcOver" )
			color = cscolors["c3"]									# ��ɫ
		else :
			if sec : min += 1										# ��������ӽ�λ
			if min == 60 :											# ������Сʱ��λ
				min = 0
				hour += 1
			if hour:
				timeText += labelGather.getText( "FamilyChallenge:FCStatusWindow", "hours" ) % hour							# Сʱ
			if min :
				timeText += labelGather.getText( "FamilyChallenge:FCStatusWindow", "mins" ) % min							# ����
		return ( timeText, color )									# ���������������ɫ

	def __reset( self ) :
		self.__cancelCallback()
		self.__pyInfoPanel.clearItems()
		self.__FCDatas = {}


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		self.__pyInfoPanel.resetState()
		self.__refresh()
		Window.show( self )

	def hide( self ) :
		self.__cancelCallback()
		Window.hide( self )

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ) :
		self.__reset()
		self.hide()