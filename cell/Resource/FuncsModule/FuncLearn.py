# -*- coding: gb18030 -*-
#
# $Id: FuncLearn.py,v 1.7 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld

class FuncLearn( Function ):
	"""
	ѧϰ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		talkEntity.sendTrainInfoToPlayer( player.id, 0 )

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
		return True


#
# $Log: not supported by cvs2svn $
# Revision 1.6  2007/12/05 03:36:24  phw
# �������޷���ȷ�رտͻ��˶Ի������bug
#
# Revision 1.5  2007/06/14 09:58:54  huangyongwei
# ���������˺궨��
#
# Revision 1.4  2007/05/18 08:42:01  kebiao
# �޸�����param ΪtargetEntity
#
# Revision 1.3  2006/12/11 11:21:09  huangyongwei
# ����˽����Ի���endGooip
#
# Revision 1.2  2006/02/28 08:13:07  phw
# no message
#
# Revision 1.1  2005/12/22 09:55:27  xuning
# no message
#
#
