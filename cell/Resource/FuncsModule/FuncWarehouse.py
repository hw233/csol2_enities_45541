# -*- coding: gb18030 -*-
#
# $Id: FuncWarehouse.py,v 1.12 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import csdefine

class FuncWarehouse( Function ):
	"""
	���� -- �ֿ�
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
		player.client.enterBank( talkEntity.id )
		player.endGossip( talkEntity )

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
# Revision 1.11  2007/12/22 09:53:05  fangpengjun
# �����ͻ��˴򿪲ֿ�ӿ�
#
# Revision 1.10  2007/12/05 03:36:24  phw
# �������޷���ȷ�رտͻ��˶Ի������bug
#
# Revision 1.9  2007/11/07 09:36:03  huangyongwei
# < 		player.enterInventoryTrade( talkEntity.id )
#
# ---
# > 		player.enterTradeIV( talkEntity.id )
#
# Revision 1.8  2007/08/18 08:06:02  yangkai
# NPC���״������
#     - �Ż���NPC����״̬���ж�
#     - ��ؽӿ����˸ı�
#
# Revision 1.7  2007/06/14 09:58:54  huangyongwei
# ���������˺궨��
#
# Revision 1.6  2007/05/18 08:42:02  kebiao
# �޸�����param ΪtargetEntity
#
# Revision 1.5  2006/12/21 10:14:18  phw
# ȡ���˲������ֿ�򿪲�����Ҫ��������
#
# Revision 1.4  2006/02/28 08:13:07  phw
# no message
#
# Revision 1.3  2005/12/22 09:55:27  xuning
# no message
#
# Revision 1.2  2005/12/14 02:50:57  phw
# no message
#
# Revision 1.1  2005/12/08 01:08:03  phw
# no message
#
#
