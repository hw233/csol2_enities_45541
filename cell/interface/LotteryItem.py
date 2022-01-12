# -*- coding: gb18030 -*-
#
# $Id: LotteryItem.py

import items
import random
import csconst
import csdefine
import ECBExtend
import ItemTypeEnum
import Const
from bwdebug import *
from MsgLogger import g_logger
import sys

#����
from items.ItemDropLoader import ItemDropLotteryLoader
from items.EquipEffectLoader import EquipEffectLoader

g_itemDropLotteryLoader = ItemDropLotteryLoader.instance()
g_items = items.instance()

class LotteryItem:
	"""
	����ϵͳ����ش��룬�ⲿ�ִ���û��д����Ʒ�е�ԭ���ǣ������ڳ����Ʒ����Ҫ�д洢��ص����ݵ��������ϣ�
	��������;���ߺ���Ʒ��Ҫ���洢�����ݿ��У��������һ�����ߺ󲹳��������ϡ�
	"""
	def __init__( self ):
		self.__ItemDropAmount = [ [0, 1 ], [0, 1 ], [0, 3 ], [0, 5], [0, 7], [0, 50], [0, 1] ]	#��¼����ĸ��ȼ�����Ʒ�б�
							#tuple��һ��ֵ��ʾʵ��������ĸõȼ�����Ʒ�������ڶ���ֵ��ʾ����������ĸõȼ���Ʒ������

	def onRoleOff( self ):
		"""
		������ߣ��鿴�Ƿ�����Ʒû����ȡ
		"""
		if self.havelotteryItem():
			self.addlotteryItem()

	def onlottery( self, lotteryUid ):
		"""
		��ʼ�����Ʒ�����洢
		"""
		self.clearlottery()
		self.lotterytimes += 1
		self.lotteryUid = lotteryUid				#��¼���ҵ�λ��
		itemIDs = []
		if self.lotterytimes != 50:
			factitemIDs    = self.getDrops( 2, True   ) #ʹ����ʵ�������������Ʒ
			falsityitemIDs = self.getDrops( 10, False ) #ʹ����ʾ�������ʮ����Ʒ
			itemIDs = factitemIDs + falsityitemIDs
		else:											#ÿ50��ʹ����ʾ�������ȫ����Ʒһ��
			itemIDs = self.getDrops( 12, False ) 		#ʹ����ʾ�������ʮ����Ʒ
			self.lotterytimes = 0

		for index in xrange( len( itemIDs ) ):
			item = None
			if itemIDs[ index ][0] == "equip":
				level =  self.getLevel()
				level += random.randint( -5, 5 )
				level = max( 1, level )
				level = min( csconst.ROLE_LEVEL_UPPER_LIMIT, level )
				itemInfo = g_itemDropLotteryLoader.getEquipDropInfo( level )
				if not itemInfo:
					try:
						g_logger.lotteryExceptLog("error", "CLottery Item getEquipDropInfo failed, equip level(%s)" % level )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					self.clearlottery()
					return
				itemID, quality, prefix, odds = itemInfo
				item = g_items.createDynamicItem( int( itemID ) , 1 )
				if quality != 0 and prefix != 0:		#��дװ������Ҫ����Ʒ�ʺ�ǰ׺
					item.setQuality( quality )
					item.setPrefix( prefix )
					if not item.createRandomEffect():
						try:
							g_logger.lotteryExceptLog( "error","CLottery Item CreatEquip Failed, createRandomEffect failed,item_id(%s),quality(%s),prefix(%s),odds(%s)" % (itemID, quality, prefix, odds) )
						except:
							g_logger.logExceptLog( GET_ERROR_MSG() )
						self.clearlottery()
						return
			else:
				item = g_items.createDynamicItem( int( itemIDs[ index ][0] ), itemIDs[index][1] )
				if not item:
					try:
						g_logger.lotteryExceptLog( "error", "Create Item Failed, itemID(%s), amount(%s)" % ( itemIDs[ index ][0], itemIDs[index][1] )  )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					self.clearlottery()
					return
			self.AllLotteryItems.append( item )

		finallyPosA = 0								#Ĭ�ϵĿ�ʼʱ������Ʒ��λ��
		finallyPosB = 1

		insertPosA = random.randint( 0, 11 )		#���򲹵���Ʒ������뵽�б�ĺ���λ����
		if insertPosA != finallyPosA:
			temp = self.AllLotteryItems[ insertPosA ]
			self.AllLotteryItems[ insertPosA ] = self.AllLotteryItems[ finallyPosA ]
			self.AllLotteryItems[ finallyPosA ] = temp
			if insertPosA == finallyPosB:
				finallyPosB = finallyPosA
			finallyPosA = insertPosA

		insertPosB = random.randint( 0, 11 )		#���򲹵���Ʒ������뵽�б�ĺ���λ����
		if insertPosB != finallyPosB:
			temp = self.AllLotteryItems[ insertPosB ]
			self.AllLotteryItems[ insertPosB ] = self.AllLotteryItems[ finallyPosB ]
			self.AllLotteryItems[ finallyPosB ] = temp
			if insertPosB == finallyPosA:				#���������B��Ʒ��λ����A��Ʒ���ڵ�λ��
				finallyPosA = finallyPosB				#��ôA��Ʒ�ͱ��滻����1��λ�� ����A��Ʒ������λ��
			finallyPosB = insertPosB


		self.lotteryItem = self.AllLotteryItems[ finallyPosA ]	#��¼��Ĭ�ϸ���ҵ���Ʒ
		if not self.lotteryItem or len( self.AllLotteryItems) != 12 or not self.AllLotteryItems[ finallyPosB ]:
			try:
				g_logger.lotteryExceptLog( "error", "lotteryItem is none: finallyPosA = %s,finallyPosB = %s, self.AllLotteryItems = %s " \
				% ( finallyPosA,finallyPosB,self.AllLotteryItems ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			self.clearlottery()
			return

		self.setTemp( "lotterydefaultIndex", finallyPosA )		#��¼����ƷA��λ��
		self.setTemp( "lotteryAlternateIndex", finallyPosB )	#��¼����ƷB��λ��
		self.setTemp( "sendlotteryindex" , 0 )					#��¼��ͻ��˷�����Ʒ��������ʼλ��
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.SHOW_LOTTER_ITEMS )	#��ͻ��˷�������
		self.client.showlotteryWindow()							#�����ʾ����
		self.lotteryState = True								#�ߵ�����˵���˴ο����ɹ������ý���״̬Ϊ������.

	def showLotterItems( self, timerID, cbid ):
		"""
		��ͻ��˷�����Ʒ������ һ��4�� �ܹ�12��
		"""
		begin = self.queryTempInt( "sendlotteryindex" )	#��ȡ���͵Ŀ�ʼλ��
		AllItem = len( self.AllLotteryItems )
		end   = min( AllItem, begin + Const.LT_SENDNUM )	#���㷢�͵���ֹλ��

		if begin < AllItem:
			self.addTempInt( "sendlotteryindex", Const.LT_SENDNUM )
		else: #����Ƿ������һ�� ��ô��������� ������Ʒ��λ�÷��͸��ͻ���
			AIndex = self.queryTempInt( "lotterydefaultIndex" )
			BIndex = self.queryTempInt( "lotteryAlternateIndex" )
			self.client.lotteryABIndex( AIndex, BIndex )	#֪ͨ�ͻ���������Ʒ��λ��(ʵ����ֻ��A��B���ܻᱻ��ҵõ�)
			self.removeTemp( "sendlotteryindex" )
			self.cancel( timerID )

		for index in xrange(begin, end):
			item = self.AllLotteryItems[ index ]
			self.client.updateLotterItems( item, index )

	def getPerhapsDropID( self, fact):
		"""
		���ݵ��ʵ����ͣ��������п��ܵ������ƷID
		@type  fact        : bool
		@param fact        : �Ƿ�����ʵ����������( ���Ҽ�¼�����׵���,һ��ʵ�ʵ�,һ����ٵ� )
		@return type       : string
		@return parame     : �����п��ܵ������ƷID��װ����һ���������,�����װ������Ҫ�����������ȥ���ң�
		"""
		odds = "fact_odds"
		if not fact:
			odds = "falsity_odds"

		randomValue = g_itemDropLotteryLoader.randomValue( fact )
		datas = g_itemDropLotteryLoader.getDropDatas()

		while 1:
			for data in datas:
				level = data["itemLevel"]
				factNum = self.__ItemDropAmount[level - 1 ][0 ]
				maxNum  = self.__ItemDropAmount[level - 1 ][1 ]
				if randomValue <= data[ odds ] and ( factNum < maxNum or fact ):
				#������ĵ���С�ڸ���Ʒ�ĵ��ʲ��ҵ�ǰ�õȼ�����Ʒ����������Ӧ����������������޻���ʹ�õ�����ʵ����
					self.__ItemDropAmount[level - 1 ][0 ] += 1	#���Ӽ���
					return ( data["id"],data["amount"] )
			randomValue = g_itemDropLotteryLoader.randomValue( fact, randomValue )	#�ٴ����һ����Ʒ�����ʵ���������һ�ε���

		DEBUG_MSG( "ItemDropLotteryLoader::getPerhapsDrop no item accord with claim " )
		return (0,0)


	def getDrops( self, amount, fact ):
		"""
		��ȡָ�������ĵ������ƷID
		@type  amount : int
		@param amount : ָ���ĵ��������
		@type  fact   : bool
		@param fact   : �����Ƿ�ʹ����ʵ�ĵ���
		"""
		itemIDs = []
		for i in xrange( amount ):
			id,amount = self.getPerhapsDropID( fact )
			itemIDs.append( ( id, amount ) )
		return itemIDs

	def setlotteryItem( self, Item ):
		"""
		���ý��ҳ������Ʒ
		"""
		self.lotteryItem = Item

	def changelotteryItem( self, srcEntityID ):
		"""
		����ǰ�������Ʒ�����ɺ���Ʒ���ö��������棩
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			self.lotteryState = False
			self.clearlottery()	#�����ԭ��������
			return
		AlternateIndex = self.queryTempInt( "lotteryAlternateIndex" )
		self.removeTemp( "lotteryAlternateIndex" )
		self.lotteryItem = self.AllLotteryItems[AlternateIndex]

	def getlotteryItem( self, srcEntityID ):
		"""
		����Ʒ���������
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			self.lotteryState = False
			self.clearlottery()	#�����ԭ��������
			return
		self.addlotteryItem()

	def addlotteryItem( self ):
		"""
		����Ʒ�ӵ���ұ���
		"""
		self.lotteryState = False
		if not self.lotteryItem:
			self.clearlottery()
			return
		item = self.getItemByUid_( self.lotteryUid )
		if item is None:
			self.clearlottery()
			return
		item.unfreeze()
		item.onSpellOver( self )
		if self.lotteryItem.id == 60101001: #�����Ʒ�ǽ�Ǯ
			self.gainMoney( self.lotteryItem.getAmount(), csdefine.CHANGE_MONEY_LOTTERYITEM )
		else:
			if item.isBinded():	# ������ɫ���񣬽��ҿ��ﲻǿ�ư� by ����
				self.lotteryItem.setBindType( ItemTypeEnum.CBT_PICKUP, self )
			self.addItemAndRadio( self.lotteryItem, ItemTypeEnum.ITEM_GET_CARD, reason =  csdefine.ADD_ITEM_ADDLOTTERYITEM )
		self.clearlottery()

	def havelotteryItem( self ):
		"""
		�ж�����Ƿ��н��ҽ���û����ȡ
		"""
		return self.lotteryState

	def clearlottery( self ):
		"""
		������ҵ�����
		"""
		self.lotteryItem = None
		self.lotteryUid = 0
		self.AllLotteryItems = []
		self.__ItemDropAmount = [ [0, 1 ], [0, 1 ], [0, 3 ], [0, 5], [0, 7], [0, 50], [0, 1] ]	#��¼����ĸ��ȼ�����Ʒ�б�
