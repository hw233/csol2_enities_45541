# -*- coding: gb18030 -*-
#
# $Id: TipWindow.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

"""
implement tips window for operation help

-- 2010/04/15 : writen by huangyongwei
"""

import random
import weakref
from cscustom import Rect
from Function import Functor
from Helper import uiopHelper
from AbstractTemplates import Singleton
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.common.Window import Window
from guis.tooluis.CSRichText import CSRichText
from TipsArea import TipsArea

"""
��ʽ
1 :						2 :						3 :						4 :
						 |\						 		/|
--������������			������������			������������			������������--
 \��        ��			��        ��			��        ��			��        ��/
  ��        ��			��        ��			��        ��			��        ��
  ��        ��			��        ��			��        ��			��        ��
  ������������			������������			������������			������������

5 :						6 :						7 :						8 :
  ������������			������������			������������			������������
  ��        ��			��        ��			��        ��			��        ��
  ��        ��			��        ��			��        ��			��        ��
  ��        ��\			��        ��			��        ��		   /��        ��
  ������������--		������������			������������		  --������������
								 \|				 |/
"""
# --------------------------------------------------------------------
# ȫ�ֶ���
# --------------------------------------------------------------------
# ������ʽ����
STYLE_LT = 1
STYLE_TL = 2
STYLE_TR = 3
STYLE_RT = 4
STYLE_RB = 5
STYLE_BR = 6
STYLE_BL = 7
STYLE_LB = 8

# -------------------------------------------
_wndPath = "guis/tooluis/infotip/ophelper/wnd.gui"


# --------------------------------------------------------------------
# ��ʾ���ڵĲ�����Ϣ
# --------------------------------------------------------------------
class FormerInfo( object ) :
	bgSiteX = 0.0								# ��ʾ�ı��������ָ���λ��
	bgSiteY = 0.0

	cpBound = ( 0, 0, 0, 0 )					# clipPanel ��� bg ��λ��
	ptmappings = {}								# ������ʽ��ָ��� mapping
	ptSizes = {}								# ������ʽ��ָ��Ĵ�С
	ptPlaces = {}								# ������ʽ��ָ���ռλ��С

	@staticmethod
	def rebuildFormerInfo() :
		"""
		���¹������崰����Ϣ
		"""
		wnd = hfUILoader.load( _wndPath )											# ��ʾ����
		pointer = wnd.elements["pointer"]											# ָ��
		bg = wnd.elements["bg"]
		clipPanel = wnd.clipPanel
		ptmapping = pointer.mapping
		bgSiteX = bg.position.x														# ��ʾ�ı��������ָ���λ��
		bgSiteY = bg.position.y
		cpBound = (
			s_util.getGuiLeft( clipPanel ) - bgSiteX,								# clipPanel ��� bg �����
			s_util.getGuiTop( clipPanel ) - bgSiteY,								# clipPanel ��� bg ���Ҿ�
			bg.size.x - clipPanel.width,
			bg.size.y - clipPanel.height,
			)

		ptmappings = {																# ������ʽ��ָ��� mapping
			STYLE_LT : ptmapping,
			STYLE_TL : util.hflipMapping( util.cwRotateMapping90( ptmapping ) ),
			STYLE_TR : util.cwRotateMapping90( ptmapping ),
			STYLE_RT : util.hflipMapping( ptmapping ),
			STYLE_RB : util.cwRotateMapping180( ptmapping ),
			STYLE_BR : util.hflipMapping( util.ccwRotateMapping90( ptmapping ) ),
			STYLE_BL : util.ccwRotateMapping90( ptmapping ),
			STYLE_LB : util.vflipMapping( ptmapping ),
			}
		ptSizes = {																	# ������ʽ��ָ��Ĵ�С
			STYLE_LT : pointer.size,
			STYLE_TL : ( pointer.size[1], pointer.size[0] ),
			STYLE_TR : ( pointer.size[1], pointer.size[0] ),
			STYLE_RT : pointer.size,
			STYLE_RB : pointer.size,
			STYLE_BR : ( pointer.size[1], pointer.size[0] ),
			STYLE_BL : ( pointer.size[1], pointer.size[0] ),
			STYLE_LB : pointer.size,
			}
		ptPlaces = {																# ������ʽ��ָ���ռλ��С
			STYLE_LT : ( bgSiteX, bgSiteY ),
			STYLE_TL : ( bgSiteY, bgSiteX ),
			STYLE_TR : ( bgSiteY, bgSiteX ),
			STYLE_RT : ( bgSiteX, bgSiteY ),
			STYLE_RB : ( bgSiteX, bgSiteY ),
			STYLE_BR : ( bgSiteY, bgSiteX ),
			STYLE_BL : ( bgSiteY, bgSiteX ),
			STYLE_LB : ( bgSiteX, bgSiteY ),
			}

		FormerInfo.bgSiteX = bgSiteX
		FormerInfo.bgSiteY = bgSiteY

		FormerInfo.cpBound = cpBound
		FormerInfo.ptmappings = ptmappings
		FormerInfo.ptSizes = ptSizes
		FormerInfo.ptPlaces = ptPlaces

	@classmethod
	def onEvent( SELF, eventName, oldRso ) :
		SELF.rebuildFormerInfo()

FormerInfo.rebuildFormerInfo()
ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", FormerInfo )


# --------------------------------------------------------------------
# ��ʾ����
# --------------------------------------------------------------------
class OperationTip( Window ) :
	__cg_pyWnds = {}

	def __init__( self ) :
		wnd = hfUILoader.load( _wndPath )
		Window.__init__( self, wnd )
		self.addToMgr()
		self.posZSegment = ZSegs.L5
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False

		self.__mapID = -1
		self.pyRich_ = CSRichText( wnd.clipPanel )
		self.pyRich_.autoNewline = False
		self.pyRich_.widthAdapt = True
		self.pyTipsArea_ = None
		self.pyIcon_ = None

		self.__pyBinder = None
		self.__style = None					# ������ʽ
		self.__vsDetectCBID = 0

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def dispose( self ) :
		BigWorld.cancelCallback( self.__vsDetectCBID )
		if self.__mapID in self.__cg_pyWnds :
			self.__cg_pyWnds.pop( self.__mapID )
		self.pyTipsArea_.dispose()
		uiopTipsMgr.onTipsHide( self.__mapID )
		Window.dispose( self )

	def __del__( self ) :
		if Debug.output_del_OperationTip :
			INFO_MSG( str( self ) )
		self.pyTipsArea_.dispose()
		Window.__del__( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __calcStyle( location ) :
		"""
		�����������򣬼���Ӧ��ʹ�õ���ʾ����ʽ
		"""
		x, y = location
		scw, sch = BigWorld.screenSize()
		hscw, hsch = scw * 0.5, sch * 0.5
		if x < hscw :
			if y < hsch :
				return random.choice( ( STYLE_LT, STYLE_TL ) )
			else :
				return random.choice( ( STYLE_LB, STYLE_BL ) )
		else :
			if y < hsch :
				return random.choice( ( STYLE_TR, STYLE_RT ) )
			else :
				return random.choice( ( STYLE_RB, STYLE_BR ) )

	@staticmethod
	def __createWindow( text, style, location, bound, pyIcon ) :
		"""
		����������ʽ�Ĵ���
		"""
		pyWnd = OperationTip()										# ����һ����ʾ����
		pyWnd.__style = style
		pyWnd.pyRich_.text = text
		pyWnd.pyTipsArea_ = TipsArea( location, bound )

		wnd = pyWnd.gui
		pointer = wnd.elements["pointer"]							# ָʾ��
		bg = wnd.elements["bg"]

		pointer.mapping = FormerInfo.ptmappings[style]				# ����ָ������
		pointer.size = FormerInfo.ptSizes[style]

		bgWidth = pyWnd.pyRich_.width + FormerInfo.cpBound[2]
		bgHeight = pyWnd.pyRich_.height + FormerInfo.cpBound[3]
		if pyIcon :
			pyWnd.pyIcon_ = pyIcon
			pyWnd.addPyChild( pyIcon, "icon" )						# ����ͼ��
			bgWidth += ( pyIcon.width - pyWnd.pyCloseBtn_.width )
		bg.size = bgWidth, bgHeight									# ���õװ�����

		if style == STYLE_LT :										# 1
			pointer.position = 0, 0, 1
			bg.position.x = FormerInfo.bgSiteX
			bg.position.y = FormerInfo.bgSiteY
			wnd.width = s_util.getFElemRight( bg )
			wnd.height = s_util.getFElemBottom( bg )
		elif style == STYLE_TL :									# 2
			pointer.position = 0, 0, 1
			bg.position.x = FormerInfo.bgSiteY
			bg.position.y = FormerInfo.bgSiteX
			wnd.width = s_util.getFElemRight( bg )
			wnd.height = s_util.getFElemBottom( bg )
		elif style == STYLE_TR :									# 3
			pointer.position.y = 0
			bg.position.y = FormerInfo.bgSiteX
			wnd.height = s_util.getFElemBottom( bg )
			bg.position.x = 0
			wnd.width = bg.size.x + FormerInfo.bgSiteY
			pointer.position.x = wnd.width - pointer.size.x
		elif style == STYLE_RT :									# 4
			pointer.position.y = 0
			bg.position.y = FormerInfo.bgSiteY
			wnd.height = s_util.getFElemBottom( bg )
			bg.position.x = 0
			pointer.position.x = bg.size.x
			wnd.width = s_util.getFElemRight( pointer )
		elif style == STYLE_RB :									# 5
			bg.position = 0, 0, 1
			pointer.position.x = bg.size.x
			wnd.width = s_util.getFElemRight( pointer )
			wnd.height = bg.size.y + FormerInfo.bgSiteY
			pointer.position.y = wnd.height - pointer.size.y
		elif style == STYLE_BR :									# 6
			bg.position = 0, 0, 1
			pointer.position.y = s_util.getFElemBottom( bg )
			wnd.height = s_util.getFElemBottom( pointer )
			wnd.width = bg.size.x + FormerInfo.bgSiteY
			pointer.position.x = wnd.width - pointer.size.x
		elif style == STYLE_BL :									# 7
			pointer.position.x = 0
			bg.position.x = FormerInfo.bgSiteY
			wnd.width = s_util.getFElemRight( bg )
			bg.position.y = 0
			pointer.position.y = bg.size.y
			wnd.height = s_util.getFElemBottom( pointer )
		else :														# 8
			pointer.position.x = 0
			bg.position.x = FormerInfo.bgSiteX
			wnd.width = s_util.getFElemRight( bg )
			bg.position.y = 0
			wnd.height = s_util.getFElemBottom( bg ) + FormerInfo.bgSiteY
			pointer.position.y = wnd.height - pointer.size.y
		pyWnd.pyCloseBtn_.right = s_util.getFElemRight( bg )
		pyWnd.pyCloseBtn_.top = bg.position.y
		pyWnd.pyRich_.left = bg.position.x + FormerInfo.cpBound[0]
		pyWnd.pyRich_.top = bg.position.y + FormerInfo.cpBound[1]
		if pyIcon :
			pyIcon.left = pyWnd.pyRich_.right
			pyIcon.top = pyWnd.pyCloseBtn_.bottom + 10
			bottom = pyIcon.bottom
			if wnd.height < bottom :
				wnd.height = bottom
		return pyWnd

	# -------------------------------------------------
	def __relocate( self, location ) :
		"""
		���㴰��λ��
		"""
		self.pyTipsArea_.relocate( location )

		pointIn = 0.25
		style = self.__style
		bound = self.pyTipsArea_.bound
		x, y = location
		x += bound.minX
		y += bound.minY
		if style == STYLE_LT :							# 1
			x += bound.width - FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.pos = x, y
		elif style == STYLE_TL :						# 2
			x += bound.width * 0.5
			y += bound.height - FormerInfo.bgSiteX * pointIn
			self.pos = x, y
		elif style == STYLE_TR :						# 3
			x += bound.width * 0.5
			y += bound.height - FormerInfo.bgSiteX * pointIn
			self.right = x
			self.top = y
		elif style == STYLE_RT :						# 4
			x += FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.right = x
			self.top = y
		elif style == STYLE_RB :						# 5
			x += FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.right = x
			self.bottom = y
		elif style == STYLE_BR :						# 6
			x += bound.width * 0.5
			y += FormerInfo.bgSiteX * pointIn
			self.right = x
			self.bottom = y
		elif style == STYLE_BL :						# 7
			x += bound.width * 0.5
			y += FormerInfo.bgSiteX * pointIn
			self.left = x
			self.bottom = y
		else :											# 8
			x += bound.width - FormerInfo.bgSiteX * pointIn
			y += bound.height * 0.5
			self.left = x
			self.bottom = y

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


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, tipid, pyBinder, unshowFrame ) :
		if pyBinder :
			self.__pyBinder = weakref.ref( pyBinder )
			BigWorld.callback( 1.0, self.__visibleDetect )
		self.__mapID = tipid
		self.__cg_pyWnds[tipid] = self
		if not unshowFrame :
			self.pyTipsArea_.show( pyBinder )
		Window.show( self, pyBinder )

	def hide( self ) :
		Window.hide( self )
		self.dispose()

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
		if tipid in SELF.__cg_pyWnds : return
		tipsInfo = uiopHelper.getTips( tipid )
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

		style = tipsInfo.style												# ������ʽ
		if style == 0 :
			style = SELF.__calcStyle( location )							# ���������û��ָ��������ʽ��������Զ�ѡ�񴰿���ʽ

		pyIcon = None
		if tipsInfo.icon != "" :											# ����ұߴ���һ��ָʾͼ��
			try :
				icon = GUI.load( "maps/ophelp_icons/%s" % tipsInfo.icon )
				pyIcon = PyGUI( icon )
			except ValueError, err :
				ERROR_MSG( err )

		text = tipsInfo.text
		pyWnd = SELF.__createWindow( text, style, location, bound, pyIcon )	# ������ʽ�������ڷ��
		pyWnd.__relocate( location )										# ���ݺ�ɫ�߿�
		pyWnd.show( tipid, pyBinder, tipsInfo.unframe )
		return True

	@classmethod
	def hideTips( SELF, tipid ) :
		"""
		������ʾ����
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		"""
		pyWnd = SELF.__cg_pyWnds.get( tipid, None )
		if pyWnd :
			pyWnd.hide()

	@classmethod
	def moveTips( SELF, tipid, location = None ) :
		"""
		�ƶ���ʾ����
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		@type			location : tuple
		@param			location : ָʾ����λ�ã����Ϊ None������ PyBinder �����Ͻ�Ϊָʾ����λ��
		"""
		pyWnd = SELF.__cg_pyWnds.get( tipid, None )
		if not pyWnd : return
		if location is None :
			pyBinder = pyWnd.__pyBinder
			if pyBinder and pyBinder() :
				location = pyBinder().posToScreen
			else :
				raise TypeError( "argument location must be a tuple or Vector2!" )
		pyWnd.__relocate( location )


class UIOpTipsMgr( Singleton ) :
	"""Implement ui operation tips rule, such as max amount
	showed at one time��priority, etc"""
	__cc_GROUP_ROOT = 0													# Ĭ�ϵķ��飨��ӵ���Ļ��UI��
	__cc_MAX_SHOW_TIPS = 3												# �����ʾ����
	__cc_TIPS_HOLD_TIME = 10											# ������ʾʱ��

	def __init__( self ) :
		"""
		"""
		self.__tips2Group = {}											# ������ʾ�Ľű�UIʵ��
		self.__tipsQueue = {}											# ��ʾ�ȴ���ʾ����
		self.__visibleTips = set()										# ������ʾ����ʾ

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __isTipsFull( self ) :
		"""�жϵ�ǰ��ʾ����ʾ�Ƿ��Ѿ��ﵽ����"""
		return len( self.__visibleTips ) >= UIOpTipsMgr.__cc_MAX_SHOW_TIPS

	def __enterQueue( self, tipid, args ) :
		"""������еȴ�"""
		pyBinder = args[0]
		groupKey = UIOpTipsMgr.__cc_GROUP_ROOT
		if pyBinder is not None :
			groupKey = id( pyBinder.pyTopParent )						# ���ո����������з���
		self.__tips2Group[tipid] = groupKey
		tipsGroup = self.__tipsQueue.get( groupKey )
		if tipsGroup is None :
			tipsGroup = []
			self.__tipsQueue[groupKey] = tipsGroup
		tipsGroup.append( ( tipid, args ) )

	def __showTips( self, tipid, args ) :
		"""��ʾ��ʾ"""
		if OperationTip.showTips( tipid, *args ) :
			pyBinder = args[0]
			groupKey = UIOpTipsMgr.__cc_GROUP_ROOT
			if pyBinder is not None :
				groupKey = id( pyBinder.pyTopParent )
			self.__visibleTips.add( tipid )								# ��¼����ʾ���ڵķ���
			self.__tips2Group[ tipid ] = groupKey						# ��¼����ʾ���ڵķ���
			hideFunc = Functor( self.hideTips, tipid )
			BigWorld.callback( UIOpTipsMgr.__cc_TIPS_HOLD_TIME, hideFunc )
		else :
			DEBUG_MSG( "------->>> Tips shows false! %s %s" % ( tipid, args ) )
			self.__showNextTips( self.__popTips( tipid ) )

	def __showNextTips( self, groupKey = None ) :
		"""���ݹرյ���ʾ���ҵ���һ����Ҫ��ʾ����ʾ"""
		if self.__isTipsFull() :
			return
		tipsGroup = self.__tipsQueue.get( groupKey )
		if not tipsGroup :
			for tipsGroup in self.__tipsQueue.itervalues() :
				if len( tipsGroup ) > 0 : break
			else :
				return													# ������ʾ�Ѿ���ʾ��
		tipid, args = tipsGroup.pop( 0 )
		del self.__tips2Group[tipid]									# �Ӽ�¼��ɾȥ�Ա�������ʾ
		self.showTips( tipid, *args )

	def __popTips( self, tipid ) :
		"""�Ƴ���tipid������"""
		groupKey = self.__tips2Group.pop( tipid, None )					# ɾ�����Ѿ���ʾ������ʾ
		if groupKey is None :
			return														# û����صļ�¼
		tipsGroup = self.__tipsQueue.get( groupKey )
		if tipsGroup is None :
			return
		for tip in tipsGroup :											# �Ӷ�����ɾ��
			if tip[0] == tipid :
				tipsGroup.remove( tip )
		if len( tipsGroup ) == 0 :
			del self.__tipsQueue[groupKey]
		return groupKey

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showTips( self, tipid, *args ) :
		"""֪ͨ��ʾһ����ʾ"""
		if tipid in self.__tips2Group :
			return False
		if not uiopHelper.hasTips( tipid ) : return False
		if self.__isTipsFull() :
			self.__enterQueue( tipid, args )
		else :
			self.__showTips( tipid, args )
		return True

	def hideTips( self, tipid ) :
		"""֪ͨ�ر�һ����ʾ"""
		if tipid in self.__visibleTips :								# ����ʾ��ǰ������ʾ
			OperationTip.hideTips( tipid )
		else :
			self.__showNextTips( self.__popTips( tipid ) )

	def moveTips( self, tipid, location = None ) :
		"""֪ͨ�ƶ�һ����ʾ"""
		if tipid in self.__visibleTips :								# �������ʾ��ǰ������ʾ
			OperationTip.moveTips( tipid, location )					# ��֪ͨλ�õ���

	def onTipsHide( self, tipid ) :
		"""ĳ����ʾ�ɹ��رպ��֪ͨ"""
		if tipid in self.__visibleTips :
			self.__visibleTips.remove( tipid )
		else :
			DEBUG_MSG( "-------->>> Tip %i is unvisible, but it hide." % tipid )
		self.__showNextTips( self.__popTips( tipid ) )

	def clear( self ) :
		"""�����������"""
		self.__tipsQueue.clear()
		self.__tips2Group.clear()
		self.__visibleTips.clear()


uiopTipsMgr = UIOpTipsMgr()
