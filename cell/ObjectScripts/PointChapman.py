# -*- coding: gb18030 -*-
#
# 2009-01-12 SongPeifang
#

"""
�˽ű����Բ���Ҫ�ˣ��������л����õ�����ʱ�����������ø�����ɾ����12:00 2010-2-26��wsf
"""

from Chapman import Chapman
import csdefine

class PointChapman( Chapman ):
	"""
	����������һ�����������
	�������˳��۵���Ʒ��������Ǯ�򣬶����������������ȡ��
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
