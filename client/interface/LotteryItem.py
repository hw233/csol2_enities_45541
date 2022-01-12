# -*- coding: gb18030 -*-
#
# $Id: LotteryItem.py

import event.EventCenter as ECenter
from ItemsFactory import ObjectItem as ItemInfo

class LotteryItem:
	"""
	����ϵͳ����ش��룬�ⲿ�ִ���û��д����Ʒ�е�ԭ���ǣ������ڳ����Ʒ����Ҫ�д洢��ص����ݵ��������ϣ�
	��������;���ߺ���Ʒ��Ҫ���洢�����ݿ��У��������һ�����ߺ󲹳��������ϡ�
	"""
	def __init__( self ):
		pass

	def updateLotterItems( self, item, order ):
		"""
		��ȡ���������͹����Ľ��ҵ�����
		"""
		self.lotteryItems[order] =  item
		itemInfo = ItemInfo( self.lotteryItems[order] )
		ECenter.fireEvent( "EVT_ON_LOTTERY_UPDATAITEM", itemInfo, order)

	def lotteryGetItem( self ):
		"""
		֪ͨ������Ҫȡ������
		"""
		if not self.lotteryItems:
			return
		self.cell.getlotteryItem()	#֪ͨ�������Ѷ����ŵ��ұ�����
		self.lotteryItems = {}

	def changelotteryItem( self ):
		"""
		֪ͨ���������ѡ�����ٴγ�ȡ
		"""
		if not self.lotteryItems:
			return
		self.cell.changelotteryItem()

	def lotteryABIndex( self, indexA, indexB ):
		"""
		��¼2����Ʒ��λ�� ����ת��Ļ�õ���Ʒ��λ��
		"""
		ECenter.fireEvent( "EVT_ON_LOTTERY_UPDATAPOS", indexA, indexB )		#֪ͨ����洢����Ʒ��λ��

	def showlotteryWindow( self ):
		ECenter.fireEvent( "EVT_ON_SHOW_LOTTERYWINDOW")