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

RADI_UNIT = math.pi/8		# 指针每调一格的弧度

class LotteryWindow( Window ):
	"""
	锦囊的界面
	"""
	round = 5	#旋转完整的圈数
	speedcorrect = 35.0		# 速度的修正值（用于协助计算加速度）
	velocity = 4.0			# 初始速度
	radians_map = { 0: 0, 1:1, 2:3, 3:4, 4:5, 5:7, 6:8, 7:9, 8:11, 9:12, 10:13, 11:15 } #物品格与对应指针指向
	lottDsp = labelGather.getText( "LotteryWindow:main", "miLottDsp" )

	def __init__( self ):
		"""
		初始化界面
		"""
		wnd = GUI.load( "guis/general/lottery/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.escHide_ = False							# 不可以按 ESC 键隐藏
		self.__pyItems  = {}		#存储所有的ITEM
		self.__pointerRadians = {}		#指针弧度
		self.__triggers = {}		#注册消息
		self.__registerTriggers()	#注册消息
		self.resultPosFirst =  -1	#记录旋转的结果位置1(第一次旋转完毕后的位置)
		self.resultPosSecond =  -1	#记录旋转的结果位置2（第二次旋转完毕后的位置）
		self.selectIndex = 0		#记录当前红色框指向的位置
		self.beginIndex = 0			#记录旋转开始的位置
		self.speed = self.velocity	#旋转的起始速度
		self.distance = 0.0			#旋转的长度
		self.acceleration = 0.0		#旋转的加速度
		self.callBackID = 0 		#抽取时使用的CALLBACKID
		self.__initialize( wnd )

	def	__initialize( self, wnd ):
		"""
		初始化所有的控件
		"""
		self.__pyGetBtn = HButtonEx( wnd.btnGet )
		self.__pyGetBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyGetBtn.onLClick.bind( self.__getItem )

		self.__pyAgainBtn	= HButtonEx( wnd.btnAgain )
		self.__pyAgainBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyAgainBtn.onLClick.bind( self.__lotteryAgain )

		self.__pointer = wnd.pointer
		util.rotateGui( self.__pointer, 0 ) #初始化时的指向
		for name, item in wnd.children:		#初始化ITEM
			if name.startswith( "item" ):
				order = int( name.split( "_" )[1] )	#取出ITEM的位置  -1是因为item的索引是从1开始，而服务器发过来的order是从0开始
				ltItem = LotteryItem( item )
				self.__pyItems[order] = ltItem

		self.__pyRtDsp = CSRichText( wnd.rtDsp )
		self.__pyRtDsp.foreColor = ( 230, 227, 185, 255 )
		self.__pyRtDsp.charSpace = -2
		self.__pyRtDsp.text = self.lottDsp

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "LotteryWindow:main", "lbTitle" )
		labelGather.setPyBgLabel( self.__pyGetBtn, "LotteryWindow:main", "getBtn" )
		labelGather.setPyBgLabel( self.__pyAgainBtn, "LotteryWindow:main", "againBtn" )

	def __registerTriggers( self ):
		"""
		注册消息
		"""
		self.__triggers["EVT_ON_LOTTERY_UPDATAITEM"]		= self.__onUpdateItem		# 更新ITEM
		self.__triggers["EVT_ON_LOTTERY_UPDATAPOS"]	 		= self.__onUpdatePos		# 记录2号物品的位置
		self.__triggers["EVT_ON_SHOW_LOTTERYWINDOW"]		= self.show					# 显示整个窗口
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# ----------------------------------------------------------------------------
	def __onUpdateItem( self, itemInfo, order):
		"""
		显示物品
		"""
		pyItem = self.__pyItems.get( order )
		if not pyItem:
			return
		pyItem.update( itemInfo )
		if order == 0:
			pyItem.selected = True

	def __onUpdatePos( self, firstChance, secondChance ):
		"""
		记录旋转后的目标,并开始第一次旋转(到这里表示已经发送完毕了物品)
		"""
		self.resultPosFirst = firstChance		#第一次旋转后应该得到的物品
		self.resultPosSecond = secondChance		#第二次旋转后应该得到的物品
		self.__beginLottery( self.resultPosFirst, 0, self.firstlotteryOver )

	def __getItem( self ):
		"""
		通知服务器取出物品到背包
		"""
		self.hide()

	def __lotteryAgain( self ):
		"""
		开始旋转抽取新的物品
		"""
		BigWorld.player().changelotteryItem()
		self.__beginLottery( self.resultPosSecond, self.resultPosFirst, self.secondlotteryOver )

	def __beginLottery( self, resultOrder, beginOrder, callback ):
		"""
		开始抽取,这里只是作为客户端表现
		"""
		if resultOrder == -1:
			return
		self.__pyGetBtn.enable = False
		self.__pyAgainBtn.enable = False
		self.pyCloseBtn_.enable = False
		self.selectIndex = 0													#初始化已旋转的索引
		self.beginIndex = beginOrder											#第一次旋转结束后的位置
		util.rotateGui( self.__pointer, beginOrder*RADI_UNIT )
		if resultOrder < beginOrder:											#如果开始位置索引在结束位置索引之后
			lastRoundDist = 12 - beginOrder + resultOrder 						#计算最后一圈需要走的距离
		else:
			lastRoundDist = resultOrder - beginOrder
		self.distance =  float( self.round * 12  + lastRoundDist )				#计算距离( 即要旋转的格数,完整的圈数*12格 + 最后一圈的位置 )
		self.acceleration = (self.speed * self.speedcorrect) / self.distance	#计算加速度( 该速度是自己调试出来的 )
		self.callBackID = BigWorld.callback( 0.0, Functor( self.__display, callback ) )

	def firstlotteryOver( self ):
		"""
		第一次旋转完毕后调用
		"""
		self.__pyGetBtn.enable = True
		self.__pyAgainBtn.enable = True
		self.pyCloseBtn_.enable = True
		self.speed = self.velocity	#旋转的起始速度

	def secondlotteryOver( self ):
		"""
		第二次旋转完毕后调用
		"""
		self.__pyGetBtn.enable = True
		self.pyCloseBtn_.enable = True

	def __display( self, callback ):
		"""
		显示旋转的图像
		"""
		self.speed += self.acceleration					#速度增加
		preItem  = self.__pyItems[( self.selectIndex + self.beginIndex ) % 12 ]
		preItem.selected = False
		self.selectIndex += 1						#增加计数
		selectedIndex = ( self.selectIndex + self.beginIndex ) % 12
		item  = self.__pyItems[selectedIndex]
		item.selected = True
		pointIndex = self.radians_map[selectedIndex] - 2
		util.rotateGui( self.__pointer, pointIndex*RADI_UNIT ) #更新指针指向
		if self.selectIndex == int( self.distance / 2 ):
			self.acceleration = - ( ( self.speed - 1.0 ) * 2.0 / self.distance )	#计算现在的速度走完一半的路程降到1.5需要的加速度
		if self.selectIndex >= self.distance or self.speed == 0.0:
			if self.selectIndex != self.distance or self.speed == 0.0 or ( self.selectIndex%12 != self.resultPosFirst and self.selectIndex%12 != self.resultPosSecond  ):	#这种情况实际是不正常的 输出错误消息和参数以便分析原因
				ERROR_MSG( "lottery a wrong item, self.selectIndex = %s, self.distance = %s, self.speed = %s, self.resultPosFirst = %s,self.resultPosSecond = %s" % ( self.selectIndex,self.distance,self.speed,self.resultPosFirst,self.resultPosSecond ) )
			callback()
			BigWorld.cancelCallback( self.callBackID )
			return
		BigWorld.cancelCallback( self.callBackID )
		next =  1.0 / self.speed	#计算下一次显示的时间
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
		清除所有的控件的值
		"""
		for key in self.__pyItems:
			self.__pyItems[key].clearItem()
		self.__pyGetBtn.enable = True
		self.__pyAgainBtn.enable = True
		self.resultPosFirst =  -1		#记录旋转的结果位置1(第一次旋转完毕后的位置)
		self.resultPosSecond =  -1		#记录旋转的结果位置2（第二次旋转完毕后的位置）
		self.selectIndex = 0				#记录当前红色框指向的位置
		self.beginIndex = 0			#记录旋转开始的位置
		self.speed = self.velocity	#旋转的起始速度
		self.distance = 0.0			#旋转的长度
		self.acceleration = 0.0		#旋转的加速度
		self.callBackID = 0 		#抽取时使用的CALLBACKID
		util.rotateGui( self.__pointer, 0 )