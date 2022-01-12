# -*- coding: gb18030 -*-
#
# $Id: ScriptObject.py,v 1.27 2008-08-05 01:18:53 huangyongwei Exp $

"""
python gui contains events
2006/08/20 : writen by huangyongwei
"""

from guis import *
from guis.ExtraEvents import ControlEvent
from GUIBaseObject import GUIBaseObject
from gbref import rds

class ScriptObject( GUIBaseObject ) :
	def __init__( self, gui = None ) :
		GUIBaseObject.__init__( self, gui )
		self.__initialize( gui )					# ��ʼ��
		self.__mouseScrollFocus = False				# ����һ������������� focus

		self.__enable = True						# ��¼�Ƿ���ã����ǻ�ɫ״̬��
		self.__dragMark = DragMark.NONE				# ����Ĭ�ϵ��Ϸű��

		self.__isLMouseDown = False					# ��ʱ������������������ʱ��¼Ϊ True��������������ʱ�����������ж��Ƿ��ǵ��
		self.__isRMouseDown = False					# ��ʱ������������Ҽ�����ʱ��¼Ϊ True��������Ҽ�����ʱ�����������ж��Ƿ��ǵ��
		self.__clickCount = 0						# ��ʱ��������¼��������������Ĵ�������ʵ��˫��
		self.__dbclickCBID = 0						# ��ʱ������ʵ��˫���� callback ID����갴��ʱ����ʱ��ʱ�䵽����� __clickCount���Զ���˫����¼

		self.generateEvents_()						# �����¼�

	def subclass( self, gui ) :
		GUIBaseObject.subclass( self, gui )
		self.__initialize( gui )
		return self

	def dispose( self ) :
		"""
		release resource
		"""
		self.focus = False
		self.moveFocus = False
		self.crossFocus = False
		self.dragFocus = False
		self.dropFocus = False
		self.mouseScrollFocus = False
		GUIBaseObject.dispose( self )

	def __del__( self ) :
		self.__guiObject = None
		GUIBaseObject.__del__( self )
		if Debug.output_del_ScriptObject :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, gui ) :
		"""
		��ʼ��
		"""
		if gui is None : return
		self.__guiObject = gui


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		event = ControlEvent( ename, self )
		return event

	def generateEvents_( self ) :
		self.__onLMouseDown = None
		self.__onLMouseUp = None
		self.__onRMouseDown = None
		self.__onRMouseUp = None
		self.__onLClick = None
		self.__onRClick = None
		self.__onLDBClick = None
		
		# ��ʹ��ʱ�����ɣ���Ϸ������ֻ����һ����ui�ᱻʹ�õ����ⲿ��ui��Ҳֻ�����ɸ��¼��ᱻ������16:15 2013-4-25 by wsf
		#self.__onLMouseDown = self.createEvent_( "onLMouseDown" )		# ������������ʱ������
		#self.__onLMouseUp = self.createEvent_( "onLMouseUp" )			# ������������ʱ������
		#self.__onRMouseDown = self.createEvent_( "onRMouseDown" )		# ������Ҽ�����ʱ������
		#self.__onRMouseUp = self.createEvent_( "onRMouseUp" )			# ������Ҽ�����ʱ������
		#self.__onLClick = self.createEvent_( "onLClick" )				# �����������ʱ������
		#self.__onRClick = self.createEvent_( "onRClick" )				# ������Ҽ����ʱ������
		#self.__onLDBClick = self.createEvent_( "onLDBClick" )			# ��������˫��ʱ������

	# ---------------------------------------
	@property
	def onLMouseDown( self ) :
		"""
		������������ʱ������
		"""
		if self.__onLMouseDown is None:
			self.__onLMouseDown = self.createEvent_( "onLMouseDown" )	
		return self.__onLMouseDown

	@property
	def onLMouseUp( self ) :
		"""
		������������ʱ������
		"""
		if self.__onLMouseUp is None:
			self.__onLMouseUp = self.createEvent_( "onRMouseUp" )
		return self.__onLMouseUp

	@property
	def onRMouseDown( self ) :
		"""
		������Ҽ�����ʱ������
		"""
		if self.__onRMouseDown is None:
			self.__onRMouseDown = self.createEvent_( "onRMouseDown" )
		return self.__onRMouseDown

	@property
	def onRMouseUp( self ) :
		"""
		������Ҽ�����ʱ������
		"""
		if self.__onRMouseUp is None:
			self.__onRMouseUp = self.createEvent_( "onRMouseUp" )
		return self.__onRMouseUp

	# ---------------------------------------
	@property
	def onLClick( self ) :
		"""
		�����������ʱ������
		"""
		if self.__onLClick is None:
			self.__onLClick = self.createEvent_( "onLClick" )
		return self.__onLClick

	@property
	def onRClick( self ) :
		"""
		������Ҽ����ʱ������
		"""
		if self.__onRClick is None:
			self.__onRClick = self.createEvent_( "onRClick" )
		return self.__onRClick

	@property
	def onLDBClick( self ) :
		"""
		��������˫��ʱ������
		"""
		if self.__onLDBClick is None:
			self.__onLDBClick = self.createEvent_( "onLDBClick" )
		return self.__onLDBClick


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __enableAllChildren( self ) :
		"""
		�ָ� enable ֮ǰ���� enable Ϊ True �ĺ��ӵ� enable ����
		"""
		def verifier( pyCh ) :
			if not pyCh.acceptEvent :							# ������� UI �������¼�
				return False, 1									# ����Ը��� UI�������������� UI ���� UI
			if not pyCh.enable :								# ������� UI ���� disable�������������� UI �϶�Ҳ�� disable
				return False, 0									# ��ˣ����Ը��� UI�����Ҳ��ټ������������ UI
			return True, 1										# ������� UI �Ѿ� �� disable ��Ϊ enable���򽫸��� UI ��ӵ��б������������� UI ���� UI

		pyChs = util.preFindPyGui( self.__guiObject, verifier )	# ǰ���������е��� UI
		for pyCh in pyChs : pyCh.onEnable_()					# �������Ѿ����� enable ״̬���� UI �� onEnable_ ����

	def __disableAllChildren( self ) :
		"""
		disable ʱ��ͬʱ disable ���еĺ���
		"""
		def verifier( pyCh ) :
			if pyCh == self :									# ����� UI �����ұ���
				return True, 1									# ����ܵ��б�������������� UI
			if not pyCh.acceptEvent :							# ������� UI �������¼�
				return False, 1									# ����Ը��� UI�������������� UI ���� UI
			if not pyCh.__enable :								# ������� UI ԭ���ʹ�����Ч״̬
				return False, 0									# ����Ը��� UI�����Ҳ��ټ����� UI �������� UI
			return True, 1										# ������� UI �Ѿ��� enable ��Ϊ disable���򽫸��� UI ��ӵ��б������������� UI ���� UI
		pyChs = util.preFindPyGui( self.__guiObject, verifier )	# ǰ���������е��� UI
		for pyCh in pyChs : pyCh.onDisable_()					# �������Ѿ����� disable ״̬���� UI �� onEnable_ ����

	# -------------------------------------------------
	def __onDCHoldingEnd( self ) :
		"""
		��¼˫����ʱ��ʱ������
		"""
		self.__clickCount = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def resetBindingUI_( self, gui ) :
		"""
		���°�һ���µ����� UI
		"""
		if gui == self.__guiObject : return
		GUIBaseObject.resetBindingUI_( self, gui )
		self.__guiObject = gui


	# -------------------------------------------------
	# about keyboard
	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		�����̼�����ʱ������
		"""
		return False

	def onKeyUp_( self, key, mods ) :
		"""
		�����̼�����ʱ������
		"""
		return False


	# -------------------------------------------------
	# about mouse
	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		"""
		������������ʱ������
		"""
		self.onLMouseDown()
		return True

	def onLMouseUp_( self, mods ) :
		"""
		������������ʱ������
		"""
		self.onLMouseUp()
		if rds.worldCamHandler._WorldCamHandler__isFixup :
			rds.worldCamHandler.unfix()
		return True


	def onRMouseDown_( self, mods ) :
		"""
		������Ҽ�����ʱ������
		"""
		self.onRMouseDown()
		return True

	def onRMouseUp_( self, mods ) :
		"""
		������Ҽ�����ʱ������
		"""
		self.onRMouseUp()
		if rds.worldCamHandler._WorldCamHandler__isFixup :
			rds.worldCamHandler.unfix()
		return True

	# ------------------------------------------------
	def onLClick_( self, mods ) :
		"""
		�����������ʱ������
		"""
		self.onLClick()
		return True

	def onRClick_( self, mods ) :
		"""
		������Ҽ����ʱ������
		"""
		self.onRClick()
		return True

	def onLDBClick_( self, mods ) :
		"""
		�����˫��ʱ������
		"""
		self.onLDBClick()
		return True

	# ------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		��������ʱ������
		"""
		pass

	def onMouseLeave_( self ) :
		"""
		������뿪ʱ������
		"""
		pass

	# ------------------------------------------------
	def onMouseMove_( self, dx, dy ) :
		"""
		������ƶ�ʱ������
		"""
		return True

	def onMouseScroll_( self, dx ) :
		"""
		�������ֹ���ʱ������
		"""
		return True


	# -------------------------------------------------
	# about drag & drop
	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		"""
		����ʼ����һ�� UI ����ʱ������
		"""
		if self.__guiObject is None : return False
		if not BigWorld.isKeyDown( KEY_LEFTMOUSE ) : return True
		rds.ruisMgr.dragObj.show( self, self.dragMark )
		return self.isMouseHit()

	def onDragStop_( self, pyDragged ) :
		"""
		���ϷŽ���ʱ������
		"""
		pass

	# ---------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		��һ���Ϸ�һ�� UI �����������Ϸ���ʱ������
		"""
		return False

	# ---------------------------------------
	def onDragEnter_( self, pyTarget, pyDragged ) :
		"""
		���ϷŽ���ʱ������
		"""
		pass

	def onDragLeave_( self, pyTarget, pyDragged ) :
		"""
		���Ϸ��뿪ʱ������
		"""
		pass

	# ---------------------------------------
	def onEnable_( self ) :
		"""
		����Ч��Ϊ��Ч״̬ʱ������
		"""
		pass

	def onDisable_( self ) :
		"""
		����Ч��Ϊ��Ч״̬ʱ������
		"""
		pass


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# keyboard relative
	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		�����̼����»�����ʱ������
		"""
		if key in KEY_MOUSE_KEYS : return False				# ��������갴����Ϣ
		if down and self.onKeyDown_( key, mods ) :			# �������������¼�
			return True
		if not down and self.onKeyUp_( key, mods ) :		# �������������¼�
			return True
		return False

	def handleAxisEvent( self, axis, value, dTime ):
		if not self.enable : return True
		return False


	# ----------------------------------------------------------------
	# mouse relative
	# ----------------------------------------------------------------
	def handleMouseButtonEvent( self, comp, key, down, mods, pos ) :
		"""
		����갴�����»�����ʱ������
		"""
		if not self.enable : return False						# ��������ã��򷵻�
		if rds.ruisMgr.dragObj.dragging : return True			# ��������Ϸ�״̬���򷵻�

		result = False
		# -----------------------------------
		# ���������¼�
		# -----------------------------------
		if down and key == KEY_LEFTMOUSE :						# ����������
			self.__isLMouseDown = True							# ������������±��
			self.__clickCount += 1								# ������������ 1
			self.__dbclickCBID = BigWorld.callback( 0.8, \
				self.__onDCHoldingEnd )							# ��ʱ 0.8 �����յ������
			result = self.onLMouseDown_( mods )					# ������������¼�
		if down and key == KEY_RIGHTMOUSE :						# ��������Ҽ�
			self.__isRMouseDown = True							# �������Ҽ����±��
			result = self.onRMouseDown_( mods )					# ���������Ҽ��¼�

		if not down and key == KEY_LEFTMOUSE :					# ����������
			clickResult = False									# ����һ����ʱ��������¼��Ƕ���ڵĴ����¼����
			if self.__isLMouseDown :							# ���������±��Ϊ True����ʾ����������ϰ��£�
				clickResult = self.onLClick_( mods )			# �򣬴�������¼����������ϰ��£������������������ڵ����
				self.__isLMouseDown = False						# ���������±�ǣ���ֹ�´��������������������Ҳ�ᴥ�������
			if self.__clickCount == 2 :							# ͳ������ڹ涨ʱ�����������ϰ��µĴ������������ 2
				BigWorld.cancelCallback( self.__dbclickCBID )	# ��ȡ��������ʱ����ձ���˫��������
				self.onLDBClick_( mods )						# ����˫���¼�
			upResult = self.onLMouseUp_( mods )					# ��󴥷���������¼�
			result = upResult or clickResult					# ����ǣ���Χ�����Ƕ���ڽ���Ļ����
		if not down and key == KEY_RIGHTMOUSE :					# �����������Ҽ�
			clickResult = False									# ����һ����ʱ��������¼��Ƕ���ڵĴ����¼����
			if self.__isRMouseDown :							# ����Ҽ�������Ϊ True��˵���Ҽ��������ϰ��£�
				clickResult = self.onRClick_( mods )			# �򣬴����һ��¼���ֻ���������ϰ��£�ͬʱҲ����������������ڵ����
				self.__isRMouseDown = False						# ����Ҽ����±�ǣ���ֹ�´��Ҽ�����������������Ҳ�ᴥ�������
			upResult = self.onRMouseUp_( mods )					# �����Ҽ������¼�
			result = upResult or clickResult					# ѡȡ����
		return result											# ���ص�����

	def handleMouseClickEvent( self, comp, pos ) :
		"""
		����굥��ʱ������
		"""
		if not self.enable : return True
		return False

	def handleMouseEvent( self, comp, pos ) :
		"""
		������ƶ�ʱ������
		"""
		if not self.enable : return True						# �����Ч���򷵻�
		dx, dy = rds.uiHandlerMgr.mouseOffset					# �ƶ�ǰ��λ�ò�
		if rds.uiHandlerMgr.isCapped( self ) :					# ���ȴ��� cap UI
			return self.onMouseMove_( dx, dy )					# ��������ƶ��¼�
		if self.isMouseHit() :									# ������� cap UI����ֻ������� UI ����
			return self.onMouseMove_( dx, dy )					# �Ŵ����ƶ��¼�
		return False

	# -------------------------------------------------
	def handleMouseEnterEvent( self, comp, pos ) :
		"""
		��������ʱ������
		"""
		if not self.enable : return True						# �����ã��򷵻�
		if ruisMgr.getMouseHitRoot() == self.pyTopParent :		# �����е����������Ĵ���
			self.onMouseEnter_()								# �����������¼�
		return True

	def handleMouseLeaveEvent( self, comp, pos ) :
		"""
		������뿪ʱ������
		"""
		if not self.enable : return True						# �����ã��򷵻�
		self.onMouseLeave_()									# ��������뿪�¼�
		return True

	# -------------------------------------------------
	# drag & drop relative
	# -------------------------------------------------
	def handleDragStartEvent( self, comp, pos ) :
		"""
		����ʼ�Ϸ�ʱ������
		"""
		if not self.enable : return False							# �����ã��򲻴����Ϸ��¼�
		if not BigWorld.isKeyDown( KEY_LEFTMOUSE ) : return False	# ���û�е���ȥ���򲻴����Ϸ��¼�
		def resetDragItemMouseInPos( itemPos, pos ) :				# ����������ϷŶ������ϵ�����
			left = pos[0] - itemPos[0]
			top = pos[1] - itemPos[1]
			rds.ruisMgr.dragObj.mouseInPos = ( left, top )

		pyDraged = UIScriptWrapper.unwrap( comp )					# �ϷŶ���� python UI
		if pyDraged is None : return False							# ��������ڣ���ȡ���Ϸ�
		if not pyDraged.rvisible : return False						# ����ϷŶ��󲻿ɼ�����ȡ���Ϸ�
		if ruisMgr.getMouseHitRoot() == pyDraged.pyTopParent :		# �ϷŶ���ĸ����ڣ����뱻������
			done = self.onDragStart_( pyDraged )					# �����Ϸ��¼�
			resetDragItemMouseInPos( pyDraged.r_posToScreen, pos )	# �����ϷŶ����λ��
			return done												# �����Ϸųɹ�
		return False

	def handleDragStopEvent( self, comp, pos ) :
		"""
		���ϷŽ���ʱ������
		"""
		if not self.enable : return True							# �ϷŶ��󲻿���
		pyDraged = UIScriptWrapper.unwrap( comp )					# ��ȡ�ϷŶ���� python UI
		if pyDraged is None : return False							# �����ڣ���ȡ���ϷŽ���֪ͨ
		self.onDragStop_( pyDraged )								# �����ϷŽ����¼�
		return True

	# ---------------------------------------
	def handleDropEvent( self, comp, pos, dropped ) :
		"""
		���Ϸ��������Ϸ���ʱ������
		"""
		if not self.enable : return True							# �������򷵻�
		pyTarget = UIScriptWrapper.unwrap( comp )					# ��ȡ���¶���� python UI
		self.onDrop_( pyTarget, UIScriptWrapper.unwrap( dropped ) )	# ���������¼�
		return True

	# ---------------------------------------
	def handleDragEnterEvent( self, comp, pos, dragged ) :
		"""
		���ϷŽ���ʱ������
		"""
		if not self.enable : return True
		pyTarget = UIScriptWrapper.unwrap( comp )
		if pyTarget is None : return False
		self.onDragEnter_( pyTarget, UIScriptWrapper.unwrap( dragged ) )
		return True

	def handleDragLeaveEvent( self, comp, pos, dragged ) :
		"""
		���Ϸ��뿪ʱ������
		"""
		if not self.enable : return True
		pyTarget = UIScriptWrapper.unwrap( comp )
		if pyTarget is None : return False
		self.onDragLeave_( pyTarget, UIScriptWrapper.unwrap( dragged ) )
		return True


	# -------------------------------------------------
	# inner methods
	# -------------------------------------------------
	def focus( self, state ) :
		"""
		�÷����������ڲ���������Ϊ�����õ������� focus ��������
		"""
		pass

	def crossFocus( self, state ) :
		"""
		�÷����������ڲ���������Ϊ�����õ������� crossFocus ��������
		"""
		pass

	def moveFocus( self, state ) :
		"""
		�÷����������ڲ���������Ϊ�����õ������� moveFocus ��������
		"""
		pass

	def dragFocus( self, state ) :
		"""
		�÷����������ڲ���������Ϊ�����õ������� dragFocus ��������
		"""
		pass

	def dropFocus( self, state ) :
		"""
		�÷����������ڲ���������Ϊ�����õ������� dropFocus ��������
		"""
		pass

	# -------------------------------------------------
	def onLoad( self, dataSection ) :
		pass

	def onDelete( self ) :
		pass

	def onSave( self, dataSection ) :
		pass

	def onBound( self ) :
		pass


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getScriptParent( self ) :
		parent = self.__guiObject.parent
		while parent :
			pyParent = UIScriptWrapper.unwrap( parent )
			if pyParent and pyParent.acceptEvent :
				return pyParent
			parent = parent.parent
		return None

	# -------------------------------------------------
	def _getFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.focus

	def _setFocus( self, value ) :
		self.__guiObject.focus = False					# ���ȴ� focus �б����������������� bug��������ﲻ��������Ϊ False����������ý���Ч��
		self.__guiObject.focus = value					# �ټ��� focus �б�

	# ---------------------------------------
	def _getMoveFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.moveFocus

	def _setMoveFocus( self, value ) :
		self.__guiObject.moveFocus = value

	# ---------------------------------------
	def _getCrossFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.crossFocus

	def _setCrossFocus( self, value ) :
		self.__guiObject.crossFocus = value

	# ---------------------------------------
	def _getMouseScrollFocus( self ) :
		if not self.enable : return False
		return self.__mouseScrollFocus

	def _setMouseScrollFocus( self, value ) :
		self.__mouseScrollFocus = value

	# ---------------------------------------
	def _getDragFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.dragFocus

	def _setDragFocus( self, value ) :
		self.__guiObject.dragFocus = value

	# ---------------------------------------
	def _getDropFocus( self ) :
		if not self.enable : return False
		return self.__guiObject.dropFocus

	def _setDropFocus( self, value ) :
		self.__guiObject.dropFocus = value

	# ---------------------------------------
	def _getEnable( self ) :
		if not self.__enable : return False
		pyParent = self.pyScriptParent
		while pyParent :										# ����и� UI ���� disable
			if not pyParent.enable :							# ��
				return False									# ������ UI Ҳ�� disable
			pyParent = pyParent.pyScriptParent
		return True

	def _setEnable( self, enable ) :
		if self.__enable == enable : return						# ����ֵû���򷵻�
		self.__enable = enable									# ��������Ϊ��Ϣ����״̬
		if enable :
			if self.enable :									# û�� disable �ĸ���
				self.__enableAllChildren()						# ������ԭ��Ϊ enable ���� UI һͬ enable
		else :
			pyParent = self.pyScriptParent
			if not pyParent or pyParent.enable :				# ���� enable
				self.__disableAllChildren()						# �������� UI ����Ϊ disable

	# -------------------------------------------------
	def _getDragMark( self ) :
		return self.__dragMark

	def _setDragMark( self, mark ) :
		self.__dragMark = mark


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyScriptParent = property( _getScriptParent )								# ��ȡ���һ����εļ̳��� ScriptObject �� parent
	acceptEvent = property( lambda self : True )								# ָ�� python �Ƿ����ϵͳ��Ϣ
	focus = property( _getFocus, _setFocus )									# ��ȡ/�����Ƿ���հ������������Ϣ
	moveFocus = property( _getMoveFocus, _setMoveFocus )						# ��ȡ/�����Ƿ��������ƶ���Ϣ
	crossFocus = property( _getCrossFocus, _setCrossFocus )						# ��ȡ/�����Ƿ������������Ϣ
	mouseScrollFocus = property( _getMouseScrollFocus, _setMouseScrollFocus )	# ��ȡ/�����Ƿ������������Ϣ
	dragFocus = property( _getDragFocus, _setDragFocus )						# ��ȡ/�����Ƿ�������������Ϣ
	dropFocus = property( _getDropFocus, _setDropFocus )						# ��ȡ/�����Ƿ������������Ϣ
	enable = property( _getEnable, _setEnable )									# ��ȡ/���ñ� UI �Ƿ���ã��ǻ�ɫ״̬��

	dragMark = property( _getDragMark, _setDragMark )							# ��ȡ/�����Ϸű��
