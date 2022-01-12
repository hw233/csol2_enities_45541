# -*- coding: gb18030 -*-
#
# $Id: QuickBar.py,v 1.13 2008-07-21 02:40:10 huangyongwei Exp $

"""
implement quickbar

2006/09/07 : rewriten by huangyongwei
"""

import csdefine
import csconst
import ECBExtend
import Const
from QuickBarItemData import QuickBarItemData


class QuickBar:
	def __init__( self ):
		self.__dictQBItems = {}
		for item in self.qbItems :
			self.__dictQBItems[item.index] = item
		self.__tmpInitIndex = 0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def qb_initializeOnCreateRole( self, roleClass ):
		"""
		��ɫ���������ʼ�������
		"""
		qbInitDataInfo = Const.ROLE_INIT_QUICKBAR_DATA[ roleClass ]

		for index, itemInfo in qbInitDataInfo.iteritems():
			qbData = QuickBarItemData()
			qbData.index = index
			qbData.qbtype = itemInfo[ 0 ]
			qbData.narg1 = itemInfo[ 1 ]
			qbData.sarg2 = itemInfo[ 2 ]
			self.__dictQBItems[ index ] = qbData
			self.qbItems.append( qbData )

	def qb_updateClient( self ) :
		"""
		requested by client to initialize quickbar
		"""
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_QB_CBID )

	def onTimer_qb_updateClient( self, timerID, cbID ) :
		"""
		���¿����
		"""
		maxIndex = min( len( self.qbItems ),  self.__tmpInitIndex + 10 )					# ÿ�γ�ʼ�� 10 ������
		for self.__tmpInitIndex in xrange( self.__tmpInitIndex, maxIndex ) :
			item = self.qbItems[self.__tmpInitIndex]
			self.client.qb_onUpdateItem( item.index, item.qbtype, item.narg1, item.sarg2 )
		self.__tmpInitIndex += 1
		if self.__tmpInitIndex >= len( self.qbItems ) :										# ��ʼ����Ϻ�ɾ�� timer
			self.delTimer( timerID )
			self.client.onInitialized( csdefine.ROLE_INIT_QUICK_BAR )						# ����֪�ͻ��˳�ʼ�������ʼ�����


	# ----------------------------------------------------------------
	# called by client
	# ----------------------------------------------------------------
	def qb_updateItem( self, index, qbtype, narg1, sarg2 ):
		""" <Exposed>
		requested by client to update an quick item
		@type				index	: int
		@param				index	: quickbar item index
		@type				qbType	: int
		@param				qbType	: type of the quickbar item ( defined in csdefine )
		@type				narg1	: int
		@param				narg1	: the integer argument to specify quick item
		@type				sarg2	: str
		@param				sarg2	: the string argument to specify quick item
		@return						: None
		"""
		if index < 0 : return
		if index >= csconst.QB_ITEMS_COUNT : return				# �����ݸ�����������Χ
		if self.__dictQBItems.has_key( index ) :				# �����ݸ��Ѿ�����
			item = self.__dictQBItems[index]					# ����ȡ���ڵĿ�ݸ����Ը��£�
		else :													# ����
			item = QuickBarItemData()							# ���´���һ��
			self.qbItems.append( item )							# ��ӵ�����б���
			self.__dictQBItems[index] = item
		item.index = index										# ���¿�ݸ������
		item.qbtype = qbtype
		item.narg1 = narg1
		item.sarg2 = sarg2

	def qb_exchangeItem( self, srcIndex, dstIndex ) :
		""" <Exposed>
		swap two items
		@type				srcIndex : int
		@param				srcIndex : source index
		@type				dstIndex : int
		@param				dstIndex : destination
		@retrun 					 : None
		"""
		if srcIndex == dstIndex : return
		if srcIndex < 0 : return
		if dstIndex < 0 : return
		if srcIndex >= csconst.QB_ITEMS_COUNT : return
		if dstIndex >= csconst.QB_ITEMS_COUNT : return

		if self.__dictQBItems.has_key( srcIndex ) :
			srcItem = self.__dictQBItems.pop( srcIndex )
			if self.__dictQBItems.has_key( dstIndex ) :
				self.__dictQBItems[srcIndex] = self.__dictQBItems[dstIndex]
				self.__dictQBItems[srcIndex].index = srcIndex
			self.__dictQBItems[dstIndex] = srcItem
			self.__dictQBItems[dstIndex].index = dstIndex

	def qb_removeItem( self, index ):
		""" <Exposed>
		remove an item
		@type				index : int
		@param				index : index of the item you want to remove
		@retrun 				  : None
		"""
		if index < 0 : return
		if index >= csconst.QB_ITEMS_COUNT : return
		if self.__dictQBItems.has_key( index ) :
			item = self.__dictQBItems.pop( index )
			self.qbItems.remove( item )


# --------------------------------------------------------------------
#
# $Log: not supported by cvs2svn $
# Revision 1.12  2008/07/15 09:09:28  fangpengjun
# csconst.QB_PET_SPELL_INDEX -> csdefine.QB_PET_SPELL_INDEX
#
# Revision 1.11  2008/06/17 06:18:37  wangshufeng
# ���������������
#
# Revision 1.10  2008/06/10 08:57:51  huangyongwei
# ���ͻ��˿�����ĳ�ʼ���ְ�����
#
# Revision 1.9  2008/01/31 10:57:56  huangyongwei
# no message
#
# Revision 1.8  2007/06/14 09:19:02  huangyongwei
# ԭ���ĺ궨������ L3Define �б��Ƶ� csconst �У����Ҫ���� import ��
#
# Revision 1.7  2007/05/17 09:06:10  huangyongwei
# ȥ���������������ʼ������Ϊ�ͻ��������ʼ��
#
# Revision 1.6  2007/05/15 04:01:08  huangyongwei
# �� client �� onAddQBItem ����Ϊ onUpdateQBItem
#
# Revision 1.5  2006/09/19 08:43:26  huangyongwei
# �޸��˽�����ݸ񲿷ִ���
#
# Revision 1.4  2006/09/09 01:31:36  huangyongwei
# ����� exchangeQBItem �����������������֮��Ľ���
#
# Revision 1.3  2005/12/23 06:25:44  wanhaipeng
# QuickBar.sendQBToClient while onClientGetCell.
#
# Revision 1.2  2005/12/23 04:26:02  wanhaipeng
# Min index is 0 not 1.
#
# Revision 1.1  2005/12/23 03:32:14  wanhaipeng
# Add QuickBar.
#
# --------------------------------------------------------------------