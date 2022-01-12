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
	__history_count = 6						# 存放历史名称的个数

	def __init__( self, cb ) :
		ODComboBox.__init__( self, cb )
		self.readOnly = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabOut_( self ) :
		"""
		焦点离开时，把密语者名字保存到历史纪录
		"""
		ODComboBox.onTabOut_( self )
		text = self.text.strip()
		if text == "" : return
		if text in self.items :									# 历史列表中已经存在该密语者
			self.sort( key = lambda pyItem : pyItem == text )	# 则把最新用过的密语者放到最后
		else :
			if self.itemCount >= self.__history_count :			# 如果历史数量已经超过指定值
				self.removeItemOfIndex( 0 )						# 删除最前面一个
			self.addItem( text )								# 并将新的添加到最后


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		重新恢复为默认状态
		"""
		self.clearItems()
		self.text = ""


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( lambda self : self.pyBox.text, \
		lambda self, v : self.pyBox._setText( v ) )
