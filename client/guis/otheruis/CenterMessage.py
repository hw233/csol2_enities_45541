# -*- coding: gb18030 -*-
#
# $Id: CenterMessage.py,v 1.4 2008-08-26 02:21:16 huangyongwei Exp $

"""
implement center message for systeminfo1's message
2008.07.23: writen by huangyongwei
"""

import csstatus
import csdefine
import Font
from Weaker import WeakList
from ChatFacade import chatFacade
from guis import *
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText


class CenterMessage( CSRichText, RootGUI ) :
	__cc_hold_time = 3.0

	def __init__( self ) :
		CSRichText.__init__( self )
		RootGUI.__init__( self, CSRichText.getGui( self ) )
		self.posZSegment = ZSegs.L3
		self.enable = False
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.opGBLink = True
		self.addToMgr()
		self.h_dockStyle = "CENTER"
		self.__initialize()

		self.__holdCBID = 0							# ά���ı���ʾһ��ʱ��� callbackID
		self.__fadeCBID = 0							# ����ʱ�� callbackID

	def dispose( self ) :
		BigWorld.cancelCallback( self.__holdCBID )
		RootGUI.dispose( self )
		CSRichText.dispose( self )

	def __del__( self ) :
		if Debug.output_del_CenterMessage :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		self.__fader = GUI.AlphaShader()
		self.__fader.speed = 0.5
		self.__fader.value = 0
		self.__fader.reset()
		self.getGui().addShader( self.__fader )

		self.r_center = 0							# ����Ϊˮƽ��Ļ�м�
		self.r_middle = 0							# ����Ϊ��ֱ��Ļ�м�
		self.backColor = ( 0, 0, 0, 0 )

	# -------------------------------------------------
	def __endHolding( self ) :
		self.__fader.value = 0
		self.__fadeCBID = BigWorld.callback( self.__fader.speed, self.hide )

	def __canShow( self ):
		if rds.viewInfoMgr.getSetting( "hide", "centerMessage" ):
			return False
		return True

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		CSRichText.generateEvents_( self )
		RootGUI.generateEvents_( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, message, font, fontSize, color ) :
		"""
		��ʾ������ʾ��Ϣ
		"""
		if not self.__canShow(): return
		msg_temp = message.split("/ltime")
		if len( msg_temp ) > 1:
			message = msg_temp[0]
			msg_lasttime = int(msg_temp[1])
		else :
			msg_lasttime = self.__cc_hold_time
		self.text = message
		if self.font != font :
			self.font = font
		if self.fontSize != fontSize :
			self.fontSize = fontSize
		if self.foreColor != color :
			self.foreColor = color
		self.r_center = 0
		RootGUI.show( self )
		self.__fader.value = 1
		BigWorld.cancelCallback( self.__holdCBID )
		BigWorld.cancelCallback( self.__fadeCBID )
		self.__holdCBID = BigWorld.callback( msg_lasttime, self.__endHolding )

	def hide( self ) :
		BigWorld.cancelCallback( self.__holdCBID )
		RootGUI.hide( self )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	left = RootGUI.left
	r_left = RootGUI.r_left
	center = RootGUI.center
	r_center = RootGUI.r_center
	right = RootGUI.right
	r_right = RootGUI.r_right
	top = RootGUI.top
	r_top = RootGUI.r_top
	middle = RootGUI.middle
	r_middle = RootGUI.r_middle
	bottom = RootGUI.bottom
	r_bottom = RootGUI.r_bottom
	visible = property( RootGUI._getVisible, lambda self, vs : vs )		# ���� visible ������Ч


# --------------------------------------------------------------------
# װ�������򷱰汾���������Ͳ���ͬ��
# --------------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator
class deco_getFontInfo( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, statusID ) :
		"""
		����ID��ȡ������Ϣ
		"""
		return Font.defFontSize, Font.defFont


# --------------------------------------------------------------------
# implement center message manager
# --------------------------------------------------------------------
class CenterMessageController :
	__cc_max_lines	= 3							# �����ʾ6��
	__cc_spacing	= 10						# �м��
	__cc_v_site		= 0.25						# ��ֱ�������ʾλ�ã�Ŀǰ��Ϊ��Ļ 3/10 λ�ô���

	def __init__( self ) :
		self.__pyMsgs = []
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_SC_HINT, self.__showMessage )
		chatFacade.bindStatus( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA, self.__onStatusMsg )
		chatFacade.bindStatus( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA, self.__onStatusMsg )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		"""
		�������������ı���λ��
		"""
		pyTmpMsg = self.__pyMsgs[0]
		for index in xrange( 1, len( self.__pyMsgs ) ) :
			pyMsg = self.__pyMsgs[index]
			if not pyMsg.visible : continue
			pyMsg.bottom = pyTmpMsg.top - self.__cc_spacing
			pyTmpMsg = pyMsg

	def __showMessage( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		����Ƶ�� 1 �¼�����ʾһ����Ϣ
		"""
		if not rds.statusMgr.isInWorld() :
			return
		pyMsg = self.__getPyMsgObj( msg )
		color = channel.color
		if len( color ) == 3 :
			color = tuple( color ) + ( 255, )
		pyMsg.r_top = 1 - self.__cc_v_site * 2
		pyMsg.show( msg, Font.defFont, Font.defFontSize, color )
		self.__layout()

	def __onStatusMsg( self, statusID, msg ) :
		"""
		�յ��󶨵�״̬��Ϣ
		"""
		if not rds.statusMgr.isInWorld() :
			return
		pyMsg = self.__getPyMsgObj( msg )
		pyMsg.r_top = 1 - self.__cc_v_site * 2
		fontSize, font = self.__getFontInfo( statusID )
		color = 255,255,255,255
		pyMsg.show( msg, font, fontSize, color )
		self.__layout()

	@deco_getFontInfo
	def __getFontInfo( self, statusID ) :
		"""
		����ID��ȡ������Ϣ
		"""
		return 14, "msyhbd.ttf"

	def __getPyMsgObj( self, msg ) :
		"""
		��ȡһ��CenterMessageʵ��
		"""
		pyMsgs = self.__pyMsgs
		pyMsg = None
		if len( pyMsgs ) > 0 and \
			pyMsgs[0].text == msg :				# ���ǰһ����Ϣ��Ŀǰ����Ϣ����һ��������˵�
				pyMsg = pyMsgs[0]
		elif len( pyMsgs ) >= self.__cc_max_lines :
			pyMsg = pyMsgs[-1]
		else :
			for pyObj in pyMsgs :
				if not pyObj.visible :
					pyMsg = pyObj
					break
			else :
				pyMsg = CenterMessage()
				pyMsgs.insert( 0, pyMsg )
		pyMsgs.remove( pyMsg )
		pyMsgs.insert( 0, pyMsg )
		return pyMsg
