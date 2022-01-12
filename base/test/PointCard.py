# -*- coding: gb18030 -*-

"""
�㿨����base���Խű�
���Թ��ܣ�
	base/PointCardMgr.py
		class PointCardMgr

"""

#ע�⣬���ɫ�йصĲ��ԣ�����һЩͨ���ӿڵ��õķ���������ȫ����ͨ��client�������ԣ�������base���ԣ��ص㽫�������౾�����ϡ�


from PointCardInfo import PointCardInfo
import BigWorld
from Function import newUID
from Function import Functor
import csdefine
import time
import csconst

def newOrderID():
	"""
	"""
	id = str(newUID())
	for i in xrange( 0, 20 - len( id ) ):
		id = '0'+id
	return id

#���ڲ��ԵĿ���Ϣ
cardsInfo = {	0:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000154587797",	"passWord"		: "ABC",
					"orderID"		: newOrderID(),				"serverName"	: "����֮��",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "���ſ��ʺź����벻��",
					"buyerMailTitle": "����ʧ��",				"buyerMailContent" : "����ĵ㿨��Ϣ�����Ѿ��¼ܣ����ʼ��������ν��׷��ã���ȡ�ء�",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "���۵㿨ʧ��",			"sellerMailContent" : "����۵ĵ㿨(����:HAAAB000000154587797)�ʺź����������Ѿ��¼ܣ�Ѻ��û�ա�",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 1,
					"salesAccount"	: "zhangyuxing1980"
				},

				1:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000154587798",	"passWord"		: "RUFSXKBD",
					"orderID"		: newOrderID(),				"serverName"	: "����֮��",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "������Ѿ���ʹ��",
					"buyerMailTitle": "����ʧ��",				"buyerMailContent" : "����ĵ㿨��Ϣ�����Ѿ��¼ܣ����ʼ��������ν��׷��ã���ȡ�ء�",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "���۵㿨ʧ��",			"sellerMailContent" : "����۵ĵ㿨(����:HAAAB000000154587798)�Ѿ�ʹ�ã��Ѿ��¼ܣ�Ѻ��û�ա�",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 1,
					"salesAccount"	: "zhangyuxing1980"
				},

				2:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000156816952",	"passWord"		: "DEDHNZEK",
					"orderID"		: newOrderID(),				"serverName"	: "����֮��",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "û������ʺŵ��³�ֵʧ��",
					"buyerMailTitle": "����ʧ��",				"buyerMailContent" : "��μ��۽��׳������ʼ��������ν��׷��ã���ȡ�ء�",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "",						"sellerMailContent" : "",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 0,
					"salesAccount"	: "zhangyuxing1980"
				},

				3:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000110285185",	"passWord"		: "NIOLKNLC",
					"orderID"		: newOrderID(),				"serverName"	: "����֮��",
					"salesName"		: "ttet",		"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "",						"sellTime"		: int(time.time()),
					"description"	: "�������������³�ֵʧ��",
					"buyerMailTitle": "����ʧ��",				"buyerMailContent" : "��μ��۽��׳������ʼ��������ν��׷��ã���ȡ�ء�",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "",						"sellerMailContent" : "",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 0,
					"salesAccount"	: "zhangyuxing1980"
				},

				4:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000110285186",	"passWord"		: "NMKZESGQ",
					"orderID"		: newOrderID(),				"serverName"	: "����С��",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "�����ڵķ���������ֵ����",
					"buyerMailTitle": "����ʧ��",				"buyerMailContent" : "��μ��۽��׳������ʼ��������ν��׷��ã���ȡ�ء�",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "",						"sellerMailContent" : "",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 0,
					"salesAccount"	: "zhangyuxing1980"
				},

				5:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000110285187",	"passWord"		: "NEUJNTKT",
					"orderID"		: newOrderID(),				"serverName"	: "����֮��",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "50",						"sellTime"		: int(time.time()),
					"description"	: "��ֵ����",
					"buyerMailTitle": "����ʧ��",				"buyerMailContent" : "����ĵ㿨��Ϣ�����Ѿ��¼ܣ����ʼ��������ν��׷��ã���ȡ�ء�",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "���۵㿨ʧ��",			"sellerMailContent" : "����۵ĵ㿨(����:HAAAB000000110285187)��ֵ�����������¼��ۣ��ϴμ��۵�Ѻ��û�ա�",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 1,
					"salesAccount"	: "zhangyuxing1980"
				},
			}


pcm = BigWorld.entities[BigWorld.globalData["PointCardMgr"].id]

cards = []

for value in cardsInfo.itervalues():
	card = PointCardInfo()
	card.isSelling 			= value["isSelling"]
	card.buyerName 			= value["buyerName"]
	card.buyerAccount 		= value["buyerAccount"]
	card.price 				= value["price"]
	card.cardNo 			= value["cardNo"].lower()
	card.passWord 			= value["passWord"]
	card.orderID 			= value["orderID"]
	card.serverName 		= value["serverName"]
	card.salesName 			= value["salesName"]
	card.salesIP 			= value["salesIP"]
	card.result				= value["result"]
	card.overTimeResult 	= value["overTimeResult"]
	card.parValue 			= value["parValue"]
	card.sellTime 			= value["sellTime"]
	card.salesAccount		= value["salesAccount"]
	cards.append( card )

def buy():

	for i in pcm.currentSellCards.keys():
		pcm.takeOffCard(i)

	query = "delete from custom_MailTable"
	BigWorld.executeRawDatabaseCommand( query, onDelete )


	pcm.addCurrentSellCard( cards[0] )								#���ſ��ʺź����벻��
	pcm._saveToDatabase( cards[0] )
	cards[0].isSelling 		= True
	cards[0].buyerName  	= "�л�Ӣ��"
	cards[0].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[0] )

	pcm.addCurrentSellCard( cards[1] )								#������Ѿ���ʹ��
	pcm._saveToDatabase( cards[1] )
	cards[1].isSelling 		= True
	cards[1].buyerName  	= "�л�Ӣ��"
	cards[1].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[1] )

	pcm.addCurrentSellCard( cards[2] )								#û������ʺŵ��³�ֵʧ��
	pcm._saveToDatabase( cards[2] )
	cards[3].isSelling 		= True
	cards[3].buyerName  	= "�л�Ӣ��"
	cards[3].buyerAccount 	= "zhangyuxingZZZZ"
	pcm._buyCard( cards[3] )


	pcm.addCurrentSellCard( cards[3] )								#�������������³�ֵʧ��
	pcm._saveToDatabase( cards[3] )
	cards[4].isSelling 		= True
	cards[4].buyerName  	= "�л�Ӣ��"
	cards[4].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[4] )



	pcm.addCurrentSellCard( cards[4] )								#�����ڵķ���������ֵ����
	pcm._saveToDatabase( cards[4] )
	cards[5].isSelling 		= True
	cards[5].buyerName  	= "�л�Ӣ��"
	cards[5].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[5] )



	pcm.addCurrentSellCard( cards[5] )								#��ֵ����
	pcm._saveToDatabase( cards[5] )
	cards[6].isSelling 		= True
	cards[6].buyerName  	= "�л�Ӣ��"
	cards[6].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[5] )


def check():
	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[0].buyerName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onBuyer, 0 ))

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[0].salesName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onSeller, 0 ))


	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[1].buyerName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onBuyer, 1 ))

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[1].salesName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onSeller, 1 ))


	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[2].buyerName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onBuyer, 2 ))

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[2].salesName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onSeller, 2 ))

	return
	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[3].buyerName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onBuyer, 3 ))

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[3].salesName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onSeller, 3 ))


	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[4].buyerName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onBuyer, 4 ))

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[4].salesName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onSeller, 4 ))


	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[5].buyerName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onBuyer, 5 ))

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[5].salesName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( _onSeller, 5 ))


def _onBuyer( num, result, rows, errstr ):
	"""
	"""
	for i in result:
		if i[1] == cardsInfo[num]["buyerMailTitle"] and i[2] == cardsInfo[num]["buyerMailContent"] and i[13] == cardsInfo[num]["buyerReceiveMoney"]:
			return
	print "------------------------------------------------------------------------------------"
	for i in result:
		print i[1]
		print i[2]
		print i[13]
	print "------------------------------------------------------------------------------------"
	print cardsInfo[num]["buyerMailTitle"]
	print cardsInfo[num]["buyerMailContent"]
	print cardsInfo[num]["buyerReceiveMoney"]
	print cardsInfo[num]["cardNo"]
	assert 0

def _onSeller( num, result, rows, errstr ):
	"""
	"""
	if cardsInfo[num]["sellerMailTitle"] == "":
		return
	for i in result:
		if i[1] == cardsInfo[num]["sellerMailTitle"] and i[2] == cardsInfo[num]["sellerMailContent"] and i[13] == cardsInfo[num]["sellerReceiveMoney"]:
			if cardsInfo[num]["takeOffCard"] == 1:
				assert cardsInfo[num]["cardNo"] not in pcm.currentSellCards
			else:
				assert cardsInfo[num]["cardNo"] in pcm.currentSellCards
			return
	print "------------------------------------------------------------------------------------"
	for i in result:
		print i[1]
		print i[2]
		print i[13]
	print "------------------------------------------------------------------------------------"
	print cardsInfo[num]["sellerMailTitle"]
	print cardsInfo[num]["sellerMailContent"]
	print cardsInfo[num]["sellerReceiveMoney"]
	print cardsInfo[num]["cardNo"]
	assert 0


def onDelete(  result, rows, errstr ):
	"""
	"""
	pass



"""���ַ����������
csdefine.RECHANGE_SUCCESS							# �㿨���۳ɹ�
csdefine.RECHANGE_NO_OR_PWD_FAILED				    # ���Ż��������
csdefine.RECHANGE_USED_FAILED					    # ��ʹ�õĿ�
csdefine.RECHANGE_ACCOUNT_NOT_ACTIVITIED_FAILED	    # �ʺ�δ�ڸ�������
csdefine.RECHANGE_ACCOUNT_NOT_HAVE_FAILED		    # �ʺŲ�����
csdefine.RECHANGE_FAILED						    # ��ֵʧ��
csdefine.RECHANGE_MD5_FAILED					    # MD5У��ʧ��
csdefine.RECHANGE_PARAMS_FAILED					    # ����������
csdefine.RECHANGE_SERVER_NAME_FAILED			    # �����ڵķ�������
csdefine.RECHANGE_OVER_DUPLICATE_FAILED			    # �������ظ�
csdefine.RECHANGE_TEN_YUAN						    # 10Ԫ��ֵ�Ŀ�
csdefine.RECHANGE_IP_FAILED						    # IP���󣬷������������ͷ�������IP��Ӧ����
csdefine.RECHANGE_ACCOUNT_MSG_FALIED			    # ��ȡ�ʺ���Ϣʧ��
csdefine.RECHANGE_CARD_LOCKED_CARD				    # �ѷ�ŵĿ�
csdefine.RECHANGE_LOGGED_FALID					    # д���ֵ��־ʧ��
csdefine.RECHANGE_CARD_NOT_EXIST_CARD			    # �������� �� ��δ����
csdefine.RECHANGE_SEND_YUANBAO_FAILED			    # �����ɹ������Ƿ���Ԫ��ʧ��
csdefine.RECHANGE_THIRTY						    # 30Ԫ��ֵ�Ŀ�
csdefine.RECHANGE_CARD_VALUE_FAILED				    # ��ֵ����
csdefine.RECHANGE_OVERTIME_FAILED				    # ��ʱ���������쳣�����
"""

def resultCheck( minNum, maxNum ):
	for i in xrange( minNum, maxNum ):
		pass


BUYER_NAME = "�л�Ӣ��"

def chargeCase( num, result ):
	query = "delete from custom_MailTable"
	BigWorld.executeRawDatabaseCommand( query, onDelete )
	pcm.takeOffCard(cards[num].cardNo)
	pcm.addCurrentSellCard( cards[num] )
	pcm._saveToDatabase( cards[num] )
	cards[num].isSelling 		= True
	cards[num].buyerName  	= BUYER_NAME
	cards[num].buyerAccount 	= "zhangyuxing1980"
	pcm.dbc.saveSellingCard( cards[num] )
	del pcm.currentSellCards[cards[num].cardNo]
	cards[num].result = result
	pcm.onReCharge( cards[num] )


def checkChargeCase( num, result ):
	"""
	"""
	buyerCallback = None
	sellerCallback = None
	if result in [3,4,5,6,7,8,9,11,12,14]:
		buyerCallback = chargeBuyResult1
		sellerCallback = chargeSellResult1
	elif result in [1,2,13,15,30,17]:
		buyerCallback = chargeBuyResult2
		sellerCallback = chargeSellResult2
	elif result in [0,10,16]:
		buyerCallback = chargeBuyResult3
		sellerCallback = chargeSellResult3
	elif result == -1:
		buyerCallback = chargeBuyResult4
		sellerCallback = chargeSellResult4

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( BUYER_NAME ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( buyerCallback, num ))

	query = "select * from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % (BigWorld.escape_string( cards[num].salesName ), csdefine.MAIL_SENDER_TYPE_RETURN )
	BigWorld.executeRawDatabaseCommand( query, Functor( sellerCallback, num ))

def chargeBuyResult1(  num, result, rows, errstr ):
	"""
	�㿨��Ч�����۹��̴��󣬷��ؽ�Ǯ�����ߡ�
	"""
	for i in result:
		if i[1] == "����ʧ��" and i[2] == "��μ��۽��׳������ʼ��������ν��׷��ã���ȡ�ء�" and i[13] == str(cards[num].price):
			print "num=",  num
			return
	print "num=",  num
	print "-----------------------------------"
	for i in result:
		print i[1]
		print i[2]
		print i[13]
	print "-----------------------------------"
	assert 0

def chargeBuyResult2(  num, result, rows, errstr ):
	"""
	�㿨��Ч�����۹�����ȷ�����ؽ�Ǯ�����ߣ�û������Ѻ��
	"""
	for i in result:
		if i[1] == "����ʧ��" and i[2] == "����ĵ㿨��Ϣ�����Ѿ��¼ܣ����ʼ��������ν��׷��ã���ȡ�ء�" and i[13] == str(cards[num].price):
			print "num=",  num
			return
	print "num=",  num
	print "-----------------------------------"
	for i in result:
		print i[1]
		print i[2]
		print i[13]
	print "-----------------------------------"
	assert 0

def chargeBuyResult3(  num, result, rows, errstr ):
	"""
	�������׳ɹ���
	"""
	for i in result:
		if i[1] == "���׳ɹ�" and i[2] == "Ԫ�������Ժ��ֵ������ʻ����뼰ʱ�鿴�����24Сʱ��û��Ԫ�����ˣ����GM��ϵ��" and i[13] == "0":
			print "num=",  num
			return
	print "num" == num
	print "-----------------------------------"
	for i in result:
		print i[1]
		print i[2]
		print i[13]
	print "-----------------------------------"
	assert 0

def chargeBuyResult4(  num, result, rows, errstr ):
	"""
	��ʱ����
	"""
	pass



def chargeSellResult1(  num, result, rows, errstr ):
	"""
	�㿨��Ч�����۹��̴��󣬷��ؽ�Ǯ�����ߡ�
	"""
	assert 1

def chargeSellResult2(  num, result, rows, errstr ):
	"""
	�㿨��Ч�����۹�����ȷ�����ؽ�Ǯ�����ߣ�û������Ѻ��
	"""
	for i in result:
		if i[1] == "���۵㿨ʧ��" and cards[num].cardNo in i[2] and i[13] == "0":
			print "num=",  num
			return
	print "num=",  num
	print "-----------------------------------"
	for i in result:
		print i[1]
		print i[2]
		print i[13]
	print "-----------------------------------"
	assert 0

def chargeSellResult3(  num, result, rows, errstr ):
	"""
	�������׳ɹ���
	"""
	for i in result:
		if i[1] == "���۵㿨�ɹ�" and i[2] == "����۵ĵ㿨(����:%s)�Ѿ��ɹ�������"%cards[num].cardNo and i[13] == str(int(cards[num].price) + csconst.SELL_POINT_CARD_YAJIN):
			print "num=",  num
			return
	print "num=",  num
	print "-----------------------------------"
	for i in result:
		print i[1]
		print i[2]
		print i[13]
	print "-----------------------------------"
	assert 0

def chargeSellResult4(  num, result, rows, errstr ):
	"""
	��ʱ����
	"""
	pass