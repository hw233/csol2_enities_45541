# -*- coding: gb18030 -*-
#
# $Id: Function.py,v 1.4 2008-01-15 06:06:34 phw Exp $

"""
"""

class Function:
	"""
	�Ի������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass
	
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ�����ܣ���������
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass
	
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ�ã���������
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/05/18 08:42:02  kebiao
# �޸�����param ΪtargetEntity
#
# Revision 1.2  2005/12/22 09:55:27  xuning
# no message
#
# Revision 1.1  2005/12/08 01:08:03  phw
# no message
#
#
