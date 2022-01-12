# -*- coding: gb18030 -*-
#
# $Id: RootGUI.py,v 1.50 2008-08-26 02:12:34 huangyongwei Exp $

"""
the python gui in GUI.roots()
2005/07/18 : writen by huangyongwei
"""

import weakref
from guis import *
from ScriptObject import ScriptObject
from guis.controls.Button import Button

class RootGUI( ScriptObject ) :
	"""
	���� UI
	ע�⣺Ҫ�ͷ� Root ���ڣ�һ��Ҫ���ȵ��� dispose ����
	"""
	__cc_dock_edge		= 50

	def __init__( self, gui = None ) :
		ScriptObject.__init__( self, gui )
		self.__posZSegment = ZSegs.L4				# ���ڲ�Σ��� guis.uidefine.py �ж���
		self.movable_ = True						# ��ʾ�����Ƿ�����ƶ�
		self.activable_ = True						# ��ʾ�����Ƿ�ɱ�����
		self.hitable_ = True						# ���Ϊ False��������ڴ�����ʱ����Ȼ�ж������������Ļ
		self.escHide_ = True						# �� esc ���Ƿ������
		self.__initialize( gui )					# ��ʼ��
		self.h_dockStyle = "LEFT"					# ����Ļ�ϵ�ˮƽͣ����ʽ
		self.v_dockStyle = "MIDDLE"					# ����Ļ�ϵĴ�ֱͣ����ʽ

		# ----------------------------------------
		# private
		# ----------------------------------------
		self.__pyOwner = None						# �����ڣ�û�������õĸ�����Ϊ None
		self.__pySubDialogs = None					# �Ӵ����б�
		self.__pyOkBtn = None						# Ĭ�ϵ� ok ��ť�����س����ڵ���ð�ť��
		self.__pyCancelBtn = None					# Ĭ�ϵ� cancel ��ť���� esc �����ڰ��ð�ť��

		self.__mouseDownPos = ( 0, 0 )				# ��ʱ����������ڴ����ϰ���ʱ����¼

	def subclass( self, gui ) :
		"""
		������������ UI
		"""
		ScriptObject.subclass( self, gui )
		self.__initialize( gui )
		return self

	def __initialize( self, gui ) :
		if gui is None : return
		self.focus = True							# Ĭ�Ͻ������ͼ��̰�����Ϣ
		self.moveFocus = True						# Ĭ�Ͻ�������ƶ���Ϣ�����ڴ����ƶ����ڣ�
		gui.visible = False							# Ĭ�ϲ��ɼ�
		uiFixer.attach( self )						# ��ӵ� ui Ԫ��������������Ļ�ֱ��ʸı�ʱ�������� UI ��λ�ã����²����λ��

	def dispose( self ) :
		"""
		��������( ע�⣬Ҫɾ������ʱ��һ��Ҫ���ø÷��� )
		"""
		pyOwner = self.pyOwner
		if pyOwner :									# ������ڸ�����
			pyOwner.__removeSubDialog( self )			# ��Ӹ������б���������Լ�
			if rds.ruisMgr.isActRoot( self ) :			# �Ƿ��ǵ�ǰ����Ĵ���
				rds.ruisMgr.activeRoot( pyOwner )		# �������
		if self.__pySubDialogs is not None :
			for pySubDialog in self.__pySubDialogs :	# ֪ͨ�����Ӵ���
				pySubDialog.__onOwnerHide()				# ���Ѿ�����
			self.__pySubDialogs = None					# ����ҵ������Ӵ���
		self.removeFromMgr()							# �ӹ�������ȥ��
		uiFixer.detach( self )							# ����������ȥ��
		ScriptObject.dispose( self )

	def __del__( self ) :
		ScriptObject.__del__( self )
		if Debug.output_del_RootGUI :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		ScriptObject.generateEvents_( self )
		self.__onBeforeShow = self.createEvent_( "onBeforeShow" )			# ������ʾ֮ǰ������
		self.__onAfterShowed = self.createEvent_( "onAfterShowed" )			# ������ʾ֮�󱻴���
		self.__onBeforeClose = self.createEvent_( "onBeforeClose" )			# ��������֮ǰ������
		self.__onAfterClosed = self.createEvent_( "onAfterClosed" )			# ��������֮�󱻴���

	@property
	def onBeforeShow( self ) :
		"""
		������ʾ֮ǰ������
		"""
		return self.__onBeforeShow

	@property
	def onAfterShowed( self ) :
		"""
		������ʾ֮�󱻵���
		"""
		return self.__onAfterShowed

	@property
	def onBeforeClose( self ) :
		"""
		��������֮ǰ������
		"""
		return self.__onBeforeClose

	@property
	def onAfterClosed( self ) :
		"""
		��������֮�󱻵���
		"""
		return self.__onAfterClosed


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addSubDialog( self, pyDialog ) :
		"""
		���һ���Ӵ���
		"""
		if self.__pySubDialogs is None :
			self.__pySubDialogs = WeakList()
			self.__pySubDialogs.append( pyDialog )
		elif pyDialog not in self.__pySubDialogs :
			self.__pySubDialogs.append( pyDialog )

	def __removeSubDialog( self, pyDialog ) :
		"""
		ɾ��һ���Ӵ���
		"""
		if self.__pySubDialogs is None :
			return
		elif pyDialog in self.__pySubDialogs :
			self.__pySubDialogs.remove( pyDialog )
			if len( self.__pySubDialogs ) == 0 :
				self.__pySubDialogs = None

	def __onOwnerHide( self ) :
		"""
		�����ڵĸ���������ʱ������
		"""
		self.hide()												# ����������ʱ���Լ�Ҳ����
		self.__pyOwner = None									# ȡ���Ը����ڵ�����


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		if self.movable_ and self.isMouseHit() :				# ���������������ƶ�
			uiHandlerMgr.capUI( self )							# cap ���ڣ����ô������Ƚ���ϵͳ��Ϣ��
			self.__mouseDownPos = self.mousePos					# ��¼������������ϵ�����λ��
		return True

	def onLMouseUp_( self, mods ) :
		uiHandlerMgr.uncapUI( self )							# �������ʱ�ͷ� cap
		if rds.worldCamHandler.fixed() :
			rds.worldCamHandler.unfix()

	def onMouseMove_( self, dx, dy ) :
		if uiHandlerMgr.getCapUI() == self :					# ������ڵ�ǰ�� cap������ζ�Ŵ��ڽ����ƶ�
			mx, my = csol.pcursorPosition()						# ��ȡ�����Ļ�ϵ�����λ��
			wx, wy = self.posToScreen							# ��ȡ��������Ļ�ϵ�����λ��
			self.left = mx - self.__mouseDownPos[0]				# (ˮƽ���򴰿��Ƶ����λ�ã���������ƶ���ǰ��λ�ò�)
			self.top = my - self.__mouseDownPos[1]				#����ֱ���򴰿��Ƶ����λ�ã���������ƶ���ǰ��λ�ò�)
			self.onMove_( dx, dy )								# �����ƶ���Ϣ
			return True											# ������Ϣ
		return ScriptObject.onMouseMove_( self, dx, dy )

	def onKeyDown_( self, key, mods ) :
		if ruisMgr.getActRoot() != self : return False									# ֻ�д��ڴ��ڼ���״̬ʱ�Ž��� keydown ��Ϣ
		ScriptObject.onKeyDown_( self, key, mods )										# �ص� ScriptObject �� onKeyDown
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# ��������˻س���
			pyOkBtn = self.pyOkBtn														# ���ȡĬ�ϵ� ok ��ť
			if pyOkBtn is not None and pyOkBtn.rvisible and pyOkBtn.enable :			# ����ð�ť����
				pyOkBtn.onLClick()														# �򴥷���ť�ĵ���¼�
				return True																# ������Ϣ
		elif ( mods == 0 ) and ( key == KEY_ESCAPE ) :									# ��������� ESC ��
			pyCancelBtn = self.pyCancelBtn												# ���ȡĬ�ϵ�ȡ����ť
			if pyCancelBtn is not None and pyCancelBtn.enable and pyCancelBtn.rvisible :# ���ȡ����ť����
				pyCancelBtn.onLClick()													# �򴥷�ȡ����ť�ĵ����Ϣ
				return True																# ������Ϣ
		return False																	# ����Ϣ����

	# -------------------------------------------------
	def onMove_( self, dx, dy ) :
		"""
		�������ƶ�ʱ������
		"""
		pass

	def onClose_( self ) :
		"""
		�����ڹر�ǰ������
		ע�⣺����ͨ����д�ú��������ƴ��ڵĹرգ�������� False����ȡ���ر�
			  ����ͨ����д�ú������رմ���֮ǰ���ڸ÷�������һЩ�ر��жϣ��Ӷ���һ��������ȡ�����ڵĹر�
		"""
		return True


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onActivated( self ) :
		"""
		�����ڼ���ʱ������
		"""
		pass

	def onInactivated( self ) :
		"""
		������ȡ������ʱ״̬������
		"""
		pass

	# -------------------------------------------------
	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		����Ϸ״̬��Ҫ�ı�ʱ������
		@param					onStatus  : �ı�ǰ��״̬���� Define.py �ж��壩
		@param					newStatus : �ı���״̬���� Define.py �ж��壩
		"""
		pass

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		����Ϸ״̬�ı�ʱ������
		@param					onStatus  : �ı�ǰ��״̬���� Define.py �ж��壩
		@param					newStatus : �ı���״̬���� Define.py �ж��壩
		"""
		pass

	def onEnterWorld( self ) :
		"""
		����ɫ��ʼ����Ͻ�������ʱ������
		"""
		pass

	def onLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addToMgr( self, hookName = "" ) :
		"""
		��ӵ����ڹ�����
		"""
		rds.ruisMgr.add( self, hookName )

	def removeFromMgr( self ) :
		"""
		�Ӵ��ڹ�������ɾ��
		"""
		rds.ruisMgr.remove( self )

	# -------------------------------------------------
	def show( self, pyOwner = None, floatOwner = True ) :
		"""
		��ʾ����
		@type				pyOwner	   : GUIBaseObject
		@param				pyOwner	   : ���ڵĸ����ڻ�ؼ���ע������ǿؼ�����ᱻת��Ϊ�ؼ������Ĵ��ڣ�
		@type				floatOwner : bool
		@param				floatOwner : �Ƿ��޸� posZSegment���ô���Ư���� pyOwner �����棨pyOwner ��Ϊ None ʱ���������ã�
		"""
		if not self.rvisible :
			self.onBeforeShow()												# ���֮ǰʱ����״̬�ģ��򴥷���ʾ��Ϣ
		self.__pyOwner = None
		if pyOwner is not None :											# ����и����ڣ��򸸿ؼ���
			pyTopParent = pyOwner.pyTopParent								# ��ȡ�����ڵĶ��� UI
			assert pyTopParent != self										# �����ڲ������Լ�
			if isinstance( pyTopParent, RootGUI ) :							# �����ڣ��򸸿ؼ��Ķ��㴰�ڣ�����̳��� RootGUI
				self.__pyOwner = weakref.ref( pyOwner.pyTopParent )			# ��¼������
				if floatOwner :
					self.posZSegment = self.pyOwner.posZSegment				# ������������Ϊ�뱾����ͬ��
				self.pyOwner.__addSubDialog( self )							# ���ø�������ӱ�������Ϊ�����ڵ��Ӵ���
			else :															# ��������ڲ��Ǽ̳��� RootGUI
				ERROR_MSG( "class of '%s' must be inheired from RootGUI!" \
				% str( pyTopParent ) )										# �����������Ϣ

		from guis.ScreenViewer import ScreenViewer
		if not ScreenViewer().isEmptyScreen() or\
			ScreenViewer().isResistHiddenRoot(self):						# �������������ʱ������ʾ�Ĵ��ڣ����ճ���ʾ
				ScriptObject._setVisible( self, True )						# �ص��������ʾ����
		rds.ruisMgr.onRootShow( self )										# ���߹���������ʾ������
		self.onAfterShowed()												# ������ʾ�¼�

	def hide( self ) :
		"""
		���ش���
		"""
		if not self.onClose_() : return										# ���ȴ��� onClose_����� onClose_ ���� False����ȡ������
		ruisMgr.onRootHide( self )											# ���߹�������һ�� UI ����
		isActive = rds.ruisMgr.isActRoot( self )							# �Ƿ��ǵ�ǰ����� UI
		self.onBeforeClose()												# ��������ǰ�¼�
		ScriptObject._setVisible( self, False )								# �ص������ visible ���Է���
		if not self.rvisible :												# ������سɹ�
			if self.__pySubDialogs is not None :
				for pySubDialog in self.__pySubDialogs :					# ֪ͨ�����Ӵ���
					pySubDialog.__onOwnerHide()								# ���Ѿ�����
				self.__pySubDialogs = None									# ����ҵ������Ӵ���
			pyOwner = self.pyOwner
			if pyOwner is not None :										# ����и�����
				pyOwner.__removeSubDialog( self )							# ��Ӹ������б���������Լ�
				if isActive :
					rds.ruisMgr.activeRoot( pyOwner )						# �������
		self.onAfterClosed()												# �������غ��¼�

	# -------------------------------------------------
	def setOkButton( self, pyBtn ) :
		"""
		����Ĭ�ϵ�ȷ����ť
		"""
		if pyBtn is None :
			self.__pyOkBtn = None
		else :
			self.__pyOkBtn = weakref.ref( pyBtn )

	# ---------------------------------------
	def setCancelButton( self, pyBtn ) :
		"""
		����Ĭ�ϵ�ȡ����ť
		"""
		if pyBtn is None :
			self.__pyCancelBtn = None
		else :
			self.__pyCancelBtn = weakref.ref( pyBtn )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPosZSegment( self ) :
		return self.__posZSegment

	def _setPosZSegment( self, seg ) :
		oldSeg = self.__posZSegment
		self.__posZSegment = seg
		ruisMgr.onZSegmentChanged( self, oldSeg, seg )

	# -------------------------------------------------
	def _getOwner( self ) :
		if self.__pyOwner is None :
			return None
		return self.__pyOwner()

	def _getOkBtn( self ) :
		if self.__pyOkBtn is None :
			return None
		return self.__pyOkBtn()

	def _getCancelBtn( self ) :
		if self.__pyCancelBtn is None :
			return None
		return self.__pyCancelBtn()

	def _getSubDialogs( self ) :
		if self.__pySubDialogs is None :
			return []
		return self.__pySubDialogs.list()

	# ---------------------------------------
	def _setVisible( self, isVisible ) :
		argCount = self.show.func_code.co_argcount						# show �����Ĳ�������
		defs = self.show.im_func.func_defaults							# show ������Ĭ�ϲ���
		defCount = 0													# show ������Ĭ�ϲ�������
		if defs : defCount = len( defs )
		if argCount == defCount + 1 :									# ������������Ĭ�ϲ�������
			if isVisible : self.show()
			else : self.hide()
		elif self.pyOwner and argCount == 2 :							# ������������������ҵڶ�������Ϊ pyOwner
			if isVisible : self.show( self.pyOwner )
			else : self.hide()
		else :
			if isVisible : RootGUI.show( self, self.pyOwner )
			else : RootGUI.hide( self )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	posZSegment = property( _getPosZSegment, _setPosZSegment )			# ��ȡ/���ô��ڵĲ��
	hitable = property( lambda self : self.hitable_ )					# ��ȡ�����Ƿ��������������Ϊ False����ʹ����ڴ����ϣ���Ȼ��Ϊ���ֱ�ӵ��������Ļ
	activable = property( lambda self : self.activable_ )				# ��ȡ�����Ƿ�ɱ�����
	escHide = property( lambda self : self.escHide_ )					# ָ���� esc ���󣬴����Ƿ��������

	pyOwner = property( _getOwner )										# ��ȡ���ڵĸ�����
	pyOkBtn = property( _getOkBtn )										# ��ȡĬ�ϵ�ȷ�ϰ�ť
	pyCancelBtn = property( _getCancelBtn )								# ��ȡĬ�ϵ�ȡ����ť
	pySubDialogs = property( _getSubDialogs )							# ��ȡ���ڵ������Ӵ���
	visible = property( ScriptObject._getVisible, _setVisible )			# ��ȡ/���ô��ڵĿɼ���
