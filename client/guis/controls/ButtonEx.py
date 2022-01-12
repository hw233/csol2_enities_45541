# -*- coding: gb18030 -*-

from guis.uidefine import UIState
from guis.controls.Button import Button
from guis.common.UIStatesTab import HStatesTabEx

# ���ఴťӵ��HFrameEx�Ŀ��
# ͨ�����ø���element��mapping��ʵ�ֲ�ͬ״̬�µı���
# �ṹ���£�
#
#	GUI.TextureFrame :
#	children :
#		lbText
#	elements :
#		frm_l, frm_bg, fem_r
# ����element�������һ�µ� mapping state


class HButtonEx( Button, HStatesTabEx ) :
	"""
	GUI.TextureFrame :
	children :
		lbText
	elements :
		frm_l, frm_bg, fem_r
	"""
	def __init__( self, button, pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		HStatesTabEx.__init__( self, button )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setStateView_( self, state ) :
		"""
		����ָ��״̬�µ���۱���
		"""
		if state == UIState.DISABLE :
			self.setDisableView_()
			return
		Button.setStateView_( self, state )
		self.exMappings = self.exMappingsMap_[state]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setExStatesMapping( self, stMode ) :
		HStatesTabEx.setExStatesMapping( self, stMode )
		if self.enable :
			self.setState( UIState.COMMON )