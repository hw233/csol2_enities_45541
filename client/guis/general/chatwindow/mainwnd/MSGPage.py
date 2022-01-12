# -*- coding: gb18030 -*-
#
# $Id: tabpage.py,v 1.10 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement tabpage for showing chating message

2009/08/26: writen by huangyongwei
"""

import csdefine
import csconst
import event.EventCenter as ECenter
from ChatFacade import chatFacade
from LabelGather import labelGather
from guis import *
from guis.common.RootGUI import RootGUI
from guis.common.WndResizer import WndResizer
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabPage
from MSGTab import MSGTab
from MSGPanel import MSGPanel

class MSGTabPanel( TabPanel ) :
	def onShow( self ) :
		"""������ʾʱ����"""
		TabPanel.onShow( self )
		if self.pyTabPage :
			self.pyTabPage.pyMSGPanel.startPasting()

	def onHide( self ) :
		"""����ر�ʱ����"""
		TabPanel.onShow( self )
		if self.pyTabPage :
			self.pyTabPage.pyMSGPanel.stopPasting()


class MSGPage( Control, TabPage ) :
	__cc_def_color		= 28, 28, 28, 180		# Ĭ�ϱ���ɫ

	def __init__( self, pyBinder ) :
		pg = GUI.load( "guis/general/chatwindow/mainwnd/tpgmsg.gui" )
		uiFixer.firstLoadFix( pg )
		self.__isInitPages = False				# ��ǣ���ֹ�ظ����������¼�
		Control.__init__( self, pg, pyBinder )
		self.__isInitPages = True
		self.__initialize( pg )
		self.color = self.__cc_def_color

		self.__locked = True					# �Ƿ���ס��ҳ
		self.__docked = True					# �Ƿ���ͣ��״̬��ͣ�������ڣ�
		self.deletable_ = True					# �Ƿ���Ա�ɾ��
		self.unlockable_ = False				# �Ƿ�ɱ�����
		self.defCareCHIDs_ = set()				# Ĭ�Ͻ�������Ϣ��Ƶ��
		self.__careCHIDs = set()				# ��������Ϣ��Ƶ������Ϊÿ�յ���Ϣ����Ҫ��ȡ�˹�עƵ����
												# ��ˣ�Ϊ�˲�Ӱ���ٶȣ���������Ϊ����������ֵʱ����ע�⣬
												# Ӧ�ø���һ�� set�������� list �� tuple��

		self.pyFiller_ = None					# ����ʱ������
		self.__cursorToFillerPos = 0, 0			# ��굽 filler ��λ��

	def dispose( self ) :
		if self.pyFiller_ :
			self.pyFiller_.dispose()
			self.pyFiller_ = None
		for chid in self.__careCHIDs :
			chatFacade.unbindChannelHandler( chid, self.__onReceiveMessage )
		Control.dispose( self )

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ChatMSGPage :
			INFO_MSG( str( self ) )

	def __initialize( self, pg ) :
		pyBtnTab = MSGTab( pg.btnTab )						# TabButton
		pyBtnTab.onRMouseUp.bind( self.__onTabRMouseUp )
		pyTPBg = MSGTabPanel( pg.tpMSG )					# MSGTabPanel
		TabPage.__init__( self, pyBtnTab, pyTPBg )
		self.pyMSGPanel_ = MSGPanel( pg.tpMSG.cpMSG, pg.tpMSG.sbar )
		self.pyMSGPanel_.h_dockStyle = "HFILL"
		self.pyMSGPanel_.v_dockStyle = "VFILL"


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		if self.__isInitPages :
			TabPage.generateEvents_( self )
			Control.generateEvents_( self )
			self.__onTabMouseUp = self.createEvent_( "onTabMouseUp" )
			del self.__isInitPages

	@property
	def onTabMouseUp( self ) :
		return self.__onTabMouseUp


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onTabRMouseUp( self, pyBtn ) :
		"""
		����Ҽ���� tab ��ťʱ������
		"""
		self.onTabMouseUp( pyBtn )

	# -------------------------------------------------
	def __onReceiveMessage( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		����Ƶ����Ϣ
		"""
		if channel.id not in self.__careCHIDs : return
		msg_temp = msg.split("/ltime")
		if len( msg_temp ) > 1 :
			msg = msg_temp[0]
		msg = channel.formatMsg( spkID, spkName, msg )
		self.pyMSGPanel_.addChanelMessage( channel, msg )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelectChanged_( self, selected ) :
		"""
		ҳ����ʾ/����ʱ������
		"""
		TabPage.onSelectChanged_( self, selected )

	def onMenuItemClick_( self, pyItem ) :
		"""
		�˵�ѡ�����Ǵ���
		"""
		pass

	# ---------------------------------------
	def onStartDrag_( self ) :
		"""
		��ʼ�϶�ҳ��
		"""
		if self.__docked :											# ����ͣ��״̬
			btnLeft = self.pyBtn.left								# ��¼ undock ǰ��ť��λ��
			self.undock( self.posToScreen )							# ���븸��( tab ��ť�������� )
			space = btnLeft - self.pyBtn.left						# ��ť�����߶��ľ���
			self.pyFiller_.left += space							# ������������
		self.__cursorToFillerPos = self.pyFiller_.mousePos			# ��¼�������� filler ��λ��

	def onDragging_( self ) :
		"""
		�϶�ҳ��
		"""
		cx, cy = csol.pcursorPosition()
		x, y = self.__cursorToFillerPos
		self.pyFiller_.pos = cx - x, cy - y
		self.pyBinder.onPageMoving_( self )

	def onStopDrag_( self ) :
		"""
		����ҳ���϶�
		"""
		self.pyBinder.onPageStopMoving_( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		if self.pyBtn.isMouseHit() :
			return True
		return self.pyPanel.isMouseHit()

	# -------------------------------------------------
	def reset( self ) :
		"""
		����Ƶ��ΪĬ�����ã���ɫ��������ʱ���ã�
		"""
		self.pyMSGPanel_.clearMessages()
		self.__careCHIDs.clear()
		self.careCHIDs = self.defCareCHIDs_
		self.color = self.__cc_def_color

	# -------------------------------------------------
	def dock( self, index ) :
		"""
		����Ϊͣ��״̬
		"""
		self.__docked = True
		if self.pyFiller_ :
			self.pyFiller_.dispose()
			self.pyFiller_ = None
		self.pyBinder.onPageDocked_( self, index )

	def undock( self, pos ) :
		"""
		ȡ��ͣ�������Ƶ�ָ��λ����
		"""
		self.__docked = False							# ȡ��ͣ��
		self.__locked = False							# ȡ������״̬
		self.pyBinder.onPageLeft_( self )				# ֪ͨ���븸��
		self.pyFiller_ = PageWindow( self, pos )		# ��ӵ����봰����
		self.selected = True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPGName( self ) :
		return self.pyBtn.text

	def _setPGName( self, name ) :
		self.pyBtn.text = name

	# ---------------------------------------
	def _getColor( self ) :
		return self.pyPanel.color

	def _setColor( self, color ) :
		self.pyBtn.selectedBackColor = color
		self.pyPanel.color = color

	# -------------------------------------------------
	def _setLocked( self, lock ) :
		if self.unlockable_ :					# �����Ա�����
			self.__locked = True
		else :
			self.__locked = lock

	# -------------------------------------------------
	def _getCareCHIDs( self ) :
		return self.__careCHIDs

	def _setCareCHIDs( self, chids ) :
		news = chids.difference( self.__careCHIDs )
		olds = self.__careCHIDs.difference( chids )
		self.__careCHIDs = set([])
		self.__careCHIDs.update( chids )
		for chid in news :
			chatFacade.bindChannelHandler( chid, self.__onReceiveMessage )
		for chid in olds :
			chatFacade.unbindChannelHandler( chid, self.__onReceiveMessage )

	# -------------------------------------------------
	def _getPos( self ) :
		if self.pyFiller_ :
			return self.pyFiller_.pos
		return Control._getPos( self )

	def _setPos( self, pos ) :
		if self.pyFiller_ :
			self.pyFiller_.pos = pos
		else :
			Control._setPos( self, pos )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyMSGPanel = property( lambda self : self.pyMSGPanel_ )				# GUIBaseObject: ��ʾ��Ϣ�İ���
	enable = property( lambda self : True, lambda self, v : v )			# bool: ���� enable ����
	pgName = property( _getPGName, _setPGName )							# str: ��ȡ/����ҳ��
	color = property( _getColor, _setColor )							# Color/tuple: ��ȡ/���ð�����ɫ
	unlockable = property( lambda self : self.unlockable_ )				# bool: ��ȡ��ҳ�Ƿ���Ա�����
	deletable = property( lambda self : self.deletable_ )				# bool: ��ȡ��ҳ�Ƿ�ɱ�ɾ��
	locked = property( lambda self : self.__locked, _setLocked )		# bool: ��ȡ/�����Ƿ�������ҳ
	docked = property( lambda self : self.__docked )					# bool: ��ȡ�Ƿ���ͣ��������״̬
	careCHIDs = property( _getCareCHIDs, _setCareCHIDs )				# set: ��ȡ/����ҳ���ע����ϢƵ��

	pos = property( _getPos, _setPos )									# Vector2: λ��


# --------------------------------------------------------------------
# �ۺϷ�ҳ
# --------------------------------------------------------------------
class GatherPage( MSGPage ) :
	def __init__( self, pyBinder) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = labelGather.getText( "ChatWindow:MSGReceiver", "tpGather" )
		self.deletable_ = False					# ���ɱ�ɾ��
		self.unlockable_ = True					# ���ɱ�����
		self.defCareCHIDs_ = set( [ \
			csdefine.CHAT_CHANNEL_NEAR,			# ����,
			csdefine.CHAT_CHANNEL_LOCAL,		# ����,
			csdefine.CHAT_CHANNEL_TEAM,			# ����,
			csdefine.CHAT_CHANNEL_TONG,			# ���,
			csdefine.CHAT_CHANNEL_WHISPER,		# ����,
			csdefine.CHAT_CHANNEL_WORLD,		# ����,
			csdefine.CHAT_CHANNEL_RUMOR,		# ҥ��,
			csdefine.CHAT_CHANNEL_WELKIN_YELL,	# ����
			csdefine.CHAT_CHANNEL_TUNNEL_YELL,	# ����

			# GM/����Ƶ��
			csdefine.CHAT_CHANNEL_SYSBROADCAST,	# �㲥,

			# NPC ����Ƶ��
			csdefine.CHAT_CHANNEL_NPC_SPEAK,	# NPC,

			# ϵͳ��ʾƵ��
			csdefine.CHAT_CHANNEL_SYSTEM,		# ϵͳ,
			csdefine.CHAT_CHANNEL_MESSAGE,		# ��Ϣ
			csdefine.CHAT_CHANNEL_CAMP,			# ��Ӫ
			] )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_CHAT_RECEIVE_ROLE_INFO"] = self.__onReceiveRoleInfo
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __onReceiveRoleInfo( self, msg ) :
		"""
		���ս�ɫ��Ϣ
		"""
		color = ( 255, 255, 255 )
		self.pyMSGPanel_.addCommonMessage( msg, color )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def dock( self, index ) :
		"""
		����ͣ������
		"""
		pass

	def undock( self, pos ) :
		"""
		���γ���ͣ������
		"""
		pass


# --------------------------------------------------------------------
# ���˷�ҳ
# --------------------------------------------------------------------
class PersonalPage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_PERSONAL]
		self.deletable_ = False					# ���ɱ�ɾ��
		self.defCareCHIDs_ = set( [
			csdefine.CHAT_CHANNEL_TEAM,			# ����,
			csdefine.CHAT_CHANNEL_TONG,			# ���,
			csdefine.CHAT_CHANNEL_PERSONAL,		# ����,
			csdefine.CHAT_CHANNEL_WHISPER,		# ����,
			] )


# --------------------------------------------------------------------
# ս����ҳ
# --------------------------------------------------------------------
class CombatPage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_COMBAT]
		self.deletable_ = False				# ���ɱ�ɾ��
		self.defCareCHIDs_ = set( [csdefine.CHAT_CHANNEL_COMBAT] )		# ս��,

# --------------------------------------------------------------------
# ����ҳ
# --------------------------------------------------------------------
class TongPage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG]
		self.deletable_ = False											# ���ɱ�ɾ��
		self.defCareCHIDs_ = set( [csdefine.CHAT_CHANNEL_TONG] )		# ���,
		

# --------------------------------------------------------------------
# ��ս��ҳ
# --------------------------------------------------------------------
class TongBattlePage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG_CITY_WAR]
		self.deletable_ = False											# ���ɱ�ɾ��
		self.defCareCHIDs_ = set( [csdefine.CHAT_CHANNEL_TONG_CITY_WAR] )		# ���,



# --------------------------------------------------------------------
# ��ҳ���ڣ������ҳ���ϳ����󽫻�ŵ���ҳ������
# --------------------------------------------------------------------
class PageWindow( RootGUI ) :
	__cc_tab_left			= 4						# ��ҳ��ť�����
	__cc_width_range		= ( 300, 700 )
	__cc_height_range		= ( 120, 600 )

	def __init__( self, pyPage, pos ) :
		wnd = GUI.load( "guis/general/chatwindow/mainwnd/pagefiller.gui" )
		RootGUI.__init__( self, wnd )
		self.focus = False
		self.movable_ = False						# ��ʾ�����Ƿ�����ƶ�
		self.activable_ = False						# ��ʾ�����Ƿ�ɱ�����
		self.escHide_ = False						# �� esc ���Ƿ������
		pyPage.pyBtn.left = self.__cc_tab_left

		self.pyPage_ = pyPage
		self.addPyChild( pyPage )
		self.addToMgr()
		self.__initResizers( wnd )

		pyPage.pos = 0, 0
		self.pos = pos
		self.size = pyPage.size
		pyPage.h_dockStyle = "HFILL"
		pyPage.v_dockStyle = "VFILL"
		self.show()

	def __del__( self ) :
		RootGUI.__del__( self )
		if Debug.output_del_ChatMSGPage :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		self.pyPage_ = None
		RootGUI.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initResizers( self, wnd ) :
		"""
		��ʼ����С������
		"""
		boards = { "r" : wnd.resizeHit_r, "t" : wnd.resizeHit_t, \
			"rt" : wnd.resizeHit_rt, "b" : wnd.resizeHit_b, "rb" : wnd.resizeHit_rb }
		self.__pyWndResizer = WndResizer( self, boards )
		self.__pyWndResizer.setWidthRange( self.__cc_width_range )
		self.__pyWndResizer.setHeightRange( self.__cc_height_range )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		if self.pyPage_.pyBtn.isMouseHit() :
			return True
		if self.__pyWndResizer.isMouseHit() :
			return True
		return False
