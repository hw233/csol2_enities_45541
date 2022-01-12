# -*- coding: gb18030 -*-
#
# $Id: WhisperTextBox.py,v 1.5 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement textbox for inputing whisper's name

2009/03/23: writen by huangyongwei
"""

from guis import *
from guis.controls.ODComboBox import ODComboBox

class WhisperInputBox( ODComboBox ) :
	__history_count = 6						# �����ʷ���Ƶĸ���

	def __init__( self, cb ) :
		ODComboBox.__init__( self, cb )
		self.readOnly = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabOut_( self ) :
		"""
		�����뿪ʱ�������������ֱ��浽��ʷ��¼
		"""
		ODComboBox.onTabOut_( self )
		text = self.text.strip()
		if text == "" : return
		if text in self.items :									# ��ʷ�б����Ѿ����ڸ�������
			self.sort( key = lambda pyItem : pyItem == text )	# ��������ù��������߷ŵ����
		else :
			if self.itemCount >= self.__history_count :			# �����ʷ�����Ѿ�����ָ��ֵ
				self.removeItemOfIndex( 0 )						# ɾ����ǰ��һ��
			self.addItem( text )								# �����µ���ӵ����


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		���»ָ�ΪĬ��״̬
		"""
		self.clearItems()
		self.text = ""


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( lambda self : self.pyBox.text, \
		lambda self, v : self.pyBox._setText( v ) )
