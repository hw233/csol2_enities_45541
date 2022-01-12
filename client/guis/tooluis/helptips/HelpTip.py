# -*- coding: gb18030 -*-
#
# $Id: HelpTip.py

from guis import *
import weakref
from guis.common.RootGUI import RootGUI
from guis.common.FrameEx import HVFrameEx
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.infotip.TipsArea import TipsArea
from cscustom import Rect
from ArrowTip import ArrowTip
from AbstractTemplates import Singleton
from HelpTipsSetting import helpTipsSetting

class HelpTip( RootGUI, HVFrameEx ):
	"""
	����ָʾ
	"""
	cc_edge_width_			= 10.0		# ��������صľ���
	__cc_min_width = 65.0				# ��С���
	__cg_pyHelpTips = {}

	def __init__( self ):
		tip = GUI.load( "guis/tooluis/helptips/helptip.gui" )
		uiFixer.firstLoadFix( tip )
		RootGUI.__init__( self, tip )
		HVFrameEx.__init__( self, tip )
		self.addToMgr()
		self.focus = False
		self.moveFocus = False
		self.escHide_ 		 = False
		self.posZSegment = ZSegs.L4
		pointer = tip.elements["pointer"]
		self.__prSitScale = float( pointer.position[0] )/ self.width

		self.pyRtMsg_ = CSRichText( tip.rtMsg )
		self.pyRtMsg_.maxWidth = 180.0
		self.pyRtMsg_.align = "L"
		self.pyRtMsg_.opGBLink = True
		self.pyRtMsg_.left = self.cc_edge_width_
		self.pyRtMsg_.top = self.cc_edge_width_

		self.__vsDetectCBID = 0
		self.__mapID = 0
		self.pyTipsArea_ = None

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def dispose( self ) :
		BigWorld.cancelCallback( self.__vsDetectCBID )
		if self.__mapID in self.__cg_pyHelpTips :
			self.__cg_pyHelpTips.pop( self.__mapID )
		self.pyTipsArea_.dispose()
		RootGUI.dispose( self )

	def __del__( self ) :
		self.pyTipsArea_.dispose()
		RootGUI.__del__( self )

	def __layout( self ) :
		"""
		���ô�����Ӧ�ı���С
		"""
		elements = self.gui.elements
		self.width = self.pyRtMsg_.right + self.cc_edge_width_#��0.6������ȥ��������ߵĺ����ģ���ʱֻ��������
		self.height = self.pyRtMsg_.bottom + elements["frm_b"].size[1]

	# -------------------------------------------------
	def __relocate( self, location ) :
		"""
		�����ͷλ��
		"""
		elements = self.gui.elements
		self.pyTipsArea_.relocate( location )
		bound = self.pyTipsArea_.bound
		x, y = location
		x += bound.minX
		y += bound.minY
		self.top = y + 15.0
		self.center = x #- elements["pointer"].size[0]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, tipid, msg, pyBinder, unshowFrame ) :
		self.pyRtMsg_.text = msg
		if len( msg ) <= 5:
			self.pyRtMsg_.center = self.__cc_min_width / 2.0
		if pyBinder :
			self.__pyBinder = weakref.ref( pyBinder )
			BigWorld.callback( 1.0, self.__visibleDetect )
		self.__mapID = tipid
		self.__cg_pyHelpTips[tipid] = self
		if not unshowFrame :
			self.pyTipsArea_.show( pyBinder )
		self.__layout()
		self.visible = True

	def hide( self ) :
		self.visible = False
		self.dispose()

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		width = max( self.__cc_min_width, width )
		HVFrameEx._setWidth( self, width )
		elements = self.gui.elements
		tl = elements["frm_tl"]
		tr = elements["frm_tr"]
		pointer = elements["pointer"]
		lt = elements["frm_lt"]
		rt = elements["frm_rt"]
		r = elements["frm_r"]
		pointer.position[0] = max( tl.position[0]+tl.size[0], width*self.__prSitScale )
		tl.size[0] = pointer.position[0] - ( lt.position[0] + lt.size[0] )
		tr.size[0] = rt.position[0] - ( pointer.position[0] + pointer.size[0] )
		tr.position[0] = rt.position[0] - tr.size[0]
		self.pyRtMsg_.left = self.cc_edge_width_

	def _setHeight( self, height ) :
		HVFrameEx._setHeight( self, height )
		elements = self.gui.elements
		t = elements["frm_t"]
		tl = elements["frm_tl"]
		tr = elements["frm_tr"]
		pointer = elements["pointer"]
		bottom = t.position[1] + t.size[1]
		tl.position[1] = bottom - tl.size[1]
		pointer.position[1] = bottom - pointer.size[1]
		tr.position[1] = bottom - tr.size[1]
		self.pyRtMsg_.top = tl.position[1] + self.cc_edge_width_

	def _getCenter( self ):
		offset = self.width*( 0.5 - self.__prSitScale )
		center = HVFrameEx._getCenter( self )
		return center - offset

	def _setCenter( self, center ):
		offset = self.width*( 0.5 - self.__prSitScale )
		HVFrameEx._setCenter( self, center + offset )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HVFrameEx._getWidth, _setWidth )
	height = property( HVFrameEx._getHeight, _setHeight )
	center = property( _getCenter, _setCenter )

	#-----------------------------------------------------------------
	# staticmethod
	# ----------------------------------------------------------------
	@staticmethod
	def __createHelpTip( location, bound ) :
		"""
		����������ʽ�Ĵ���
		"""
		pyHelpTip = HelpTip()										# ����һ����ʾ����
		pyHelpTip.pyTipsArea_ = TipsArea( location, bound )
		return pyHelpTip

	# -------------------------------------------------
	def __visibleDetect( self ) :
		if self.__pyBinder is None or \
			self.__pyBinder() is None or \
			not self.__pyBinder().rvisible :
				self.dispose()
		else :
			self.__vsDetectCBID = BigWorld.callback( 1.0, self.__visibleDetect )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventName, oldRso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		pyBinder = self.__pyBinder
		if pyBinder and pyBinder() :
			self.__relocate( pyBinder().posToScreen )

	# -------------------------------------------------
	@classmethod
	def showTips( SELF, tipid, pyBinder = None, bound = None ) :
		"""
		��ʾ�ı�
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		@type			pyBinder : instance of GUIBaseObject
		@param			pyBinder : Ҫ��ʾ�Ŀؼ���
									�����Ϊ None�����ɫ�߿��λ����� pyBinder ��λ��
									���Ϊ None�����ɫ�߿��λ�������Ļ��λ��
		@type			bound	 : cscustom::Rect
		@param			bound	 : Ȧ�����ĺ�ɫָʾ�߿����Ϊ None����ʹ��������ָ��������
		@rtype					 : bool
		@param					 : ��ʾ�ɹ����򷵻� True
		"""
		if tipid in SELF.__cg_pyHelpTips : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		if not tipsInfo : return False										# �����в����ڸ���ʾ ID
		location = 0, 0														# Ĭ�Ϻ�߿�λ�������Ļ
		if pyBinder :														# ����������ؼ�
			location = pyBinder.posToScreen									# ���߿�λ����������ؼ������Ͻ�
			if bound is None :												# ���û��ָ��ָʾ����
				bound = tipsInfo.bound										# ��ʹ�������е�ָʾ����
				if bound.width == 0 :										# ���������Ҳûָ��ָʾ����
					bound = Rect( ( 0, 0 ), pyBinder.size )					# ��ʹ�� pyBinder ����Ӿ�����Ϊָʾ����
		elif bound :														# û�������ؼ�
			location = bound.location										# ��λ�������Ļ
			bound.updateLocation( 0, 0 )
		else :
			raise TypeError( "one of argument 'pyBinder' and 'bound' must be not None!" )
		text = tipsInfo.text
		pyHelpTip = SELF.__createHelpTip( location, bound )	# ������ʽ�������ڷ��
		pyHelpTip.__relocate( location )										# ���ݺ�ɫ�߿�
		pyHelpTip.show( tipid, text, pyBinder, tipsInfo.unframe )
		return True

	@classmethod
	def hideTips( SELF, tipid ) :
		"""
		������ʾ����
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		"""
		pyHelpTip = SELF.__cg_pyHelpTips.get( tipid, None )
		if pyHelpTip :
			pyHelpTip.hide()

	@classmethod
	def moveTips( SELF, tipid, location = None ) :
		"""
		�ƶ���ʾ����
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		@type			location : tuple
		@param			location : ָʾ����λ�ã����Ϊ None������ PyBinder �����Ͻ�Ϊָʾ����λ��
		"""
		pyHelpTip = SELF.__cg_pyHelpTips.get( tipid, None )
		if not pyHelpTip : return
		if location is None :
			pyBinder = pyHelpTip.__pyBinder
			if pyBinder and pyBinder() :
				location = pyBinder().posToScreen
			else :
				raise TypeError( "argument location must be a tuple or Vector2!" )
		pyHelpTip.__relocate( location )

# -----------------------------------------------------------------------
class HelpTipsMgr( Singleton ):
	"""
	������ʾ������
	"""
	def __init__( self ):

		self.__helpTips = {}

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showTips( self, tipid, pyBinder, bound ) :
		"""
		֪ͨ��ʾһ����ʾ�������������Ǽ�ͷ��������ָʾ
		"""
		if not helpTipsSetting.hasTips( tipid ) : return False
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		style = tipsInfo.style
		if style == 0:
			ArrowTip.showTips( tipid, pyBinder, bound )
		else:
			HelpTip.showTips( tipid, pyBinder, bound )
		return True

	def hideTips( self, tipid ) :
		"""
		֪ͨ�ر�һ����ʾ
		"""
		if not helpTipsSetting.hasTips( tipid ) : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		style = tipsInfo.style
		if style == 0:
			ArrowTip.hideTips( tipid )
		else:
			HelpTip.hideTips( tipid )

	def moveTips( self, tipid, location = None ) :
		"""
		֪ͨ�ƶ�һ����ʾ
		"""
		if not helpTipsSetting.hasTips( tipid ) : return
		tipsInfo = helpTipsSetting.getTipInfo( tipid )
		style = tipsInfo.style
		if style == 0:
			ArrowTip.moveTips( tipid, location )					# ��֪ͨλ�õ���
		else:
			HelpTip.moveTips( tipid, location )

helpTipsMgr = HelpTipsMgr()
