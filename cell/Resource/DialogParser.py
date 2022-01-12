# -*- coding: gb18030 -*-
#
# $Id: DialogParser.py,v 1.4 2005-12-08 01:07:20 phw Exp $

"""
�Ի�������
"""

import Xparser

class DialogParser( Xparser.Xparser ):
	"""
	�Ի���������
	���͹���::
		- ����Ի�������Ҫǿ�ƻ��п���ʹ�á�[BREAK/]����־
	"""
	def parseString( self, string ):
		"""
		�̳��ڻ���

		@return: �Ի�����
		@rtype:  string
		"""
		self.msg = ""
		self.isBreak = False
		Xparser.Xparser.parseString( self, Xparser.stripLines( string, "\t" ) )
		return self.msg

	def startElementHandler( self, name, attrs ):
		"""�̳��ڻ���"""
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
# �����˶Ի���ʽ
#
# Revision 1.2  2005/09/07 02:35:18  phw
# �����˲˵�λ�û��ҵ�����
#
# Revision 1.1  2005/08/19 08:28:48  phw
# �Ի����ݽ�����
#
#
