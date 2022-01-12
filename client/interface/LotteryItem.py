# -*- coding: gb18030 -*-
#
# $Id: LotteryItem.py

import event.EventCenter as ECenter
from ItemsFactory import ObjectItem as ItemInfo

class LotteryItem:
	"""
	锦囊系统的相关代码，这部分代码没有写到物品中的原因是，锦囊在抽出物品后，需要有存储相关的数据到人物身上，
	在人物中途下线后，物品需要被存储到数据库中，在玩家下一次上线后补充带玩家身上。
	"""
	def __init__( self ):
		pass

	def updateLotterItems( self, item, order ):
		"""
		获取服务器发送过来的锦囊的数据
		"""
		self.lotteryItems[order] =  item
		itemInfo = ItemInfo( self.lotteryItems[order] )
		ECenter.fireEvent( "EVT_ON_LOTTERY_UPDATAITEM", itemInfo, order)

	def lotteryGetItem( self ):
		"""
		通知服务器要取东西了
		"""
		if not self.lotteryItems:
			return
		self.cell.getlotteryItem()	#通知服务器把东西放到我背包里
		self.lotteryItems = {}

	def changelotteryItem( self ):
		"""
		通知服务器玩家选择了再次抽取
		"""
		if not self.lotteryItems:
			return
		self.cell.changelotteryItem()

	def lotteryABIndex( self, indexA, indexB ):
		"""
		记录2号物品的位置 即旋转后的获得的物品的位置
		"""
		ECenter.fireEvent( "EVT_ON_LOTTERY_UPDATAPOS", indexA, indexB )		#通知界面存储候补物品的位置

	def showlotteryWindow( self ):
		ECenter.fireEvent( "EVT_ON_SHOW_LOTTERYWINDOW")