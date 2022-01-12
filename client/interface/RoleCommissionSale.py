# -*- coding: gb18030 -*-



MONEY_CHECK = 1		# checkAndNotify�����������money�ı�־
import GUIFacade
import items
import cPickle
import csdefine

g_item = items.instance()	# ���ڿͻ��˰Ѽ��������������������ݻ�ԭ��һ��item

class RoleCommissionSale:
	"""
	��Ҽ���ϵͳ�ͻ��˽ӿ�
	"""

	def __init__( self ):
		"""
		"""
		pass

	def cms_enterTrade( self ):
		"""
		Define method.

		�ṩ�����cell�򿪿ͻ��˼�������Ľӿ�
		"""
		pass	# ������ʱ������


	def cms_saleGoods( self, price, uid, entityID ):
		"""
		����һ����Ʒ

		@param price��	�����ļ۸�
		@type price:	UINT32
		@param uid:	��Ʒ���ڱ�����
		@type uid:	INT64
		@param amount:	������Ʒ������
		@type amount:	INT16
		@param entityID:����npc��id
		@type entityID:	OBJECT_ID
		"""
		self.cell.cms_saleGoods( price, uid, entityID )


	def cms_buyGoods( self, index, entityID ):
		"""
		����һ��������Ʒ

		@param index:	������Ʒ�����ݿ��е����
		@type index:	INT32
		@param entityID:npcID
		@type entityID:	OBJECT_ID
		"""
		self.cell.cms_buyGoods( index, entityID )


	def cms_receiveQueryInfo( self, tempList ):
		"""
		define method
		���ز�ѯ���

		tempList�����ݽṹΪ[index��owner��price��item]
		@param tempList:	��Ʒ�����б�
		@type tempList:		ARRAY of STRING
		"""
		# �����ݷ��͸�����wsf
		print tempList


	def cms_receiveOwnGoodsInfo( self, tempList ):
		"""
		Define method.
		���ղ�ѯ�Լ�������Ʒ���ݵĿͻ��˽ӿ�

		tempList�����ݽṹΪ[index��owner��price��item]
		@param goodsList:	��Ʒ�����б�
		@type goodsList:	ARRAY of STRING
		"""
		# �����ݷ��͸�����wsf
		print tempList


	def cms_queryByType( self, param1, param2, param3, beginNum, callFlag, entityID ):
		"""
		����Ʒ���Ͳ�ѯ,Ϊ����Ӧ����������Ʒ��3���ѯ(����߻��ĵ�),������param1,param2,param3��3������,��3�������Ľ�����callFlag����.
		��callFlagΪ1ʱ,param1Ϊ��Ʒ����,param2Ϊ0,param3Ϊ0,��ʱ�ǰ���Ʒ���Ͳ�ѯ;
		��callFlagΪ2ʱ,˵���ǲ�ѯ�������͵���Ʒ->����������ְҵ,param1Ϊ��Ʒ����,param2Ϊ������ְҵ,param3Ϊ0;
		��callFlagΪ3ʱ,˵���ǲ�ѯ�������͵���Ʒ->����������ְҵ->�����ĵ�˫������,param1Ϊ�������param2Ϊ������ְҵ,param3Ϊ�����ĵ�˫������
		����ѯ�Ĳ����������͵���Ʒʱ,�����õ�param1,��Ϊ������Ʒû������������Ʒ�Ĳ�ѯ���.

		@param param1,param2,param3: ����callFlag����������3������������
		@type param1: 		STRING
		@type param2:		STRING
		@type param3:		STRING
		@param beginNum : 	��ѯ��Ʒ�Ŀ�ʼλ��
		@type biginNum:		INT32
		@param call : 		��ѯ������
		@type call : 		INT8
		@param traderID:	����npc��id
		@type traderID:		INT32
		"""
		self.cell.cms_queryByType( param1, param2, param3, beginNum, callFlag, entityID )


	def cms_queryByItemName( self, itemName, beginNum, entityID ):
		"""
		����Ʒ���ֲ�ѯ�Ŀͻ��˽ӿ�

		@type itemName:		��Ʒ����
		@type itemName:		STRING
		@param beginNum : 	��ѯ��Ʒ�Ŀ�ʼλ��
		@type biginNum:		INT32
		@param entityID:	����npc��id
		@type entityID:		INT32
		"""
		self.cell.cms_queryByItemName( itemName, beginNum, entityID )


	def cms_queryOwnGoods( self, beginNum, entityID ):
		"""
		��ѯ�Լ�������Ʒ�Ľӿڣ��ڼ��������������۵��ߡ���ת����۵��ߴ���ͬʱ�����ݿ����Լ���������Ʒ

		���������cms_queryByItemName
		"""
		self.cell.cms_queryOwnGoods( beginNum, entityID )


	def cms_cancelSaleGoods( self, index, entityID ):
		"""
		ȡ��һ��������Ʒ

		@param index:	������Ʒ�����ݿ��е����
		@type index:	INT32
		@param entityID:	����npc��id
		@type entityID:		INT32
		"""
		self.cell.cms_cancelSaleGoods( index, entityID )