# -*- coding: gb18030 -*-
#
# 2009-01-12 SongPeifang
#

"""
�˽ű��ѿ���ɾ����������NPCMonster�����л�����ʹ����ItemChapman����ʱ�����������ø�����ɾ����9:06 2010-2-23��wsf
"""

from Chapman import Chapman
import csdefine
from bwdebug import *

class ItemChapman( Chapman ):
	"""
	����������һ�����������
	�������˳��۵���Ʒ��������Ǯ�򣬶�������Ʒ����ȡ��
	"""
	def __init__( self ):
		"""
		"""
		Chapman.__init__( self )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		����ĳ��Ʒ�¼�
		"""
		playerEntity.buyFromNPC( selfEntity, newInvoice, argIndex, argAmount )

	def onSellItems( self, selfEntity, playerEntity, invoiceItems, argIndices, argAmountList ):
		"""
		����ĳ����Ʒ�¼�
		"""
		playerEntity.buyArrayFromNPC( selfEntity, invoiceItems, argIndices, argAmountList )
