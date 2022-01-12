# -*- coding: gb18030 -*-
#
# $Id: PushButton.py,v 1.3 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement button class��
-- 2008/06/18 : writen by huangyongwei
"""
"""
composing :
	GUI.XXX

or
	GUI.Window
		-- lbText��GUI.Text( ����û�� )
"""


from guis import *
from Button import Button

class PushButton( Button ) :
	"""
	���������һ�����£��ظ����һ��������İ�ť
	"""
	def __init__( self, button = None, pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		self.__initialize( button )						# ��ʼ��
		self.__pushed = False							# �Ƿ��ڰ���״̬

	def subclass( self, button, pyBinder = None ) :
		Button.subclass( self, button, pyBinder )
		self.__initialize( button )
		return self

	def __del__( self ) :
		Button.__del__( self )
		if Debug.output_del_Button :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, button ) :
		pass


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Button.generateEvents_( self )
		self.__onPushed = self.createEvent_( "onPushed" )			# ������ʱ����
		self.__onRaised = self.createEvent_( "onRaised" )			# ������ʱ����

	@property
	def onPushed( self ) :
		"""
		������ʱ����
		"""
		return self.__onPushed

	@property
	def onRaised( self ) :
		"""
		������ʱ����
		"""
		return self.__onRaised


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __push( self ) :
		"""
		����Ϊѡ��״̬
		"""
		if self.pushed : return
		self.__pushed = True
		self.setState( UIState.PRESSED )
		self.onPushed()

	def __raise( self ) :
		"""
		ȡ��ѡ��
		"""
		if not self.pushed : return
		self.__pushed = False
		self.setState( UIState.COMMON )
		self.onRaised()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseUp_( self, mods ) :
		Button.onLMouseUp_( self, mods )
		if self.enable and self.pushed :
			self.setState( UIState.PRESSED )
		return True

	# ---------------------------------------
	def onLClick_( self, mods ) :
		Button.onLClick_( self, mods )
		if self.isMouseHit() :
			self.pushed = not self.pushed
		return True

	# ---------------------------------------
	def onMouseEnter_( self ) :
		Button.onMouseEnter_( self )
		if self.pushed :
			self.setState( UIState.PRESSED )
		else :
			self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		Button.onMouseLeave_( self )
		if self.pushed :
			self.setState( UIState.PRESSED )
		else :
			self.setState( UIState.COMMON )
		return True

	# ---------------------------------------
	def onEnable_( self ) :
		Button.onEnable_( self )
		if self.pushed :
			self.setState( UIState.PRESSED )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPushed( self ) :
		return self.__pushed

	def _setPushed( self, pushed ) :
		if pushed : self.__push()
		else : self.__raise()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pushed = property( _getPushed, _setPushed )										# ����ѡ��״̬
