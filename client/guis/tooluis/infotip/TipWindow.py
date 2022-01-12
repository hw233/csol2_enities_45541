# -*- coding: gb18030 -*-
#
# $Id: TipWindow.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

"""
implement information tips window

-- 2008/08/28 : writen by huangyongwei
"""

from guis import *
from guis.common.FlexWindow import HVFlexWindow

class TipWindow( HVFlexWindow ) :
	cc_fade_speed_			= 0.3		# ������ʱ
	cc_edge_width_			= 8.0		# ��������صľ���

	def __init__( self ) :
		wnd = GUI.load( "guis/tooluis/infotip/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		HVFlexWindow.__init__( self, wnd )
		self.posZSegment = ZSegs.L1
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.moveFocus = False
		wnd.visible = False
		self.addToMgr()

		self.__fader = wnd.fader
		self.__fader.value = 0
		self.__fader.speed = self.cc_fade_speed_

		self.__fadeDelayCBID = 0						# ������ʱ�ص� ID
		self.__vsDetectCBID = 0							# �����󶨿ؼ��ɼ����ص� ID

	def __del__( self ) :
		if Debug.output_del_InfoTip :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __visableDetect( self, pyBinder ) :
		"""
		�������Ƿ�ɼ���������ɼ���������������ʾ��
		"""
		BigWorld.cancelCallback( self.__vsDetectCBID )
		if not pyBinder.rvisible :
			self.hide()
		elif rds.ruisMgr.getMouseHitRoot() != pyBinder.pyTopParent :	# ������û�л��а󶨿ؼ�
			self.hide()													# ��������ʾ������������ԣ��ݽ�ȼü֮����
		else :
			func = Functor( self.__visableDetect, pyBinder )
			self.__vsDetectCBID = BigWorld.callback( 1.0, func )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, pyBinder ) :
		BigWorld.cancelCallback( self.__fadeDelayCBID )
		self.__fader.value = 1.0
		self.__visableDetect( pyBinder )
		HVFlexWindow.show( self )

	def hide( self ) :
		BigWorld.cancelCallback( self.__fadeDelayCBID )
		BigWorld.cancelCallback( self.__vsDetectCBID )
		self.__fader.value = 0.0
		def delayHide() :
			HVFlexWindow.hide( self )
			self.clear()
		self.__fadeDelayCBID = BigWorld.callback( self.__fader.speed, delayHide )

	def clear( self ) :
		"""
		��������ı�
		"""
		pass
