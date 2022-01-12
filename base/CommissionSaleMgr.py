# -*- coding: gb18030 -*-
#

import BigWorld
import cPickle
import ItemTypeEnum
import items
import time
import csstatus
from bwdebug import *
from Function import Functor

"""
��Ʒ�б��˳��(���ͣ��� �����ݿ��е�sm_type��Ӧ, see also ItemTypeEnum.py/CIST_*
"""

"""
������֣� custom_SaleOnCommission
���ݿ��м�����Ʒ�Ĵ洢��ʽ��

ע�� index �ǽ���ʱ���õ��Զ�������4�ֽڳ��ȣ������������ӵ���Ʒ,���ֵ��������
�����Զ����ɵġ�

type �� flag ��Ҫ�����ڿ��ٲ�ѯ

���ݿ��м�����Ʒ��״̬��4�֣�
	0���������루����ȡ������������Ҳ�ѯ���ݿ��ʱ��ֻ�ܲ鵽���״̬�µ���Ʒ����
	1����Ʒ����,û��֪ͨ����
	2���ɹ���������Ʒ
	3: �ɹ�ȡ����������Ʒ
"""

MAXLENGTH = 20			# һ�β�ѯ��Ʒ��Ŀ�ĳ���
QUERY_LIMIT_TIME = 10	# ��Ҳ�ѯ��Ϊ������ʱ��,��λΪs
COMMISSION_FAILURE_TIME = 60	# �����һ����ƷʱЧ��������ʱ��˵���������Ʒʧ��
QUERY_CLEAR_TIME = 60	# queryData�е����ݵı���ʱЧ
RUN_TIMER = 120			# ��ʱ���ݵ���������

g_item = items.instance()

class CommissionSaleMgr( BigWorld.Base ):
	"""
	����������
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )

		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "CommissionSaleMgr", self._onRegisterManager )

		# �����ݿ��д���������Ʒ��custom_SaleOnCommission
		self._createCommissionTable()

		self.mutexDict = {}	# ʵ����ҶԼ�����Ʒ���в���ʱ�Ļ���

		self.queryData = {}	# ��Ҳ�ѯ����ʱ���ݱ���{ "index":[owner,price,item,itemName,queryTime],�� }
		self.queryTime = {}	# ����������ҵĲ�ѯƵ��{ "playerName":queryTime, ��}

		self.addTimer( RUN_TIMER, RUN_TIMER )


	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register CommissionSaleMgr Fail!" )
			# again
			self.registerGlobally( "CommissionSaleMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["CommissionSaleMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("CommissionSaleMgr Create Complete!")


	def _createCommissionTable( self ):
		"""
		���ɱ�����custom_SaleOnCommission��񲻴��ڣ��򴴽������˱�ֻ����һ�Ρ�

		����ֶ����£�
		id : 		�Զ�����, ��Ʒ�����ݿ��е�����
		sm_owner : 	�����ߵ�����
		sm_price :	������Ʒ�ļ۸�
		sm_type  :	������Ʒ������
		sm_flag :	������Ʒ�����͸���
		sm_item	:	һ����Ʒ������
		sm_itemName:	��Ʒ���֣���ʵͨ��sm_item���Բ�ѯ����Ʒ�����֣������������Ҫ��Ϊ�˷�������
		sm_purchaser��	�������֣�������ʱ����һ���ǿյģ�ֻ����Ʒ�����߲Ű�������ֵ�������д��
		sm_commissionTime:	��Ʒ����ʱ��
		sm_endTradeTime:	��Ʒ�������ʱ��(��������ȡ������)
		sm_state:	������Ʒ״̬
		���ݿ��м�����Ʒ��״̬��4�֣�
			0���������루����ȡ������������Ҳ�ѯ���ݿ��ʱ��ֻ�ܲ鵽���״̬�µ���Ʒ����
			1����Ʒ����,û��֪ͨ����
			2���ɹ���������Ʒ
			3: �ɹ�ȡ����������Ʒ
		"""
		query  = "CREATE TABLE  IF NOT EXISTS `custom_SaleOnCommission` (`id` int(11) NOT NULL auto_increment, `sm_owner` varchar(45) default \" \", `sm_price` int(11) default 0, `sm_type` int(11) default 0,`sm_occupation` int(11) default 0,`sm_wieldType` int(11) default 0,`sm_item` blob default NULL,`sm_itemName` varchar(45) default \" \",`sm_purchaser` varchar(45) default \" \",`sm_commissionTime` datetime default NULL, `sm_endTradeTime` datetime default NULL, `sm_state` int(11) default 0,PRIMARY KEY  (`id`)) ENGINE=InnoDB;"
		BigWorld.executeRawDatabaseCommand( query, self._createCommissionTableCB )


	def _createCommissionTableCB( self, result, rows, errstr ):
		"""
		���ɱ��ص�����
		"""
		if errstr:
			# ���ɱ�����Ĵ���
			ERROR_MSG( "Create custom_Saleoncommission Fail!" )
			return


	def saleGoods( self, sellerName, price, item ):
		"""
		Define method.
		����һ����Ʒ����Ҽ���һ����Ʒʱ���ô˽ӿ�

		@param sellerName:	�����ߵ�����
		@type sellerName:	STRING
		@param price:	�����۸�
		@type price:	UINT32
		@param item:	��Ʒ
		@type item:		ITEM

		���̣�	1.���������ʱ����Ϣ������Ʒ���ݽ���ת��
				2.����Ʒ��Ϣд�����ϵͳ
		"""
		# itemType:��Ʒ������;occupation:������ְҵ����;wieldType:������˫������.
		itemType = item.getType()

		if itemType > 0 and itemType < 13:		# 1-12������
			occupation = item.query( "reqClasses" )
			wieldType = item.query( "eq_wieldType" )
		else:
			occupation = 0
			wieldType = 0

		itemName = item.query( "name" )

		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
		itemData = cPickle.dumps( tempDict, 2 )

		query = "insert into custom_SaleOnCommission ( sm_owner, sm_price, sm_type, sm_occupation, sm_wieldType, sm_item, sm_itemName, sm_commissionTime ) value ( \'%s\', %i, %i, %i, %i, \'%s\', \'%s\', now() );" \
					% ( BigWorld.escape_string( sellerName ), price, itemType, occupation, wieldType, itemData, itemName )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._saleGoodsCB, sellerName, price, item ) )


	def _saleGoodsCB( self, sellerName, price, item, result, dummy, errstr ):
		"""
		����һ����Ʒ�Ļص�����

		@param sellerName:	������
		@type sellerName:	STRING
		@param price:		�����۸�
		@type price:		INT32
		@param item:		��Ʒ
		@type item:			ITEM
		@param result��dummy��errstr: ��api�ĵ�
		"""
		if errstr:
			# д���ݿ�ʧ�ܣ�����Ʒ��Ϣд����־����ʱ��Ʒ�Ѿ�����ұ���ɾ��������cell�Ѿ�����һ�������Ĵ���
			itemData = repr( item.addToDict() )
			INFO_MSG( "error:%s vender an item. price of item: %i, item data: %s" % ( sellerName, price, itemData ) )
			return


	def buyGoods( self, index, moneyCount, playerBaseMailbox ):
		"""
		Define method.
		�����cell����һ��������Ʒ�ӿ�

		self.queryData�����ݽṹΪ��{ "index":[owner,price,item,queryTime],�� }

		@param index��		��Ʒ�����ݿ��е����
		@type index:		INT32
		@param moneyCount	������ӵ�еĽ����Ŀ
		@type moneyCount:	UINT32
		@param playerBaseMailbox:	��ҵ�mailbox
		@type playerBaseMailbox:	MAILBOX
		"""
		if not self.queryData.has_key( index ):		# ��Ʒ�Ѿ������ߣ����������Ѿ������
			return
		if self.mutexDict.has_key( index ):			# �Ѿ�����������
			playerBaseMailbox.client.onStatusMessage( csstatus.CMS_ITEM_HAS_BEEN_SELLED, "" )
			return
		else:
			self.mutexDict[index] = time.time()		# ��index���뻥���ֵ�
			# ������Ӧ��queryDataʱ�䣬���ⱻontimer��գ�����յ���Ʒ�����֪ͨ���ҵ����ݿ��Ը���index���ڴ��л�ã�������Ҫ�������Ĳ���
			self.queryData[index][4] = time.time()
		if int( self.queryData[index][1] ) > moneyCount:
			return

		sellerName = self.queryData[index][0]
		price = int( self.queryData[index][1] )
		itemDict = cPickle.loads( self.queryData[index][2] )
		itemDict["tmpExtra"] = cPickle.dumps( {}, 2 )
		item = g_item.createFromDict( itemDict )

		if hasattr( playerBaseMailbox, "cell" ) :	# ��ǰ���� CommissionSaleMgr ��Ӧ�� base�У�playerBaseMailbox�п��ܸո�����cell
			playerBaseMailbox.cell.cms_receiveSaleItem( sellerName, price, item, index )
		else:
			del self.mutexDict[ index ]


	def sendItemSuccess( self, buyerName, index ):
		"""
		Define method.
		����յ���Ʒ����ȷ�ϵĽӿ�

		@param buyerName:	��ҵ�����
		@type buyerName:	STRING
		@param sellerName:	���ҵ�����
		@type sellerName:	STRING
		@param itemName:	��Ʒ������
		@type itemName:		STRING
		@param price:		�����۸�
		@type price:		INT32
		@param index��		��Ʒ�����ݿ��е����
		@type index:		INT32
		"""
		query = "update custom_SaleOnCommission set sm_state = 1, sm_purchaser=\'%s\' where id = %i" % ( BigWorld.escape_string( buyerName ), index )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._sendItemSuccessCB, buyerName, index ) )


	def _sendItemSuccessCB( self, buyerName, index, resultSet, rows, errstr ):
		"""
		sendItemSuccess�Ļص�����
		"""
		if errstr:
			INFO_MSG( "error:updated sm_state to '1' failure,the index is %i." % ( index ) )
			return

		BigWorld.lookUpBaseByName( "Role", self.queryData[index][0], Functor( self._getPlayerMailboxCB, buyerName, index ) )


	def _getPlayerMailboxCB( self, buyerName, index, callResult ):
		"""
		ͨ���������ֲ���������������Ļص�����

		ǰ�����ͬ sendItemSuccess
		@param callResult:	BigWorld.lookUpBaseByName�Ĳ��ҽ��,mailbox��True��False���п���
		@type callResult:	MAILBOX OR BOOL
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			# ��Ǯ������
			if hasattr( callResult, "cell" ):	# ��ǰ���� CommissionSaleMgr ��Ӧ�� base�У�callResult�п��ܸո�����cell
				callResult.cell.cms_receiveMoney( int( self.queryData[index][1] ), self.queryData[index][3], buyerName, index )
		# �ߵ���һ����mutexDict��queryData�����ܵ�ʱЧ����onTimer���
		del self.mutexDict[ index ]
		del self.queryData[ index ]


	def sendMoneySuccess( self, index ):
		"""
		Define method.
		�����յ�Ǯ,֪ͨ�������Ľӿ�
		���������յ�Ǯʱ���ô˺���;���Ҳ�����,�ص�½�յ�Ǯʱ,Ҳ���ô˺���

		@param index��	��Ʒ�����ݿ��е����
		@type index:	INT32
		"""
		# �������,д״̬2
		query = "update custom_SaleOnCommission set sm_state = 2,sm_endTradeTime=now() where id = %i" % ( index )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._sendMoneySuccessCB, index ) )


	def _sendMoneySuccessCB( self, index, result, dummy, errstr ):
		"""
		sendMoneySuccess�Ļص�����
		"""
		if errstr:		# ������Ʒ״̬����,�����´����߻����յ�Ǯ
			INFO_MSG( "error:updated sm_state to '2' failure,the index is %i." % ( index ) )
			return


	def queryByType( self, param1, param2, param3, beginNum, callFlag, playerBaseMailbox, playerName ):
		"""
		Define method.

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
		@param callFlag : 		��ѯ������
		@type callFlag : 		INT8
		@param playerBaseMailbox:	���baseMailBox
		@type playerBaseMailbox:		MAILBOX
		@param playerName:		�������
		@type playerName:		STRING
		"""
		# ������ҵ����β�ѯʱ����������ڻ����QUERY_LIMIT_TIME
		if self.queryTime.has_key( playerName ):
			if time.time() - self.queryTime[playerName] < QUERY_LIMIT_TIME:
				return

		if callFlag == 1:
			query = "select id,sm_owner,sm_price,sm_item, sm_itemName from custom_SaleOnCommission where sm_type = %i and sm_state = 0 limit %i,%i"\
					 % ( int( param1 ), beginNum, MAXLENGTH )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )
			return
		if callFlag == 2:
			query = "select id,sm_owner,sm_price,sm_item, sm_itemName from custom_SaleOnCommission where sm_type = %i and ( sm_occupation & %i ) = sm_occupation and sm_state = 0 limit %i,%i"\
					 % ( int( param1 ), int( param2 ), beginNum, MAXLENGTH )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )
			return
		if callFlag == 3:
			query = "select id,sm_owner,sm_price,sm_item, sm_itemName from custom_SaleOnCommission where sm_type = %i and ( sm_occupation & %i ) = sm_occupation and ( sm_wieldType & %i ) = sm_wieldType and sm_state = 0 limit %i,%i"\
					 % ( int( param1 ), int( param2 ), int( param3 ), beginNum, MAXLENGTH )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )
			return


	def queryByItemName( self, itemName, beginNum, playerBaseMailbox, playerName ):
		"""
		Define method.

		����Ʒ���ֲ�ѯ���ݿ�Ľӿ�
		"""
		if self.queryTime.has_key( playerName ):
			if time.time() - self.queryTime[playerName] < QUERY_LIMIT_TIME:
				return

		query = "select id, sm_owner, sm_price, sm_item, sm_itemName from custom_SaleOnCommission where sm_itemName = \'%s\' and sm_state = 0 limit %i,%i"\
				 % ( itemName, beginNum, MAXLENGTH )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )


	def queryOwnGoods( self, beginNum, playerBaseMailbox, playerName ):
		"""
		Define method.

		��Ҳ�ѯ�Լ�������Ʒ�Ľӿ�
		"""
		if self.queryTime.has_key( playerName ):
			if time.time() - self.queryTime[playerName] < QUERY_LIMIT_TIME:
				return

		query = "select id, sm_owner, sm_price, sm_item, sm_itemName from custom_SaleOnCommission where sm_owner = \'%s\' and sm_state = 0 limit %i,%i"\
					 % ( BigWorld.escape_string( playerName ), beginNum, MAXLENGTH )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryOwnGoodsCB,  playerBaseMailbox, playerName ) )


	def _queryGoodsCB( self, playerBaseMailbox, playerName, resultSet, rows, errstr ):
		"""
		��ѯ������Ʒ�Ļص�����

		"""
		if errstr:		# ��ѯ����,�޴���
			INFO_MSG( errstr )
			return
		if rows == 0:	# û�в鵽�κ�����
			return

		self.queryTime[playerName] = time.time()
		for tempGoods in resultSet:			# queryData�����ݽṹΪ{ "index":[owner,price,item,itemName,queryTime],�� }
			itemName = tempGoods.pop( 4 )	# �ͻ��˲���Ҫ�����ݣ����ٴ�����
			playerBaseMailbox.client.cms_receiveQueryInfo( tempGoods )
			tempGoods.append( itemName )	# ���°�itemName����
			tempGoods.append( time.time() )
			self.queryData[ int( tempGoods[0] ) ] = tempGoods[1:]


	def _queryOwnGoodsCB( self, playerBaseMailbox, playerName, resultSet, rows, errstr ):
		"""
		��ѯ�Լ�������Ʒ�Ļص�����
		"""
		if errstr:		# ��ѯ����,�޴���
			INFO_MSG( errstr )
			return
		if rows == 0:	# û�в鵽�κ�����
			return
		self.queryTime[playerName] = time.time()
		for tempGoods in resultSet:
			itemName = tempGoods.pop( 4 )	# �ͻ��˲���Ҫ�����ݣ����ٴ�����
			playerBaseMailbox.client.cms_receiveOwnGoodsInfo( tempGoods )
			tempGoods.append( itemName )	# ���°�itemName����
			tempGoods.append( time.time() )
			# queryData�����ݽṹΪ{ "index":[owner,price,item,itemName,queryTime],�� }
			self.queryData[ int( tempGoods[0] ) ] = tempGoods[1:]


	def queryForLogin( self, playerBaseMailbox, playerName ):
		"""
		Define method.
		�������ʱ��ѯ�Լ��ļ�����Ϣ

		@param playerName:	��ѯ��ҵ�����
		@type playerName:	STRING
		@param playerBaseMailbox:	��ҵ�mailbox
		@type playerBaseMailbox:	MAILBOX
		"""
		query = "select id, sm_price,sm_purchaser,sm_itemName from custom_SaleOnCommission where sm_owner=\'%s\' and sm_state = 1 " \
				% ( BigWorld.escape_string( playerName ) )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryForLoginCB, playerBaseMailbox ) )


	def _queryForLoginCB( self, playerBaseMailbox, resultSet, rows, errstr ):
		"""
		queryForLogin�Ķ�ȡ���ݿ�Ļص�����
		������������ߺ󣬲�ѯ�м������������˵���Ʒ����Ϣ�����û�У��ͷ��أ�����У�����ź�������

		@param playerBaseMailbox:	����base
		@type playerBaseMailbox:	MAILBOX
		@param playerName:	��ѯ��ҵ�����
		@type playerName:	STRING
		"""
		if errstr:
			INFO_MSG( errstr )
			return
		if rows == 0:
			return

		for temp in resultSet:
			if hasattr( playerBaseMailbox, "cell" ) :	#��ǰ���� CommissionSaleMgr ��Ӧ�� base�У�  playerBaseMailbox�п��ܸո�����cell
				playerBaseMailbox.cell.cms_receiveMoney( int( temp[1] ), temp[3], temp[2], int( temp[0] ) )


	def cancelSaleGoods( self, index, playerBaseMailbox, playerName ):
		"""
		Define method.
		���ȡ������

		@param index:	��Ʒ�����ݿ��е�����
		@type index:	INT32
		@param playerBaseMailbox:	��ҵ�mailbox
		@type playerBaseMailbox:	MAILBOX
		@param playerName:	�������
		@type playerName:	STRING
		"""
		if not self.queryData.has_key( index ):		# ��Ʒ�Ѿ������ߣ����������Ѿ����Զ����
			playerBaseMailbox.client.onStatusMessage( csstatus.CMS_QUERY_AGAIN, "" )
			return
		if self.mutexDict.has_key( index ):			# �Ѿ�����������
			playerBaseMailbox.client.onStatusMessage( csstatus.CMS_ITEM_HAS_BEEN_SELLED, "" )
			return
		else:
			self.mutexDict[index] = time.time()		# ��index���뻥���ֵ�
			self.queryData[index][4] = time.time()	# ������Ӧ���ݵ�ʱ�䣬���ⱻ���

		if self.queryData[index][0] != playerName: #����ȡ�����˼��� ��Ʒ��Ԥ�����ף�������ʾ
			return

		itemDict = cPickle.loads( self.queryData[index][2] )
		itemDict["tmpExtra"] = cPickle.dumps( {}, 2 )
		item = g_item.createFromDict( itemDict )

		playerBaseMailbox.cell.cms_receiveCancelItem( item, index )


	def cancelSuccess( self, index ):
		"""
		Define method.
		�ɹ�ȡ������,���֪ͨ�����������Ľӿ�
		@param index:	������Ʒ�����ݿ�����
		@type index:	INT32
		"""
		query = "update custom_SaleOnCommission set sm_state = 3,sm_endTradeTime = now() where id = %i" %( index )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._cancelSuccessCB, index ) )


	def _cancelSuccessCB( self, index, result, dummy, errstr ):
		"""
		cancelSuccess�Ļص�����

		@param index:	������Ʒ�����ݿ�����
		@type index:	INT32
		"""
		if errstr:
			INFO_MSG( "error:updated sm_state to '3' failure when '_cancelSuccessCB',the index is %i." % ( index ) )
			return
		# �ߵ���һ����mutexDict��queryData�����ܵ�ʱЧ����ontimer���
		del self.mutexDict[ index ]
		del self.queryData[ index ]


	def onTimer( self, id, userArg ):
		"""
		Timer
		"""
		# ������mutexDict
		for temp in self.mutexDict:
			if temp is not None and time.time() - self.mutexDict[temp] > COMMISSION_FAILURE_TIME:
				del self.mutexDict[temp]

		for temp in self.queryData:
			if temp is not None and time.time() - self.queryData[temp][4] > QUERY_CLEAR_TIME:
				del self.queryData[temp]

		for temp in self.queryTime:
			if temp is not None and time.time() - self.queryTime[temp] > QUERY_LIMIT_TIME:
				del self.queryTime[temp]



