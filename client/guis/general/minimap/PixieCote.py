# -*- coding: gb18030 -*-

import re
import GUI
import ResMgr
import BigWorld
from gbref import rds
from Helper import pixieHelper
from LabelGather import labelGather
from AbstractTemplates import Singleton

from guis import Debug
from guis import s_util
from guis.UIFixer import uiFixer
from guis.uidefine import MIStyle
from guis.common.FrameEx import HVFrameEx
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem


class PixieMenu( ContextMenu, Singleton ) :
	"""小精灵功能按钮"""
	def __init__( self ) :
		ContextMenu.__init__( self )
		self.__pyMIs = []										# 菜单项引用列表
		self.__initialize()

	def __initialize( self ) :
		"""初始化菜单项"""
		def createMI( pyParent, label, cloven = True, style = MIStyle.COMMON ) :
			text = labelGather.getText( "minmap:pixie", label )
			pyMI = DefMenuItem( text, style )
			pyParent.add( pyMI )
			if cloven :
				pyST = DefMenuItem( style = MIStyle.SPLITTER )
				pyParent.add( pyST )
			self.__pyMIs.append( pyMI )
			return pyMI
		# 不能随便调整下面的创建顺序
		pyMI = createMI( self, "miConjure" )												# 召唤精灵
		pyMI.onLClick.bind( self.__conjurePixie )
		pySTMI = createMI( self, "miSetting" )												# 精灵设置
		pyMI = createMI( pySTMI.pySubItems, "miShowDirection", False, MIStyle.CHECKABLE )	# 精灵指引
		pyMI.pyCheckBox_.onCheckChanged.bind( self.__enableDirection )
		#pyMI = createMI( pySTMI.pySubItems, "miShowGossip", False, MIStyle.CHECKABLE )		# 精灵闲话	------- 暂时去掉闲话功能
		#pyMI.pyCheckBox_.onCheckChanged.bind( self.__enableGossip )
		pyMI = createMI( pySTMI.pySubItems, "miShareVIP", False, MIStyle.CHECKABLE )		# VIP共享
		pyMI.pyCheckBox_.onCheckChanged.bind( self.__enableShareVIP )
		pyMI = createMI( pySTMI.pySubItems, "miShowVIPFlag", False, MIStyle.CHECKABLE )		# 显示VIP标识
		pyMI.pyCheckBox_.onCheckChanged.bind( self.__visibleVIPFlag )
		pyMI = createMI( self, "miWithdraw", False )										# 收回精灵
		pyMI.onLClick.bind( self.__withdrawPixie )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __conjurePixie( self ) :
		BigWorld.player().conjureEidolon()

	def __withdrawPixie( self ) :
		BigWorld.player().withdrawEidolon()

	def __enableDirection( self, checked ) :
		pixieHelper.enableDirection( checked )

	def __enableGossip( self, checked ) :
		pixieHelper.enableGossip( checked )

	def __enableShareVIP( self, checked ) :
		BigWorld.player().vipShareSwitch()

	def __visibleVIPFlag( self, checked ) :
		pixieHelper.visibleVIPFlag( checked )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refresh( self ) :
		"""刷新状态"""
		self.__pyMIs[2].checked = pixieHelper.isInDirecting()
		#self.__pyMIs[3].checked = pixieHelper.isInGossipping()
		self.__pyMIs[3].pyCheckBox_.onCheckChanged.unbind( self.__enableShareVIP )
		self.__pyMIs[3].checked = False						# 默认关闭VIP共享
		self.__pyMIs[3].pyCheckBox_.onCheckChanged.bind( self.__enableShareVIP )
		self.__pyMIs[4].checked = pixieHelper.isVipFlagShow()

	def onRoleEnterWorld( self ) :
		"""玩家上线"""
		self.refresh()

	def onRoleLeaveWorld( self ) :
		"""玩家下线"""
		pass

class PixieBubble( HVFrameEx, RootGUI ) :
	"""随机帮助提示"""
	__cc_dressTpl = re.compile("(?<=_)\d(?=\.\w{3,3})")		# 泡泡风格替换表达式

	def __init__( self ) :
		bubble = GUI.load( "guis/general/minimap/pixiebubble.gui" )
		uiFixer.firstLoadFix( bubble )
		RootGUI.__init__( self, bubble )
		HVFrameEx.__init__( self, bubble )
		self.crossFocus = False
		self.focus = False
		self.movable_ = False
		self.escHide_ = False
		self.minHeight_ += bubble.elements["frm_pointer"].size.y
		self.addToMgr()

		self.__pyRtMsg = CSRichText( bubble.rtMsg )
		self.__hide_cbid = 0

	def __del__( self ) :
		if Debug.output_del_BubbleTip :
			INFO_MSG( str( self ) )

	def __layout( self ) :
		"""
		设置窗口适应文本大小
		"""
		self.size = self.__pyRtMsg.size + ( 35, 15 )						# 受到最小高度和宽度的限制，实际尺寸可能与计算结果不一样
		self.__pyRtMsg.center = s_util.getFElemCenter( self.gui.elements["frm_t"] )
		self.__pyRtMsg.middle = s_util.getFElemMiddle( self.gui.elements["frm_l"] )

	def __dressUp( self ) :
		"""换装"""
		if rds.viewInfoMgr.getSetting( "bubble", "style" ) :				# 泡泡风格
			style_str = "1"
		else :
			style_str = "0"
		for elem in self.getGui().elements.itervalues():
			elem.texture = self.__cc_dressTpl.sub( style_str, elem.texture )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, msg ) :
		RootGUI.show( self )
		BigWorld.cancelCallback( self.__hide_cbid )
		show_time = max( 5, len( msg ) / 7 )								# 根据文本长短设置显示时间，最少提示5秒
		self.__hide_cbid = BigWorld.callback( show_time, self.hide )
		self.__dressUp()
		self.__pyRtMsg.text = msg
		self.__layout()

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		HVFrameEx._setWidth( self, width )
		pt = self.gui.elements["frm_pointer"]
		pt.position.x = self.width - pt.size.x

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HVFrameEx._getWidth, _setWidth )