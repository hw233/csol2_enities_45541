# -*- coding: gb18030 -*-
#
# $Id: FuncRaceclass.py,v 1.6 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently

class FuncRaceclass( Function ):
	"""
	�ж�����ְҵ
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param = section.readInt( "param1" )  << 4	# ����4λ��ԭ������Ϊ��ǰ���û�������

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return player.getClass() == self.param


#
# $Log: not supported by cvs2svn $
# Revision 1.5  2007/06/14 09:58:54  huangyongwei
# ���������˺궨��
#
# Revision 1.4  2007/05/18 08:42:01  kebiao
# �޸�����param ΪtargetEntity
#
# Revision 1.3  2007/04/21 02:36:01  phw
# method modified: valid(), L3Command.isRaceclass -> player.isRaceclass
#
# Revision 1.2  2005/12/28 06:29:55  phw
# ��������ֵ���Ͳ���ȷ������
#
# Revision 1.1  2005/12/22 09:55:27  xuning
# no message
#
#
