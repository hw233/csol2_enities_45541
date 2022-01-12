# -*- coding: gb18030 -*-
#
# $Id: LotteryWindow.py,v 1.00 2008/09/6 11:19:09 huangdong Exp $

from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from ItemsFactory import ObjectItem as ItemInfo
from guis.tooluis.CSRichText import CSRichText
from LotteryItem import LotteryItem
import event.EventCenter as ECenter
from Function import Functor
from LabelGather import labelGather
import math
import sys

RADI_UNIT = math.pi/8		# ָ��ÿ��һ��Ļ���

class LotteryWindow( Window ):
	"""
	���ҵĽ���
	"""
	round = 5	#��ת������Ȧ��
	speedcorrect = 35.0		# �ٶȵ�����ֵ������Э��������ٶȣ�
	velocity = 4.0			# ��ʼ�ٶ�
	radians_map = { 0: 0, 1:1, 2:3, 3:4, 4:5, 5:7, 6:8, 7:9, 8:11, 9:12, 10:13, 11:15 } #��Ʒ�����Ӧָ��ָ��
	lottDsp = labelGather.getText( "LotteryWindow:main", "miLottDsp" )

	def __init__( self ):
		"""
		��ʼ������
		"""
		wnd = GUI.load( "guis/general/lottery/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.escHide_ = False							# �����԰� ESC ������
		self.__pyItems  = {}		#�洢���е�ITEM
		self.__pointerRadians = {}		#ָ�뻡��
		self.__triggers = {}		#ע����Ϣ
		self.__registerTriggers()	#ע����Ϣ
		self.resultPosFirst =  -1	#��¼��ת�Ľ��λ��1(��һ����ת��Ϻ��λ��)
		self.resultPosSecond =  -1	#��¼��ת�Ľ��λ��2���ڶ�����ת��Ϻ��λ�ã�
		self.selectIndex = 0		#��¼��ǰ��ɫ��ָ���λ��
		self.beginIndex = 0			#��¼��ת��ʼ��λ��
		self.speed = self.velocity	#��ת����ʼ�ٶ�
		self.distance = 0.0			#��ת�ĳ���
		self.acceleration = 0.0		#��ת�ļ��ٶ�
		self.callBackID = 0 		#��ȡʱʹ�õ�CALLBACKID
		self.__initialize( wnd )

	def	__initialize( self, wnd ):
		"""
		��ʼ�����еĿؼ�
		"""
		self.__pyGetBtn = HButtonEx( wnd.btnGet )
		self.__pyGetBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyGetBtn.onLClick.bind( self.__getItem )

		self.__pyAgainBtn	= HButtonEx( wnd.btnAgain )
		self.__pyAgainBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyAgainBtn.onLClick.bind( self.__lotteryAgain )

		self.__pointer = wnd.pointer
		util.rotateGui( self.__pointer, 0 ) #��ʼ��ʱ��ָ��
		for name, item in wnd.children:		#��ʼ��ITEM
			if name.startswith( "item" ):
				order = int( name.split( "_" )[1] )	#ȡ��ITEM��λ��  -1����Ϊitem�������Ǵ�1��ʼ������������������order�Ǵ�0��ʼ
				ltItem = LotteryItem( item )
				self.__pyItems[order] = ltItem

		self.__pyRtDsp = CSRichText( wnd.rtDsp )
		self.__pyRtDsp.foreColor = ( 230, 227, 185, 255 )
		self.__pyRtDsp.charSpace = -2
		self.__pyRtDsp.text = self.lottDsp

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "LotteryWindow:main", "lbTitle" )
		labelGather.setPyBgLabel( self.__pyGetBtn, "LotteryWindow:main", "getBtn" )
		labelGather.setPyBgLabel( self.__pyAgainBtn, "LotteryWindow:main", "againBtn" )

	def __registerTriggers( self ):
		"""
		ע����Ϣ
		"""
		self.__triggers["EVT_ON_LOTTERY_UPDATAITEM"]		= self.__onUpdateItem		# ����ITEM
		self.__triggers["EVT_ON_LOTTERY_UPDATAPOS"]	 		= self.__onUpdatePos		# ��¼2����Ʒ��λ��
		self.__triggers["EVT_ON_SHOW_LOTTERYWINDOW"]		= self.show					# ��ʾ��������
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# ----------------------------------------------------------------------------
	def __onUpdateItem( self, itemInfo, order):
		"""
		��ʾ��Ʒ
		"""
		pyItem = self.__pyItems.get( order )
		if not pyItem:
			return
		pyItem.update( itemInfo )
		if order == 0:
			pyItem.selected = True

	def __onUpdatePos( self, firstChance, secondChance ):
		"""
		��¼��ת���Ŀ��,����ʼ��һ����ת(�������ʾ�Ѿ������������Ʒ)
		"""
		self.resultPosFirst = firstChance		#��һ����ת��Ӧ�õõ�����Ʒ
		self.resultPosSecond = secondChance		#�ڶ�����ת��Ӧ�õõ�����Ʒ
		self.__beginLottery( self.resultPosFirst, 0, self.firstlotteryOver )

	def __getItem( self ):
		"""
		֪ͨ������ȡ����Ʒ������
		"""
		self.hide()

	def __lotteryAgain( self ):
		"""
		��ʼ��ת��ȡ�µ���Ʒ
		"""
		BigWorld.player().changelotteryItem()
		self.__beginLottery( self.resultPosSecond, self.resultPosFirst, self.secondlotteryOver )

	def __beginLottery( self, resultOrder, beginOrder, callback ):
		"""
		��ʼ��ȡ,����ֻ����Ϊ�ͻ��˱���
		"""
		if resultOrder == -1:
			return
		self.__pyGetBtn.enable = False
		self.__pyAgainBtn.enable = False
		self.pyCloseBtn_.enable = False
		self.selectIndex = 0													#��ʼ������ת������
		self.beginIndex = beginOrder											#��һ����ת�������λ��
		util.rotateGui( self.__pointer, beginOrder*RADI_UNIT )
		if resultOrder < beginOrder:											#�����ʼλ�������ڽ���λ������֮��
			lastRoundDist = 12 - beginOrder + resultOrder 						#�������һȦ��Ҫ�ߵľ���
		else:
			lastRoundDist = resultOrder - beginOrder
		self.distance =  float( self.round * 12  + lastRoundDist )				#�������( ��Ҫ��ת�ĸ���,������Ȧ��*12�� + ���һȦ��λ�� )
		self.acceleration = (self.speed * self.speedcorrect) / self.distance	#������ٶ�( ���ٶ����Լ����Գ����� )
		self.callBackID = BigWorld.callback( 0.0, Functor( self.__display, callback ) )

	def firstlotteryOver( self ):
		"""
		��һ����ת��Ϻ����
		"""
		self.__pyGetBtn.enable = True
		self.__pyAgainBtn.enable = True
		self.pyCloseBtn_.enable = True
		self.speed = self.velocity	#��ת����ʼ�ٶ�

	def secondlotteryOver( self ):
		"""
		�ڶ�����ת��Ϻ����
		"""
		self.__pyGetBtn.enable = True
		self.pyCloseBtn_.enable = True

	def __display( self, callback ):
		"""
		��ʾ��ת��ͼ��
		"""
		self.speed += self.acceleration					#�ٶ�����
		preItem  = self.__pyItems[( self.selectIndex + self.beginIndex ) % 12 ]
		preItem.selected = False
		self.selectIndex += 1						#���Ӽ���
		selectedIndex = ( self.selectIndex + self.beginIndex ) % 12
		item  = self.__pyItems[selectedIndex]
		item.selected = True
		pointIndex = self.radians_map[selectedIndex] - 2
		util.rotateGui( self.__pointer, pointIndex*RADI_UNIT ) #����ָ��ָ��
		if self.selectIndex == int( self.distance / 2 ):
			self.acceleration = - ( ( self.speed - 1.0 ) * 2.0 / self.distance )	#�������ڵ��ٶ�����һ���·�̽���1.5��Ҫ�ļ��ٶ�
		if self.selectIndex >= self.distance or self.speed == 0.0:
			if self.selectIndex != self.distance or self.speed == 0.0 or ( self.selectIndex%12 != self.resultPosFirst and self.selectIndex%12 != self.resultPosSecond  ):	#�������ʵ���ǲ������� ���������Ϣ�Ͳ����Ա����ԭ��
				ERROR_MSG( "lottery a wrong item, self.selectIndex = %s, self.distance = %s, self.speed = %s, self.resultPosFirst = %s,self.resultPosSecond = %s" % ( self.selectIndex,self.distance,self.speed,self.resultPosFirst,self.resultPosSecond ) )
			callback()
			BigWorld.cancelCallback( self.callBackID )
			return
		BigWorld.cancelCallback( self.callBackID )
		next =  1.0 / self.speed	#������һ����ʾ��ʱ��
		self.callBackID = BigWorld.callback( next , Functor( self.__display, callback ) )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ) :
		self.allClear()

	def onLeaveWorld( self ) :
		self.hide()

	def show( self ) :
		self.allClear()
		Window.show( self )

	def hide( self ):
		BigWorld.player().lotteryGetItem()
		self.allClear()
		Window.hide( self )

	def allClear(self ):
		"""
		������еĿؼ���ֵ
		"""
		for key in self.__pyItems:
			self.__pyItems[key].clearItem()
		self.__pyGetBtn.enable = True
		self.__pyAgainBtn.enable = True
		self.resultPosFirst =  -1		#��¼��ת�Ľ��λ��1(��һ����ת��Ϻ��λ��)
		self.resultPosSecond =  -1		#��¼��ת�Ľ��λ��2���ڶ�����ת��Ϻ��λ�ã�
		self.selectIndex = 0				#��¼��ǰ��ɫ��ָ���λ��
		self.beginIndex = 0			#��¼��ת��ʼ��λ��
		self.speed = self.velocity	#��ת����ʼ�ٶ�
		self.distance = 0.0			#��ת�ĳ���
		self.acceleration = 0.0		#��ת�ļ��ٶ�
		self.callBackID = 0 		#��ȡʱʹ�õ�CALLBACKID
		util.rotateGui( self.__pointer, 0 )