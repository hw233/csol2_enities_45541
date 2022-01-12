# -*- coding: gb18030 -*-
#
# $Id: InfoTip.py,v 1.2 2008-08-21 09:11:16 huangyongwei Exp $

"""
implement information tip window

-- 2008/08/19 : writen by huangyongwei
"""

import weakref
import csol
from guis import *
from guis.ScreenViewer import ScreenViewer
from guis.tooluis.infotip.ToolTip import ToolTip
from guis.tooluis.infotip.ItemTip import ItemTip
from guis.tooluis.infotip.OperationTip import uiopTipsMgr
from guis.tooluis.infotip.ItemTip import Grid
from guis.tooluis.helptips.HelpTip import helpTipsMgr

class InfoTip( object ) :
	__cg_pyTipWnds = {}
	__cg_pyTipWnds[ItemTip]		= set()			# ��Ʒ��ʾ����
	__cg_pyTipWnds[ToolTip]		= set()			# ������ʾ����

	__cc_delayShowTime			= 0.1			# ��ʱ�೤ʱ����ʾ

	def __init__( self ) :
		self.__pyBinder = None					# �󶨵Ŀؼ�
		self.__pyMainWnd = None					# ������
		self.__pyAssistWnds = []				# ��������
		self.__vsDetectCBID = 0					# ���󶨿ؼ��ɼ��Ե� callback ID
		self.__delayShowCBID = 0				# ��ʱ��ʾ�� callback ID

		self.__itemTpls = ()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getTipWindow( self, WndCls ) :
		"""
		����ģ�����Ӷ����������һ�� tipwindow �� tooltip
		"""
		if len( self.__cg_pyTipWnds[WndCls] ) :				# ���������л��ж���
			return self.__cg_pyTipWnds[WndCls].pop()		# ��Ӷ�����е���һ��
		return WndCls()										# �������´���һ��

	def __reclaimWnds( self ) :
		"""
		������ʾ����
		"""
		if self.__pyMainWnd :
			self.__pyMainWnd.hide()
			self.__cg_pyTipWnds[self.__pyMainWnd.__class__].add( self.__pyMainWnd )
			ScreenViewer().removeResistHiddenRoot(self.__pyMainWnd)
		for pyWnd in self.__pyAssistWnds :
			pyWnd.hide()
			self.__cg_pyTipWnds[pyWnd.__class__].add( pyWnd )
		self.__pyAssistWnds = []
		self.__pyBinder = None

	# -------------------------------------------------
	def __locateToolTips( self ) :
		"""
		���ù�����ʾ��λ��
		"""
		pyWnd = self.__pyMainWnd
		sw, sh = BigWorld.screenSize()					# ��Ļ��С
		x, y = rds.ccursor.pos							# ���ָ��λ��
		dx, dy = rds.ccursor.dpos						# ������½�λ��
		dx = min( dx, sw )
		if pyWnd.width <= sw - dx :
			if pyWnd.height < sh - dy :					# ���½��ܷ�����ʾ����
				pyWnd.pos = dx, dy						# �򽫴��ڷŵ�����ұ�
			else :										# ���Ͻ��ܷ�����ʾ����
				pyWnd.left = x
				pyWnd.bottom = y
		else :
			if pyWnd.height < sh - dy :					# ���½��ܷ�����ʾ����
				pyWnd.right = dx
				pyWnd.top = dy
			else :										# ֻ�ܷ����Ͻ�
				pyWnd.right = x
				pyWnd.bottom = y

	# -------------------------------------------------
	def __locateESignTips( self ) :
		"""
		����ʵ������ʾ��λ��
		"""
		pyWnd = self.__pyMainWnd
		sw, sh = BigWorld.screenSize()					# ��Ļ��С
		x, y = rds.ccursor.pos							# ���ָ��λ��
		dx, dy = rds.ccursor.dpos						# ������½�λ��
		dx = min( dx, sw )
		if pyWnd.height <= sh - dy :					# ��������ܷŵ��������
			pyWnd.top = dy
			if dx < pyWnd.width / 2 :					# ������ڶ������
				pyWnd.left = 0
			elif sw - dx < pyWnd.width / 2 :			# ������ڶ����ұ�
				pyWnd.right = sw
			else :
				pyWnd.center = dx						# ���򣬴����м����������
		else :											# ������ڲ��ܷŵ��������
			pyWnd.bottom = y							# ����ŵ��������
			if dx < pyWnd.width / 2 :
				pyWnd.left = 0
			elif sw - dx < pyWnd.width / 2 :
				pyWnd.right = sw
			else :
				pyWnd.center = x						# �����м����������

	# -------------------------------------------------
	def __generateItemTips( self, tips ) :
		"""
		����һ����Ʒ��ʾ����
		"""
		pyWnd = self.__getTipWindow( ItemTip )				# ��ȡһ����Ʒ��ʾ����
		pyWnd.clear()
		pyWnd.setItemInfo( tips )
		return pyWnd

	def __locateItemTips( self, pyBinder ) :
		"""
		����������Ʒ��ʾ����
		"""
		width, height = self.size							# ���д��ڵĿ�Ⱥͣ���ߴ��ڵĸ߶�
		sw, sh = BigWorld.screenSize()						# ��Ļ��С
		x, y = rds.ccursor.pos								# ���ָ��λ��
		dx, dy = rds.ccursor.dpos							# ������½�λ��
		dx = max( 0, min( dx, sw ) )
		if height <= sh - dy or y < height :				# �����������ܷ���������ʾ���ڣ������������Ų���������ʾ����
			top = self.__pyMainWnd.top = min( dy, sh - height )
			if width <= sw - dx or width > dx :				# ���������ʾ�����������½���ʾ
				self.__pyMainWnd.left = min( dx, sw - width )
				left = self.__pyMainWnd.right
				for pyWnd in self.__pyAssistWnds :
					pyWnd.left = left
					pyWnd.top = top
					left = pyWnd.right
					pyWnd.show( pyBinder )
			else :											# ���ȫ����ʾ�����������½���ʾ
				self.__pyMainWnd.right = dx
				right = self.__pyMainWnd.left
				for pyWnd in self.__pyAssistWnds :
					pyWnd.right = right
					pyWnd.top = top
					right = pyWnd.left
					pyWnd.show( pyBinder )
		else :												# ������ʾ����ֻ�������������ʾ
			bottom = self.__pyMainWnd.bottom = y
			if width <= sw - dx or width > x :				# ���������ʾ���������Ͻ���ʾ
				self.__pyMainWnd.left = min( x, sw - width )
				left = self.__pyMainWnd.right
				for pyWnd in self.__pyAssistWnds :
					pyWnd.left = left
					pyWnd.bottom = bottom
					left = pyWnd.right
					pyWnd.show( pyBinder )
			else :											# ������ʾ����ֻ����������Ͻ���ʾ
				self.__pyMainWnd.right = x
				right = self.__pyMainWnd.left
				for pyWnd in self.__pyAssistWnds :
					pyWnd.right = right
					pyWnd.bottom = bottom
					right = pyWnd.left
					pyWnd.show( pyBinder )
		self.__pyMainWnd.show( pyBinder )

	def __visableDetect( self, pyBinder ) :
		"""
		�������Ƿ�ɼ���������ɼ���������������ʾ��
		"""
		if not pyBinder.visible :
			self.hide()
		else :
			BigWorld.cancelCallback( self.__vsDetectCBID )
			func = Functor( self.__visableDetect, pyBinder )
			self.__vsDetectCBID = BigWorld.callback( 0.5, func )
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showToolTips( self, pyBinder, text, resistHidden=False ) :
		"""
		��ʾ������ʾ
		@type				pyBinder : python UI
		@param				pyBinder : �� UI
		@type				text	 : str
		@param				text	 : ��ʾ����
		@type				resistHidden : bool
		@param				resistHidden : �Ƿ��������
		"""
		if text == "" : return
		self.__reclaimWnds()								# ���Ȼ������д���
		self.__pyBinder = weakref.ref( pyBinder )			# ��¼�󶨿ؼ�
		pyWnd = self.__getTipWindow( ToolTip )
		pyWnd.clear()
		pyWnd.setText( text )
		self.__pyMainWnd = pyWnd
		self.__locateToolTips()
		if resistHidden:
			ScreenViewer().addResistHiddenRoot(self.__pyMainWnd)
		pyWnd.show( pyBinder )

	# ---------------------------------------
	def showESignTips( self, pyBinder, text ) :
		"""
		��ʾ��/С��ͼ�� entity ����Ϣ
		"""
		if text == "" : return
		self.__reclaimWnds()								# ���Ȼ������д���
		self.__pyBinder = weakref.ref( pyBinder )			# ��¼�󶨿ؼ�
		pyWnd = self.__getTipWindow( ToolTip )
		pyWnd.clear()
		pyWnd.setText( text )
		self.__pyMainWnd = pyWnd
		self.__locateESignTips()
		pyWnd.show( pyBinder )

	# ---------------------------------------
	def getItemGrid( self, text, tpl ) :
		"""
		��ȡ��Ʒ��ʾ����ģ��
		@type				text : str
		@param				text : �����е��ı�
		@type				tpl	 : dict
		@param				tpl	 : ��ʽ���ֵ䣺
								   "align"		: �ı�ˮƽ���뷽ʽ��"L"��"C"��"R" �ֱ��ʾ�����Ҷ���
								   "lineFlat"	: �ı���ֱ���뷽ʽ��"T"��"M"��"B" �ֱ��ʾ�����¶���
								   "newline": �Ƿ��Զ�����
								   ȫ���ؼ��ֶ�Ϊ��ѡ��Ʃ����Խ������룺{ "maxWidth" : 100 }
		"""
		return Grid( text, tpl )

	def setItemTemplates( self, *tpls ) :
		"""
		������Ʒ��ʾ���ڵ�ģ��
		@type			tpls : tuple of dict
		@param			tpls : { "minWidth" : ��С���, "lMaxWith" : ����������, "rMaxWidth" : �ұ�������� }
		"""
		self.__itemTpls = tpls

	def showItemTips( self, pyBinder, *tips ) :
		"""
		��ʾ��Ʒ��ʾ
		@type				pyBinder : python UI
		@param				pyBinder : �� UI
		@type				tips	 : str / list
		@param				tips	 : ��ʾ���ݣ�����ͨ��������������ʵ�ֶ����ʾ��ÿ���ɱ������ʾһ����ʾ������ݣ�:
									   ����ǵ��е��ı���ʾ������ֱ�Ӵ��� str �磺
										   showItemTips( pyBinder, str1 )
									   ��gt1 = getItemGridTemplate( ���Ӹ�ʽ��ģ��, str1 )
										   showItemTips( pyBinder, gt1 )

									   ���Ҫ��ʾ�����ʾ������Դ�������ʾ����ı����ݣ��磺
										   showItemTips( pyBinder, str1, [str2, [str3, str4]] )
									   ��gt1 = getItemGridTemplate( ���Ӹ�ʽ��ģ��, str1 )
										   gt2 = getItemGridTemplate( ���Ӹ�ʽ��ģ��, str2 )
										   gt3 = getItemGridTemplate( ���Ӹ�ʽ��ģ��, str3 )
										   showItemTips( pyBinder, gt, [gt2, [gt3, str4]] ) ��������һ����ʾ���ǵ����ı���
										   �ڶ�����ʾ��Ϊ���������ı�:
										  ����������������������
										  ��    ����str2      ��
										  ��str1���������Щ�����
										  ��    ����str3��str4��
										  ���������������ة�����
									   Ҳ����д�ɣ�
										   showItemTips( pyBinder, [[str1]], [[str2], [str3, str4]] )
									   Ҳ����д�ɣ�
										   showItemTips( pyBinder, [[str1, ""]], [[str2, ""], [str3, str4]] )

									   ���Ҫ��ĳ�к�����һ���ָ��������������д��
										   showItemTips( pyBinder, [str1, [], str2] )
										   ��������������
										   ��   str1   ��---> ��Ȼ�ǵ�һ�У������� 0��
										   ��������������---> �ָ���
										   ��   str2   ��---> ��Ȼ�ǵڶ��У������� 1��
                                           ��������������
		"""
		def delayHandle() :
			self.__reclaimWnds()								# ���Ȼ������д���
			self.__pyBinder = weakref.ref( pyBinder )			# ��¼�󶨿ؼ�
			pyWnds = []
			for idx, tip in enumerate( tips ) :					# ѭ������ÿ����ʾ������
				pyWnd = self.__generateItemTips( tip )			# ����һ����ʾ��
				if idx < len( self.__itemTpls ) :				# �Ƿ���ģ��
					pyWnd.setTemplate( self.__itemTpls[idx] )	# ����ģ��
				pyWnd.typeset()									# �Ű�����
				pyWnds.append( pyWnd )							# ����ʾ��ŵ���ǰ��ʾ�б���
			if len( pyWnds ) :
				self.__pyMainWnd = pyWnds[0]
				self.__pyAssistWnds = pyWnds[1:]
				self.__locateItemTips( pyBinder )				# �������д���λ��
				self.__itemTpls = ()							# ���ģ��

		BigWorld.cancelCallback( self.__delayShowCBID )
		self.__delayShowCBID = BigWorld.callback( self.__cc_delayShowTime, delayHandle )
		self.__visableDetect( pyBinder )

	# -------------------------------------------------
	def hide( self, pyBinder = None ) :
		"""
		����������ʾ����
		"""
		BigWorld.cancelCallback( self.__delayShowCBID )
		if self.__pyMainWnd is None : return
		if pyBinder is None or self.pyBinder == pyBinder :
			BigWorld.cancelCallback( self.__vsDetectCBID )
			self.__vsDetectCBID = 0
			self.__reclaimWnds()

	# -------------------------------------------------
	def showOperationTips( self, tipid, pyBinder = None, bound = None ) :
		"""
		��ʾ������ʾ
		ע�⣺����ʾ��������꣬���ҿ���ͬʱ��ʾ���
		@type			tipid	 : INT16
		@param			tipid	 : �����е���ʾ ID
		@type			pyBinder : instance of GUIBaseObject
		@param			pyBinder : Ҫ��ʾ�Ŀؼ���
									�����Ϊ None�����ɫ�߿��λ����� pyBinder ��λ��
									���Ϊ None�����ɫ�߿��λ�������Ļ��λ��
		@type			bound	 : cscustom::Rect
		@param			bound	 : Ȧ�����ĺ�ɫָʾ�߿����Ϊ None����ʹ��������ָ��������
		"""
		return uiopTipsMgr.showTips( tipid, pyBinder, bound )

	def hideOperationTips( self, tipid ) :
		"""
		���ز�����ʾ
		@type				tipid	 : INT16
		@param				tipid	 : Ҫ��ʾ�Ĳ��� id
		"""
		uiopTipsMgr.hideTips( tipid )

	def moveOperationTips( self, tipid, location = None ) :
		"""
		�ƶ�������ʾ��λ��
		@type				tipid	 : INT16
		@param				tipid	 : Ҫ��ʾ�Ĳ��� id
		@type				point	 : tuple
		@param				point	 : ��ʾ��ʾ��λ�ã������ʾ��λ��Ϊ None��������� pyBinder ��λ�ý����ƶ�
		"""
		uiopTipsMgr.moveTips( tipid, location )

	def showHelpTips( self, tipid, pyBinder = None, bound = None ):
		"""
		��ʾ������ʾ
		"""
		return helpTipsMgr.showTips( tipid, pyBinder, bound )

	def hideHelpTips( self, tipid ):
		"""
		���ذ�����ʾ
		"""
		helpTipsMgr.hideTips( tipid )

	def moveHelpTips( self, tipid, location = None ):
		"""
		�ƶ�������ʾ
		"""
		helpTipsMgr.moveTips( tipid, location )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# -------------------------------------------------
	def _getWidth( self ) :
		width = 0
		if self.__pyMainWnd :
			width = self.__pyMainWnd.width
		for pyWnd in self.__pyAssistWnds :
			width += pyWnd.width
		return width

	def _getHeight( self ) :
		height = 0
		if self.__pyMainWnd :
			height = self.__pyMainWnd.height
		for pyWnd in self.__pyAssistWnds :
			height = max( pyWnd.height, height )
		return height

	def _getSize( self ) :
		width = height = 0
		if self.__pyMainWnd :
			width = self.__pyMainWnd.width
			height = self.__pyMainWnd.height
		for pyWnd in self.__pyAssistWnds :
			height = max( pyWnd.height, height )
			width += pyWnd.width
		return width, height


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )								# ��ǰ��ʾ�󶨵Ŀؼ�
	width = property( _getWidth )									# ������ʾ��Ŀ�Ⱥ�
	height = property( _getHeight )									# ������ʾ���У������ʾ��ĸ߶�
	size = property( _getSize )										# ( self.width, self.height )
