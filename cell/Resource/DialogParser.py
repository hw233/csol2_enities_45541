# -*- coding: gb18030 -*-
#
# $Id: DialogParser.py,v 1.4 2005-12-08 01:07:20 phw Exp $

"""
对话解释器
"""

import Xparser

class DialogParser( Xparser.Xparser ):
	"""
	对话解释器。
	解释规则::
		- 如果对话内容需要强制换行可以使用“[BREAK/]”标志
	"""
	def parseString( self, string ):
		"""
		继承于基类

		@return: 对话内容
		@rtype:  string
		"""
		self.msg = ""
		self.isBreak = False
		Xparser.Xparser.parseString( self, Xparser.stripLines( string, "\t" ) )
		return self.msg

	def startElementHandler( self, name, attrs ):
		"""继承于基类"""
		if name == "BREAK":
			self.isBreak = True
			self.msg += "\n"

	def endElementHandler( self, name ):
		self.isBreak = False

	def characterDataHandler( self, data ):
		assert not self.isBreak
		self.msg += data


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2005/10/12 08:07:29  phw
# 调整了对话方式
#
# Revision 1.2  2005/09/07 02:35:18  phw
# 修正了菜单位置混乱的问题
#
# Revision 1.1  2005/08/19 08:28:48  phw
# 对话内容解释器
#
#
