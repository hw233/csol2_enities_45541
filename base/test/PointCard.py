# -*- coding: gb18030 -*-

"""
点卡寄售base测试脚本
测试功能：
	base/PointCardMgr.py
		class PointCardMgr

"""

#注意，与角色有关的测试（就是一些通过接口调用的方法），完全可以通过client完整测试，所以在base测试，重点将集中在类本身功能上。


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

#用于测试的卡信息
cardsInfo = {	0:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000154587797",	"passWord"		: "ABC",
					"orderID"		: newOrderID(),				"serverName"	: "永恒之光",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "这张卡帐号和密码不对",
					"buyerMailTitle": "交易失败",				"buyerMailContent" : "购买的点卡信息有误，已经下架，本邮件包含本次交易费用，请取回。",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "寄售点卡失败",			"sellerMailContent" : "你寄售的点卡(卡号:HAAAB000000154587797)帐号和密码有误，已经下架，押金没收。",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 1,
					"salesAccount"	: "zhangyuxing1980"
				},

				1:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000154587798",	"passWord"		: "RUFSXKBD",
					"orderID"		: newOrderID(),				"serverName"	: "永恒之光",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "这个卡已经被使用",
					"buyerMailTitle": "交易失败",				"buyerMailContent" : "购买的点卡信息有误，已经下架，本邮件包含本次交易费用，请取回。",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "寄售点卡失败",			"sellerMailContent" : "你寄售的点卡(卡号:HAAAB000000154587798)已经使用，已经下架，押金没收。",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 1,
					"salesAccount"	: "zhangyuxing1980"
				},

				2:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000156816952",	"passWord"		: "DEDHNZEK",
					"orderID"		: newOrderID(),				"serverName"	: "永恒之光",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "没有这个帐号导致充值失败",
					"buyerMailTitle": "交易失败",				"buyerMailContent" : "这次寄售交易出错。本邮件包含本次交易费用，请取回。",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "",						"sellerMailContent" : "",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 0,
					"salesAccount"	: "zhangyuxing1980"
				},

				3:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000110285185",	"passWord"		: "NIOLKNLC",
					"orderID"		: newOrderID(),				"serverName"	: "永恒之光",
					"salesName"		: "ttet",		"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "",						"sellTime"		: int(time.time()),
					"description"	: "参数不完整导致充值失败",
					"buyerMailTitle": "交易失败",				"buyerMailContent" : "这次寄售交易出错。本邮件包含本次交易费用，请取回。",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "",						"sellerMailContent" : "",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 0,
					"salesAccount"	: "zhangyuxing1980"
				},

				4:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000110285186",	"passWord"		: "NMKZESGQ",
					"orderID"		: newOrderID(),				"serverName"	: "永恒小光",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "10",						"sellTime"		: int(time.time()),
					"description"	: "不存在的服务器名充值错误",
					"buyerMailTitle": "交易失败",				"buyerMailContent" : "这次寄售交易出错。本邮件包含本次交易费用，请取回。",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "",						"sellerMailContent" : "",
					"sellerReceiveMoney": "0",
					"takeOffCard"	: 0,
					"salesAccount"	: "zhangyuxing1980"
				},

				5:{	"isSelling"		: 0,						"buyerName"	: "",
					"buyerAccount"	: "",						"price"			: 1000,
					"cardNo"		: "HAAAB000000110285187",	"passWord"		: "NEUJNTKT",
					"orderID"		: newOrderID(),				"serverName"	: "永恒之光",
					"salesName"		: "ttet",					"salesIP"		: 2030047404,
					"result"		: -1,						"overTimeResult": -1,
					"parValue"		: "50",						"sellTime"		: int(time.time()),
					"description"	: "面值不符",
					"buyerMailTitle": "交易失败",				"buyerMailContent" : "购买的点卡信息有误，已经下架，本邮件包含本次交易费用，请取回。",
					"buyerReceiveMoney"	: "1000",
					"sellerMailTitle": "寄售点卡失败",			"sellerMailContent" : "你寄售的点卡(卡号:HAAAB000000110285187)面值不符，请重新寄售，上次寄售的押金没收。",
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


	pcm.addCurrentSellCard( cards[0] )								#这张卡帐号和密码不对
	pcm._saveToDatabase( cards[0] )
	cards[0].isSelling 		= True
	cards[0].buyerName  	= "中华英雄"
	cards[0].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[0] )

	pcm.addCurrentSellCard( cards[1] )								#这个卡已经被使用
	pcm._saveToDatabase( cards[1] )
	cards[1].isSelling 		= True
	cards[1].buyerName  	= "中华英雄"
	cards[1].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[1] )

	pcm.addCurrentSellCard( cards[2] )								#没有这个帐号导致充值失败
	pcm._saveToDatabase( cards[2] )
	cards[3].isSelling 		= True
	cards[3].buyerName  	= "中华英雄"
	cards[3].buyerAccount 	= "zhangyuxingZZZZ"
	pcm._buyCard( cards[3] )


	pcm.addCurrentSellCard( cards[3] )								#参数不完整导致充值失败
	pcm._saveToDatabase( cards[3] )
	cards[4].isSelling 		= True
	cards[4].buyerName  	= "中华英雄"
	cards[4].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[4] )



	pcm.addCurrentSellCard( cards[4] )								#不存在的服务器名充值错误
	pcm._saveToDatabase( cards[4] )
	cards[5].isSelling 		= True
	cards[5].buyerName  	= "中华英雄"
	cards[5].buyerAccount 	= "zhangyuxing1980"
	pcm._buyCard( cards[5] )



	pcm.addCurrentSellCard( cards[5] )								#面值不符
	pcm._saveToDatabase( cards[5] )
	cards[6].isSelling 		= True
	cards[6].buyerName  	= "中华英雄"
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



"""各种返回情况处理
csdefine.RECHANGE_SUCCESS							# 点卡寄售成功
csdefine.RECHANGE_NO_OR_PWD_FAILED				    # 卡号或密码错误
csdefine.RECHANGE_USED_FAILED					    # 已使用的卡
csdefine.RECHANGE_ACCOUNT_NOT_ACTIVITIED_FAILED	    # 帐号未在该区激活
csdefine.RECHANGE_ACCOUNT_NOT_HAVE_FAILED		    # 帐号不存在
csdefine.RECHANGE_FAILED						    # 充值失败
csdefine.RECHANGE_MD5_FAILED					    # MD5校验失败
csdefine.RECHANGE_PARAMS_FAILED					    # 参数不完整
csdefine.RECHANGE_SERVER_NAME_FAILED			    # 不存在的服务器名
csdefine.RECHANGE_OVER_DUPLICATE_FAILED			    # 定单号重复
csdefine.RECHANGE_TEN_YUAN						    # 10元面值的卡
csdefine.RECHANGE_IP_FAILED						    # IP错误，服务器中文名和服务器的IP对应不上
csdefine.RECHANGE_ACCOUNT_MSG_FALIED			    # 获取帐号信息失败
csdefine.RECHANGE_CARD_LOCKED_CARD				    # 已封号的卡
csdefine.RECHANGE_LOGGED_FALID					    # 写入充值日志失败
csdefine.RECHANGE_CARD_NOT_EXIST_CARD			    # 卡不存在 或 卡未激活
csdefine.RECHANGE_SEND_YUANBAO_FAILED			    # 操作成功，但是发放元宝失败
csdefine.RECHANGE_THIRTY						    # 30元面值的卡
csdefine.RECHANGE_CARD_VALUE_FAILED				    # 面值不符
csdefine.RECHANGE_OVERTIME_FAILED				    # 超时处理（包括异常情况）
"""

def resultCheck( minNum, maxNum ):
	for i in xrange( minNum, maxNum ):
		pass


BUYER_NAME = "中华英雄"

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
	点卡有效，寄售过程错误，返回金钱给买者。
	"""
	for i in result:
		if i[1] == "交易失败" and i[2] == "这次寄售交易出错。本邮件包含本次交易费用，请取回。" and i[13] == str(cards[num].price):
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
	点卡无效，寄售过程正确，返回金钱给买者，没收买者押金。
	"""
	for i in result:
		if i[1] == "交易失败" and i[2] == "购买的点卡信息有误，已经下架，本邮件包含本次交易费用，请取回。" and i[13] == str(cards[num].price):
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
	买卖交易成功。
	"""
	for i in result:
		if i[1] == "交易成功" and i[2] == "元宝将在稍后充值入你的帐户，请及时查看。如果24小时内没有元宝到账，请和GM联系。" and i[13] == "0":
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
	超时返回
	"""
	pass



def chargeSellResult1(  num, result, rows, errstr ):
	"""
	点卡有效，寄售过程错误，返回金钱给买者。
	"""
	assert 1

def chargeSellResult2(  num, result, rows, errstr ):
	"""
	点卡无效，寄售过程正确，返回金钱给买者，没收买者押金。
	"""
	for i in result:
		if i[1] == "寄售点卡失败" and cards[num].cardNo in i[2] and i[13] == "0":
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
	买卖交易成功。
	"""
	for i in result:
		if i[1] == "寄售点卡成功" and i[2] == "你寄售的点卡(卡号:%s)已经成功卖出。"%cards[num].cardNo and i[13] == str(int(cards[num].price) + csconst.SELL_POINT_CARD_YAJIN):
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
	超时返回
	"""
	pass