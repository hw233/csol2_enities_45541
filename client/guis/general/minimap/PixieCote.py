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
	"""С���鹦�ܰ�ť"""
	def __init__( self ) :
		ContextMenu.__init__( self )
		self.__pyMIs = []										# �˵��������б�
		self.__initialize()

	def __initialize( self ) :
		"""��ʼ���˵���"""
		def createMI( pyParent, label, cloven = True, style = MIStyle.COMMON ) :
			text = labelGather.getText( "minmap:pixie", label )
			pyMI = DefMenuItem( text, style )
			pyParent.add( pyMI )
			if cloven :
				pyST = DefMenuItem( style = MIStyle.SPLITTER )
				pyParent.add( pyST )
			self.__pyMIs.append( pyMI )
			return pyMI
		# ��������������Ĵ���˳��
		pyMI = createMI( self, "miConjure" )												# �ٻ�����
		pyMI.onLClick.bind( self.__conjurePixie )
		pySTMI = createMI( self, "miSetting" )												# ��������
		pyMI = createMI( pySTMI.pySubItems, "miShowDirection", False, MIStyle.CHECKABLE )	# ����ָ��
		pyMI.pyCheckBox_.onCheckChanged.bind( self.__enableDirection )
		#pyMI = createMI( pySTMI.pySubItems, "miShowGossip", False, MIStyle.CHECKABLE )		# �����л�	------- ��ʱȥ���л�����
		#pyMI.pyCheckBox_.onCheckChanged.bind( self.__enableGossip )
		pyMI = createMI( pySTMI.pySubItems, "miShareVIP", False, MIStyle.CHECKABLE )		# VIP����
		pyMI.pyCheckBox_.onCheckChanged.bind( self.__enableShareVIP )
		pyMI = createMI( pySTMI.pySubItems, "miShowVIPFlag", False, MIStyle.CHECKABLE )		# ��ʾVIP��ʶ
		pyMI.pyCheckBox_.onCheckChanged.bind( self.__visibleVIPFlag )
		pyMI = createMI( self, "miWithdraw", False )										# �ջؾ���
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
		"""ˢ��״̬"""
		self.__pyMIs[2].checked = pixieHelper.isInDirecting()
		#self.__pyMIs[3].checked = pixieHelper.isInGossipping()
		self.__pyMIs[3].pyCheckBox_.onCheckChanged.unbind( self.__enableShareVIP )
		self.__pyMIs[3].checked = False						# Ĭ�Ϲر�VIP����
		self.__pyMIs[3].pyCheckBox_.onCheckChanged.bind( self.__enableShareVIP )
		self.__pyMIs[4].checked = pixieHelper.isVipFlagShow()

	def onRoleEnterWorld( self ) :
		"""�������"""
		self.refresh()

	def onRoleLeaveWorld( self ) :
		"""�������"""
		pass

class PixieBubble( HVFrameEx, RootGUI ) :
	"""���������ʾ"""
	__cc_dressTpl = re.compile("(?<=_)\d(?=\.\w{3,3})")		# ���ݷ���滻���ʽ

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
		���ô�����Ӧ�ı���С
		"""
		self.size = self.__pyRtMsg.size + ( 35, 15 )						# �ܵ���С�߶ȺͿ�ȵ����ƣ�ʵ�ʳߴ�������������һ��
		self.__pyRtMsg.center = s_util.getFElemCenter( self.gui.elements["frm_t"] )
		self.__pyRtMsg.middle = s_util.getFElemMiddle( self.gui.elements["frm_l"] )

	def __dressUp( self ) :
		"""��װ"""
		if rds.viewInfoMgr.getSetting( "bubble", "style" ) :				# ���ݷ��
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
		show_time = max( 5, len( msg ) / 7 )								# �����ı�����������ʾʱ�䣬������ʾ5��
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