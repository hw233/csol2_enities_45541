# -*- coding: gb18030 -*-
#
# $Id: Control.py,v 1.35 2008-08-07 10:39:24 huangyongwei Exp $

"""
implement control base class
-- 2005/04/16 : writen by huangyongwei
"""

import weakref
import IME
from guis import *
from guis.common.ScriptObject import ScriptObject

class Control( ScriptObject ) :
	"""
	���пؼ��Ļ���
	"""
	def __init__( self, control = None, pyBinder = None ) :
		ScriptObject.__init__( self, control )
		self.__pyBinder = None								# �ؼ����ߣ�����Ϊ None
		self.__initialize( control, pyBinder )				# ��ʼ���ؼ�
		self.__canTabIn = True								# �ؼ��Ƿ���Ի�ý���
		self.__tabStop = False								# �ؼ��Ƿ��ý���
		self.__escTabOut = True								# ���� ESC ��ʱ���Ƿ��뽹�㣨��Ƹ������ǲ�����ģ�����Ϊ�˷���ʹ˷��ã�

	def subclass( self, control, pyBinder = None ) :
		"""
		�������ÿؼ��󶨵����� UI
		"""
		ScriptObject.subclass( self, control )
		self.__pyBinder = None
		self.__initialize( control, pyBinder )
		return self

	def dispose( self ) :
		"""
		�����ؼ�
		"""
		self.__pyBinder = None
		ScriptObject.dispose( self )

	def __del__( self ) :
		ScriptObject.__del__( self )
		if Debug.output_del_Control :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, control, pyBinder ) :
		if control is None : return
		if pyBinder is not None :
			self.__pyBinder = weakref.ref( pyBinder )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		ScriptObject.generateEvents_( self )
		self.__onTabIn = None
		self.__onTabOut = None
		self.__onEnable = None
		self.__onDisable = None
		self.__onKeyDown = None
		self.__onKeyUp = None
		self.__onMouseEnter = None
		self.__onMouseLeave = None
		self.__onMouseMove = None
		self.__onMouseScroll = None
		self.__onDragStart = None
		self.__onDragStop = None
		self.__onDrop = None
		self.__onDragEnter = None
		self.__onDragLeave = None
		# ----------------------------------------------------------------------
		#self.__onTabIn = self.createEvent_( "onTabIn" )				# ��ý���ʱ������
		#self.__onTabOut = self.createEvent_( "onTabOut" )			# �����뿪ʱ������
		#self.__onEnable = self.createEvent_( "onEnable" )			# ����ʱ������
		#self.__onDisable = self.createEvent_( "onDisable" )			# ����ʱ������
		#self.__onKeyDown = self.createEvent_( "onKeyDown" )			# ���̰�������ʱ������( �����һ���¼����� True������Ϣ����������·� )
		#self.__onKeyUp = self.createEvent_( "onKeyUp" )				# ���̰�������ʱ������( �����һ���¼����� True������Ϣ����������·� )
		#self.__onMouseEnter = self.createEvent_( "onMouseEnter" )	# ������ʱ������
		#self.__onMouseLeave = self.createEvent_( "onMouseLeave" )	# ����뿪ʱ������
		#self.__onMouseMove = self.createEvent_( "onMouseMove" )		# ����ڿؼ����ƶ�ʱ������
		#self.__onMouseScroll = self.createEvent_( "onMouseScroll" )	# ����ڿؼ��Ϲ����м�ʱ������
		#self.__onDragStart = self.createEvent_( "onDragStart" )		# ����ʱ������
		#self.__onDragStop = self.createEvent_( "onDragStop" )		# �ϷŽ���ʱ������
		#self.__onDrop = self.createEvent_( "onDrop" )				# ����ʱ������
		#self.__onDragEnter = self.createEvent_( "onDragEnter" )		# �ϷŽ���ʱ������
		#self.__onDragLeave = self.createEvent_( "onDragLeave" )		# �Ϸ��뿪ʱ������

	# -------------------------------------------------
	@property
	def onTabIn( self ) :
		"""
		��ý���ʱ������
		"""
		if self.__onTabIn is None:
			self.__onTabIn = self.createEvent_( "onTabIn" )				# ��ý���ʱ������
		return self.__onTabIn

	@property
	def onTabOut( self ) :
		"""
		�����뿪ʱ������
		"""
		if self.__onTabOut is None:
			self.__onTabOut = self.createEvent_( "onTabOut" )				# ��ý���ʱ������
		return self.__onTabOut

	# ---------------------------------------
	@property
	def onEnable( self ) :
		"""
		����ʱ������
		"""
		if self.__onEnable is None:
			self.__onEnable = self.createEvent_( "onEnable" )				# ��ý���ʱ������
		return self.__onEnable

	@property
	def onDisable( self ) :
		"""
		����ʱ������
		"""
		if self.__onDisable is None:
			self.__onDisable = self.createEvent_( "onDisable" )				# ��ý���ʱ������
		return self.__onDisable

	# ---------------------------------------
	@property
	def onKeyDown( self ) :
		"""
		���̰�������ʱ������
		"""
		if self.__onKeyDown is None:
			self.__onKeyDown = self.createEvent_( "onKeyDown" )				# ��ý���ʱ������
		return self.__onKeyDown

	@property
	def onKeyUp( self ) :
		"""
		���̰�������ʱ������
		"""
		if self.__onKeyUp is None:
			self.__onKeyUp = self.createEvent_( "onKeyUp" )				# ��ý���ʱ������
		return self.__onKeyUp

	# ---------------------------------------
	@property
	def onMouseEnter( self ) :
		"""
		������ʱ������
		"""
		if self.__onMouseEnter is None:
			self.__onMouseEnter = self.createEvent_( "onMouseEnter" )				# ��ý���ʱ������
		return self.__onMouseEnter

	@property
	def onMouseLeave( self ) :
		"""
		����뿪ʱ������
		"""
		if self.__onMouseLeave is None:
			self.__onMouseLeave = self.createEvent_( "onMouseLeave" )				# ��ý���ʱ������
		return self.__onMouseLeave

	# ---------------------------------------
	@property
	def onMouseMove( self ) :
		"""
		����ڿؼ����ƶ�ʱ������
		"""
		if self.__onMouseMove is None:
			self.__onMouseMove = self.createEvent_( "onMouseMove" )				# ��ý���ʱ������
		return self.__onMouseMove

	@property
	def onMouseScroll( self ) :
		"""
		����ڿؼ��Ϲ����м�ʱ������
		"""
		if self.__onMouseScroll is None:
			self.__onMouseScroll = self.createEvent_( "onMouseScroll" )				# ��ý���ʱ������
		return self.__onMouseScroll

	# ---------------------------------------
	@property
	def onDragStart( self ) :
		"""
		����ʱ������
		"""
		if self.__onDragStart is None:
			self.__onDragStart = self.createEvent_( "onDragStart" )				# ��ý���ʱ������
		return self.__onDragStart

	@property
	def onDragStop( self ) :
		"""
		�ϷŽ���ʱ������
		"""
		if self.__onDragStop is None:
			self.__onDragStop = self.createEvent_( "onDragStop" )				# ��ý���ʱ������
		return self.__onDragStop

	@property
	def onDrop( self ) :
		"""
		����ʱ������
		"""
		if self.__onDrop is None:
			self.__onDrop = self.createEvent_( "onDrop" )				# ��ý���ʱ������
		return self.__onDrop

	@property
	def onDragEnter( self ) :
		"""
		�ϷŽ���ʱ������
		"""
		if self.__onDragEnter is None:
			self.__onDragEnter = self.createEvent_( "onDragEnter" )				# ��ý���ʱ������
		return self.__onDragEnter

	@property
	def onDragLeave( self ) :
		"""
		�Ϸ��뿪ʱ������
		"""
		if self.__onDragLeave is None:
			self.__onDragLeave = self.createEvent_( "onDragLeave" )				# ��ý���ʱ������
		return self.__onDragLeave


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabIn_( self ) :
		"""
		����ý���ʱ������
		"""
		self.onTabIn()
		if hasattr( self, "notifyInput" ) :
			IME.active()

	def onTabOut_( self ) :
		"""
		�������뿪ʱ������
		"""
		self.onTabOut()
		IME.inactive()

	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		�����̼�����ʱ������
		"""
		if self.onKeyDown( key, mods ) :
			return True
		if self.__escTabOut and key == KEY_ESCAPE and mods == 0 :
			self.tabStop = False									# ���� ESC ���ѽ��㳷��
			ScriptObject.onKeyDown_( self, key, mods )
			return True
		return ScriptObject.onKeyDown_( self, key, mods )

	def onKeyUp_( self, key, mods ) :
		"""
		�����̼�����ʱ������
		"""
		if self.onKeyUp( key, mods ) :
			return True
		return ScriptObject.onKeyUp_( self, key, mods )

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		������ʱ������
		"""
		self.onMouseEnter()
		return ScriptObject.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		"""
		����뿪ʱ������
		"""
		self.onMouseLeave()
		return ScriptObject.onMouseLeave_( self )

	def onMouseMove_( self, dx, dy ) :
		"""
		����ڿؼ����ƶ�ʱ������
		"""
		self.onMouseMove( dx, dy )
		return ScriptObject.onMouseMove_( self, dx, dy )

	def onMouseScroll_( self, dz ) :
		"""
		����ڿؼ��Ϲ���ʱ������
		"""
		ScriptObject.onMouseScroll_( self, dz )
		self.onMouseScroll( dz )
		return True

	# ---------------------------------------
	def onDragStart_( self, pyDragged ) :
		"""
		�ؼ�������ʱ����
		"""
		ScriptObject.onDragStart_( self, pyDragged )
		self.onDragStart()
		return True

	def onDragStop_( self, pyDragged ) :
		"""
		�ؼ�������ʱ������
		"""
		self.onDragStop()

	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		���Ϸ� UI ����ʱ������
		"""
		ScriptObject.onDrop_( self, pyTarget, pyDropped )
		self.onDrop( pyDropped )
		return True

	def onDragEnter_( self, pyTarget, pyDragged ) :
		"""
		�ϷŽ���ؼ�ʱ������
		"""
		self.onDragEnter( pyDragged )

	def onDragLeave_( self, pyTarget, pyDragged ) :
		"""
		�Ϸ��뿪�ؼ�ʱ������
		"""
		self.onDragLeave( pyDragged )

	# ---------------------------------------
	def onEnable_( self ) :
		ScriptObject.onEnable_( self )
		if hasattr( self, "_Control__oldFX" ) :
			self.materialFX = self.__oldFX
			del self.__oldFX
		self.onEnable()

	def onDisable_( self ) :
		ScriptObject.onDisable_( self )
		self.tabStop = False
		self.__oldFX = self.materialFX
		self.materialFX = "COLOUR_EFF"
		r, g, b, a = self.gui.colourLightFactor
		self.gui.colourLightFactor = ( r, g, b, self.alpha / 255.0 )
		self.onDisable()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPyBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# ---------------------------------------
	def _getCanTabIn( self ) :
		return self.__canTabIn

	def _setCanTabIn( self, value ) :
		self.__canTabIn = value
		if not value :
			self.tabStop = False

	def _getTabStop( self ) :
		return rds.uiHandlerMgr.getTabInUI() == self

	def _setTabStop( self, value ) :
		if value and self.canTabIn :
			rds.uiHandlerMgr.tabInUI( self )
		else :
			rds.uiHandlerMgr.tabOutUI( self )

	def _getESCTabOut( self ) :
		return self.__escTabOut

	def _setESCTabOut( self, escTabOut ) :
		self.__escTabOut = escTabOut

	# -------------------------------------------------
	def _setVisible( self, visible ) :
		ScriptObject._setVisible( self, visible )
		if not self.rvisible and self.tabStop :
			self.tabStop = False


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getPyBinder )											# ��ȡ/���ÿؼ��İ���
	canTabIn = property( _getCanTabIn, _setCanTabIn )							# ��ȡ/���ÿؼ��Ƿ������ȡ����
	tabStop = property( _getTabStop, _setTabStop )								# ���ÿؼ�����״��
	escTabOut = property( _getESCTabOut, _setESCTabOut )					 	# ���� ESC ��ʱ���Ƿ��뽹��
	visible = property( ScriptObject._getVisible, _setVisible )					# ��ȡ/���ÿؼ��Ŀɼ���
