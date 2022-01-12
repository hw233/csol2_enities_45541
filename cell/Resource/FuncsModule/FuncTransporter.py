# -*- coding: gb18030 -*-
#
# $Id: FuncTransporter.py,v 1.5 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
import Const

class FuncTransporter( Function ):
	"""
	װ��ǿ��
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
		talkEntity.transportDialog( player.id, "Talk" )

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
		if player.hasMerchantItem():
			return False
		# ����з�������buff
		if len( player.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return False
		return True


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2007/12/05 03:36:24  phw
# �������޷���ȷ�رտͻ��˶Ի������bug
#
# Revision 1.3  2007/06/14 09:58:54  huangyongwei
# ���������˺궨��
#
# Revision 1.2  2007/05/18 08:42:02  kebiao
# �޸�����param ΪtargetEntity
#
# Revision 1.1  2007/05/10 02:28:21  panguankong
# ����ļ�
#
# Revision 1.1  2007/04/06 01:33:53  panguankong
# ����ļ�
#
# Revision 1.1  2007/04/05 02:04:13  panguankong
# ��Ӳ��Ϻϳɹ���
#
#