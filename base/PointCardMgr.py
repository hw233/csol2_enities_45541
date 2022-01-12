# -*- coding: gb18030 -*-

import Love3
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import BackgroundTask
from bwdebug import *
from urllib import urlopen
import csdefine
import time
import random
import csconst
import socket
from PointCardInfo import PointCardInfo
from Function import newUID
import binascii
import urllib
import _md5
from MsgLogger import g_logger
from Function import Functor
import csstatus

import struct,socket


socket.setdefaulttimeout(5.0)	#设置超时时间

HANDLE_CARD_SELLING_CBID 			= 10000		#处理交易
HANDLE_CARD_OVERTIME_CBID			= 10001		#处理超时
HANDLE_CARD_OVERANDOVERTIME_CBID 	= 10002		#超时处理返回任然超时
OPERATE_CONTROL_CBID 				= 10003		#速度控制回调
HANDLE_CARD_OUT_OF_DATE_CBID		= 10004		#过期点卡检查回调


OUTOFDATECHECKSPEED			= 3600.0			#过期点卡检查
OVERTIME			= 60.0
OVERANDOVERTIME		= 3600.0

CARD_VALID_TIME		= 24 * 3600		# 一天

#BigWorld.globalData["pointCardWord"] = "tempString"
#BigWorld.globalData["pointCardAddr"]					#充值端口 如：http://transfer.gyyx.cn:81/CsServiceTest/CSCarConsignment.asmx
#BigWorld.globalData["pointCardWord"]					#充值校验码
class PointCharge:
	def easyCardRule( self, cardInfo ):
		"""
		#处理简单的点卡规则判定
		简单规则：
			20个字母，前4个字母为haaa,第5个字母代表点卡面值，6-20随机生成
			字母代表的点卡面值为：
			E       10.0 光宇10元冲值卡(带矩阵)

			F       30.0 光宇30元冲值卡(带矩阵)

			B       10.0 光宇10元冲值卡

			D      30.0 光宇30元冲值卡

			P       10.0 声讯10元冲值卡

		@return  (bool， value)
			1.是否有效
			2.卡的数值
		"""
		valueDict = { 'e' 	: "10",
				'f'	: "30",
				'b'	: "10",
				'd'	: "30",
				'p'	: "10",
				}
		if len(cardInfo.cardNo) != 20:
			return (False,0)

		if cardInfo.cardNo[0:4]  != "haaa":
			return (False,0)

		if cardInfo.cardNo[4] not in valueDict:
			return (False, 0)
		return ( True, valueDict[cardInfo.cardNo[4]] )

	def recharge( self, cardInfo ):
		"""
		充值
		"""
		#http://transfer.gyyx.cn:81/CsServiceTest/CSCarConsignment.asmx/CSFill?CardNo=HAAAB000000012345678&CardPwd=QWERASDF&OrderId=06111610325136200123&UserName=zhaoye&ServerName=%BB%A8%B9%FB%C9%BD&SalesName=martin&SalesIP=218.54.14.45&ParValue=30&SignKey=57794C27B70FF9F8B1CDAF921B212550
		#path = "http://transfer.gyyx.cn:81/CsServiceTest/CSCarConsignment.asmx/CSFill?"
		path = BigWorld.globalData["pointCardAddr"] + "/CSFill?"

		params = "cardNo=%s&cardPwd=%s&orderId=%s&userName=%s&serverName=%s&salesName=%s&salesIP=%s&parValue=%s&signKey=%s"

		cardNo 		= cardInfo.cardNo
		cardPwd 	= cardInfo.passWord
		cardOrderID = cardInfo.orderID
		buyerAccount	= cardInfo.buyerAccount
		serverName 	= cardInfo.serverName
		salesAccount	= cardInfo.salesAccount
		salesIP 	= socket.inet_ntoa(struct.pack("!I",cardInfo.salesIP))
		parValue 	= cardInfo.parValue
		#卡号 + 密码 + 订单号 + 用户名 + 服务器名 + 寄售玩家名字 + 寄售IP + 面值 + BigWorld.globalData["pointCardWord"]
		#print cardNo + cardPwd + str(cardOrderID) + buyerAccount + urllib.quote(cardInfo.serverName.decode("gbk").encode("utf-8")).lower() + salesName + str(salesIP) + str(parValue) + BigWorld.globalData["pointCardWord"]
		hash = _md5.new()
		hash.update( cardNo + cardPwd + cardOrderID + buyerAccount + urllib.quote(cardInfo.serverName.decode("gbk").encode("utf-8")).lower() + salesAccount + str(salesIP) + str(parValue) + BigWorld.globalData["pointCardWord"] )
		cardInfo.signKey = hash.hexdigest()
		result = -1
		try:
			#print path + params%( cardNo, cardPwd, cardOrderID,buyerAccount, serverName, salesAccount, salesIP, parValue, cardInfo.signKey )
			print path + params%( cardNo, cardPwd, cardOrderID,buyerAccount, urllib.quote(cardInfo.serverName.decode("gbk").encode("utf-8")).lower(), salesAccount, salesIP, parValue, cardInfo.signKey )
			ht = urlopen(path + params%( cardNo, cardPwd, cardOrderID,buyerAccount, urllib.quote(cardInfo.serverName.decode("gbk").encode("utf-8")).lower(), salesAccount, salesIP, parValue, cardInfo.signKey )).read()
			result = ht.replace('<?xml version="1.0" encoding="utf-8"?>\r\n<string xmlns="http://www.gyyx.cn/">',"").replace('</string>',"")
			return int(result)
		except Exception, errstr:
			return result

def overTimeHandle( cardInfo ):
	"""
	超时处理
	"""
	#http://transfer.gyyx.cn:81/CsServiceTest/CSCarConsignment.asmx/CSValid?orderId=123
	path = "http://transfer.gyyx.cn:81/CsServiceTest/CSCarConsignment.asmx/CSValid?orderId=%s"%cardInfo.orderID
	try:
		ht = urlopen(path).read()
		result = ht.replace('<?xml version="1.0" encoding="utf-8"?>\r\n<string xmlns="http://www.gyyx.cn/">',"").replace('</string>',"")
		return int(result)
	except Exception, errstr:
		return -1



class RechargeThread( BackgroundTask.BackgroundTask ):
	"""
	充值线程
	"""
	def __init__( self, cardInfo ):
		"""
		"""
		self.cardInfo = cardInfo
		BackgroundTask.BackgroundTask.__init__( self )


	def doBackgroundTask( self, mgr ):
		#读取网页字符
		#有效->关闭网页字符
		id = BigWorld.globalData["PointCardMgr"].id
		scMgr = BigWorld.entities[id]
		self.cardInfo.result = scMgr.chargeInstance.recharge( self.cardInfo )
		#self.cardInfo.result = random.randint( 0, 30 )
		mgr.addMainThreadTask( self )


	def doMainThreadTask( self, mgr ):
		id = BigWorld.globalData["PointCardMgr"].id
		scMgr = BigWorld.entities[id]
		scMgr.onReCharge( self.cardInfo )

class OverTimeThread(  BackgroundTask.BackgroundTask ):
	"""
	处理超时线程
	"""
	def __init__( self, cardInfo ):
		"""
		"""
		self.cardInfo = cardInfo
		BackgroundTask.BackgroundTask.__init__( self )


	def doBackgroundTask( self, mgr ):
		#读取网页字符
		#有效->关闭网页字符
		self.cardInfo.overTimeResult = overTimeHandle( self.cardInfo )
		mgr.addMainThreadTask( self )


	def doMainThreadTask( self, mgr ):
		id = BigWorld.globalData["PointCardMgr"].id
		scMgr = BigWorld.entities[id]
		scMgr.onOverTime( self.cardInfo )



class RechargeResultHandle:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		pass


class SuccessResult( RechargeResultHandle ):
	"""
	充值成功
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "冲卡成功"
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_1, cschannel_msgs.POINT_CARD_INFO_2%cardInfo.cardNo, cardInfo.price + csconst.SELL_POINT_CARD_YAJIN, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_3, cschannel_msgs.POINT_CARD_INFO_4, 0, "" )
		try:
			g_logger.pointCardRechargeLog( cardInfo.cardNo, cardInfo.price, cardInfo.buyerName, cardInfo.buyerAccount, cardInfo.salesName )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellSuccessful, cardInfo.cardNo, cardInfo.price + csconst.SELL_POINT_CARD_YAJIN, cardInfo.buyerName, cardInfo.parValue  ) )


	def _onCardSellSuccessful( self, cardNo, price, buyerName, parValue, callResult ):
		"""
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		jin	= price/10000
		yin = price/100 - jin*100
		tong = price - jin*10000 - yin*100
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_SUCCESSFUL, str(( cardNo, jin, yin, tong, )) )
		BigWorld.lookUpBaseByName( "Role", buyerName, Functor( self._onCardBuySuccessful, parValue ) )

	def _onCardBuySuccessful( self, parValue, callResult ):
		"""
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
			count = str( int( parValue ) * 100 )
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_BUY_SUCCESSFUL, str( (count, )) )




class NoOrPwdFailedResult( RechargeResultHandle ):
	"""
	帐号和密码错误导致充值失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "帐号和密码错误导致充值失败"
		ERROR_MSG( "寄售点卡错误：帐号和密码错误导致充值失败。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_6%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )

		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )

class UsedFailedResult( RechargeResultHandle ):
	"""
	点卡已经使用导致充值失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "寄售点卡错误：点卡已经使用导致充值失败。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_9%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )

		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )

class AccountNotActivitiedFailedResult( RechargeResultHandle ):
	"""
	帐号在该区没有激活导致充值失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "帐号在该区没有激活导致充值失败"
		ERROR_MSG( "寄售点卡错误：理论上不存在帐号在该区没有激活导致充值失败的返回，可是现在返回了。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )

class AccountNotHaveFailedResult( RechargeResultHandle ):
	"""
	没有这个帐号导致充值失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "没有这个帐号导致充值失败"
		ERROR_MSG( "寄售点卡错误：理论上不存在'没有这个帐号'导致充值失败的返回，可是现在返回了。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class RechangeFailedResult( RechargeResultHandle ):
	"""
	普通充值失败（未知错误）
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "普通充值失败"
		ERROR_MSG( "寄售点卡错误：未知原因的充值失败。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class MD5FailedResult( RechargeResultHandle ):
	"""
	MD5检测失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "MD5检测失败"
		ERROR_MSG( "寄售点卡错误：理论上不存在'MD5检测失败'导致充值失败的返回，可是现在返回了。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class ParamsFailedResult( RechargeResultHandle ):
	"""
	参数不完整充值错误
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "参数不完整充值错误"
		ERROR_MSG( "寄售点卡错误：理论上不存在'参数不完整充值错误'导致充值失败的返回，可是现在返回了。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )




class ServerNameFailedResult( RechargeResultHandle ):
	"""
	不存在的服务器名充值错误
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "不存在的服务器名充值错误"
		ERROR_MSG( "寄售点卡错误：服务器名字不对。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class OrderDuplicateFailedResult( RechargeResultHandle ):
	"""
	订单重复充值错误
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "订单重复充值错误"

		ERROR_MSG( "寄售点卡错误：生成的随机订单重复。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )




class IPFailedResult( RechargeResultHandle ):
	"""
	IP错误，服务器中文名和服务器的IP对应不上
	不会有这个返回
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "IP错误，服务器中文名和服务器的IP对应不上"
		ERROR_MSG( "寄售点卡错误：IP错误，服务器中文名和服务器的IP对应不上。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )




class AccountMsgFailedResult( RechargeResultHandle ):
	"""
	获取帐号信息失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "寄售点卡错误：获取帐号信息失败。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class CardLockedFailedResult( RechargeResultHandle ):
	"""
	已封号的卡
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "已封号的卡"
		ERROR_MSG( "寄售点卡错误：已封号的卡。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_11%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )


		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )



class LoggedFailedResult( RechargeResultHandle ):
	"""
	写入充值日志失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "寄售点卡错误：写入充值日志失败。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class CardNotExistFailedResult( RechargeResultHandle ):
	"""
	卡不存在 或 卡未激活
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "寄售点卡错误：卡不存在 或 卡未激活。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_12%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_13, cardInfo.price, "" )

		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )


class SendYuanbaoFailedResult( RechargeResultHandle ):
	"""
	操作成功，但是发放元宝失败
	可以理解为成功。网络充值部分会持续尝试，直到成功。
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "操作成功，但是发放元宝失败"
		ERROR_MSG( "寄售点卡错误：操作成功，但是发放元宝失败。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_1, cschannel_msgs.POINT_CARD_INFO_2%cardInfo.cardNo, cardInfo.price + csconst.SELL_POINT_CARD_YAJIN, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_3, cschannel_msgs.POINT_CARD_INFO_4, 0, "" )



class CardValueFailedResult( RechargeResultHandle ):
	"""
	面值不符
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "面值不符"
		ERROR_MSG( "寄售点卡错误：理论上不存在‘面值不符’这个返回，可是现在返回了。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_14%cardInfo.cardNo, cardInfo.price + csconst.SELL_POINT_CARD_YAJIN, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )

		pointCardMgr.takeOffCard( cardInfo.cardNo )

class OverTimeResult( RechargeResultHandle ):
	"""
	充值超时
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "寄售点卡错误：充值超时。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.addOverTimeCard( cardInfo )


class OverTimeCheckHandle:
	"""
	超时处理
	"""
	def __init__( self ):
		"""
		"""
		pass

	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		pass


class OverTimeCheckOverTime( OverTimeCheckHandle ):
	"""
	超时处理返回超时
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		pointCardMgr.onOverTimeAgain( cardInfo )


class OverTimeCheckSuccess( OverTimeCheckHandle ):
	"""
	超时处理返回成功
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_1, cschannel_msgs.POINT_CARD_INFO_2%cardInfo.cardNo, cardInfo.price + csconst.SELL_POINT_CARD_YAJIN, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_3, cschannel_msgs.POINT_CARD_INFO_4, 0, "" )


class OverTimeCheckFailed( OverTimeCheckHandle ):
	"""
	超时处理返回失败
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "寄售点卡错误：未知原因的充值失败。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )



class OverTimeCheckOrderFailed( OverTimeCheckHandle ):
	"""
	超时处理返回没有这个订单
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "寄售点卡错误：超时处理返回没有这个订单。卡号(%s), 卖主(%s), 买主(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )



#充值返回处理
RECHARGE_RESULT_PROCESSES = {	csdefine.RECHANGE_SUCCESS					:	SuccessResult(),							# 点卡寄售成功
							csdefine.RECHANGE_NO_OR_PWD_FAILED				:	NoOrPwdFailedResult(),						# 卡号或密码错误
							csdefine.RECHANGE_USED_FAILED					:	UsedFailedResult(),							# 已使用的卡
							csdefine.RECHANGE_ACCOUNT_NOT_ACTIVITIED_FAILED	:	AccountNotActivitiedFailedResult(),			# 帐号未在该区激活
							csdefine.RECHANGE_ACCOUNT_NOT_HAVE_FAILED		:	AccountNotHaveFailedResult(),				# 帐号不存在
							csdefine.RECHANGE_FAILED						:	RechangeFailedResult(),						# 充值失败
							csdefine.RECHANGE_MD5_FAILED					:	MD5FailedResult(),							# MD5校验失败
							csdefine.RECHANGE_PARAMS_FAILED					:	ParamsFailedResult(),						# 参数不完整
							csdefine.RECHANGE_SERVER_NAME_FAILED			:	ServerNameFailedResult(),					# 不存在的服务器名
							csdefine.RECHANGE_OVER_DUPLICATE_FAILED			:	OrderDuplicateFailedResult(),				# 定单号重复
							csdefine.RECHANGE_TEN_YUAN						:	SuccessResult(),							# 10元面值的卡
							csdefine.RECHANGE_IP_FAILED						:	IPFailedResult(),							# IP错误，服务器中文名和服务器的IP对应不上
							csdefine.RECHANGE_ACCOUNT_MSG_FALIED			:	AccountMsgFailedResult(),					# 获取帐号信息失败
							csdefine.RECHANGE_CARD_LOCKED_CARD				:	CardLockedFailedResult(),					# 已封号的卡
							csdefine.RECHANGE_LOGGED_FALID					:	LoggedFailedResult(),						# 写入充值日志失败
							csdefine.RECHANGE_CARD_NOT_EXIST_CARD			:	CardNotExistFailedResult(),					# 卡不存在 或 卡未激活
							csdefine.RECHANGE_SEND_YUANBAO_FAILED			:	SendYuanbaoFailedResult(),					# 操作成功，但是发放元宝失败
							csdefine.RECHANGE_THIRTY						:	SuccessResult(),							# 30元面值的卡
							csdefine.RECHANGE_CARD_VALUE_FAILED				:	CardValueFailedResult(),					# 面值不符
							csdefine.RECHANGE_OVERTIME_FAILED				:	OverTimeResult(),							# 超时处理
						}


OVERTIME_RESULT_PROCESSES = {	csdefine.OVERTIME_OVERTIME_FAILED			:	OverTimeCheckOverTime(),					# 超时检测还是超时
							csdefine.OVERTIME_RECHANGE_SUCCESS				:	OverTimeCheckSuccess(),						# 超时检测充值成功
							csdefine.OVERTIME_RECHANGE_FAILED				:	OverTimeCheckFailed(),						# 超时检测充值失败
							csdefine.OVERTIME_NO_ORDER_FAILED				:	OverTimeCheckOrderFailed(),					# 超时检测没有这个订单号
						}



class PointCardDataBaseControl:
	"""
	"""
	def __init__( self ):
		"""
		"""
		query = """CREATE TABLE IF NOT EXISTS `custom_PointCardsTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_isSelling`		BIGINT(20),
				`sm_buyerName`		text not null,
				`sm_buyerAccount`	text not null,
				`sm_price`		 	BIGINT(20),
				`sm_cardNo`			text not null,
				`sm_passWord` 		text not null,
				`sm_orderID`		text not null,
				`sm_sellTime` 		text not null,
				`sm_serverName`	 	text not null,
				`sm_salesName`	 	text not null,
				`sm_salesIP`		BIGINT(20),
				`sm_parValue`	 	BIGINT(20),
				`sm_salesAccount` 	text not null,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

	def initCards( self, mgr ):
		"""
		"""
		query = "select * from custom_PointCardsTable"
		BigWorld.executeRawDatabaseCommand( query, Functor( self._onInitCards, mgr ) )



	def saveSellCard( self, card ):
		"""
		"""
		paramTuple = ( card.cardNo, card.passWord, card.sellTime, card.price, card.orderID, card.serverName, card.salesName, card.salesAccount, card.salesIP, card.parValue )
		#print paramTuple
		#print "( 0, \'%s\',\'%s\',%i, %i, %i,\'%s\',\'%s\',%i,\'%s\' )"
		query = "insert into custom_PointCardsTable( sm_isSelling, sm_cardNo,sm_passWord,sm_sellTime,sm_price,sm_orderID,sm_serverName,sm_salesName,sm_salesAccount, sm_salesIP,sm_parValue )Value ( 0, \'%s\',\'%s\',%i, %i, \'%s\',\'%s\',\'%s\',\'%s\',%i,\'%s\' )"%paramTuple
		BigWorld.executeRawDatabaseCommand( query, self.__onSaveSellCard )

	def saveSellingCard( self, card ):
		"""
		"""
		query = "update custom_PointCardsTable set sm_isSelling = 1, sm_buyerName = \'%s\', sm_buyerAccount = \'%s\' where sm_cardNo = \'%s\'"%( card.buyerName, card.buyerAccount, card.cardNo )
		BigWorld.executeRawDatabaseCommand( query, self.__onSaveSellingCard )

	def takeOffCard( self, cardNo ):
		"""
		"""
		query = "delete from custom_PointCardsTable where sm_cardNo =  \'%s\'"%cardNo
		BigWorld.executeRawDatabaseCommand( query, self.__onTakeOffCard)

	def cancelSellingState( self, cardNo ):
		"""
		"""
		query = "update custom_PointCardsTable set sm_isSelling = 0, sm_buyerName = \'%s\', sm_buyerAccount = \'%s\' where sm_cardNo = \'%s\'"%( "", "", cardNo )
		BigWorld.executeRawDatabaseCommand( query, self.__onCancelSellingState )


	def __createTableCB( self, result, rows, errstr ):
		"""
		生成数据库表格回调函数

		param tableName:	生成的表格名字
		type tableName:		STRING
		"""
		if errstr:
			# 生成表格错误的处理
			ERROR_MSG( "Create table fault! %s" % errstr  )
			return


	def _onInitCards( self, mgr, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "PointCardDataBaseControl: init sell card failed!" )
			return

		for i in result:
			print i
			card 				= PointCardInfo()
			card.isSelling		= int(i[1])
			card.buyerName 		= i[2]
			card.buyerAccount	= i[3]
			card.price			= int(i[4])
			card.cardNo			= i[5]
			card.passWord		= i[6]
			card.orderID		= i[7]
			card.sellTime		= int(i[8])
			card.serverName		= i[9]
			card.salesName		= i[10]
			card.salesIP		= int(i[11])
			card.parValue		= i[12]
			card.salesAccount	= i[13]


			if time.time() - card.sellTime  > CARD_VALID_TIME:
				BigWorld.globalData["MailMgr"].send( None, card.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_15, cschannel_msgs.POINT_CARD_INFO_16, 0, "" )
				mgr.dbc.takeOffCard( card.cardNo )
				continue

			if card.isSelling == 0:
				mgr.addCurrentSellCard( card )
			else:
				mgr.addOverTimeCard( card )

	def __onSaveSellCard( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "PointCardDataBaseControl: insert new sell card failed!" )
			return

	def __onSaveSellingCard( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "PointCardDataBaseControl: insert new selling card failed!" )
			return


	def __onTakeOffCard( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "PointCardDataBaseControl: take off card failed!" )
			return

	def __onCancelSellingState( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "PointCardDataBaseControl: remove card selling state failed!" )
			return


class PointCardMgr( BigWorld.Base ):
	#点卡寄售管理器
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.currentSellCards 			= {}					#正在寄售的卡，寄售中
		self.requestVendCardNos			= []					#请求交易列表	key: 点卡ID， value: 角色信息
		self.overTimeCards				= {}					#通讯超时的卡
		self.overAndOverTimeCards 		= {}					#通讯超时又超时的卡
		self.vendTimerID 				= 0						#交易timerID (用于限定交易数量)
		self.overTimeTimerID 			= 0						#处理超时充值的timerID
		self.canOperate					= True					#速度控制
		self.dbc = PointCardDataBaseControl()					#数据库操作
		self.chargeInstance = PointCharge()
		self.threadMgr = BackgroundTask.Manager()				#线程管理器
		self.threadMgr.startThreads( 10 )						#开启10条线程
		self.registerGlobally( "PointCardMgr", self._onRegisterManager )

		self._initCardsFromDB()
		self.addTimer( OUTOFDATECHECKSPEED, OUTOFDATECHECKSPEED, HANDLE_CARD_OUT_OF_DATE_CBID )

	#---------------------------------- 接口 ---------------------------------------------------------
	def sellPointCard( self, cardInfo, playerBaseMB ):
		"""
		defined method
		玩家寄售点卡
		"""
		if not self._checkOperate():
			return
		self._addOperateLimit()
		cardInfo.cardNo = cardInfo.cardNo.lower()
		if cardInfo.cardNo in self.currentSellCards or cardInfo.cardNo in self.overTimeCards or cardInfo.cardNo in self.overAndOverTimeCards:
			playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_SELLING, str(( cardInfo.cardNo, )) )
			return

		useful,value = self._checkCard( cardInfo )

		if useful:
			cardInfo.sellTime = int(time.time())
			cardInfo.parValue = value
			id = str(newUID())
			for i in xrange( 0, 20 - len( id ) ):
				id = '0'+id
			cardInfo.orderID 		= id
			self.addCurrentSellCard( cardInfo )
			self._saveToDatabase( cardInfo )
			playerBaseMB.cell.onSellPointCard()																		#存储到数据库中
			INFO_MSG("New Sell Card: No:%s, pwd:%s, serverName:%s, salesName:%s,  IP:%s"%(cardInfo.cardNo, cardInfo.passWord, cardInfo.serverName, cardInfo.salesName, cardInfo.salesIP  ))
			playerBaseMB.client.onAddPointCard( cardInfo )
			playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_SELL_SUCCESS, str(( cardInfo.cardNo, )) )
			jin	 = cardInfo.price/10000
			yin  = cardInfo.price/100 - jin*100
			tong = cardInfo.price - jin*10000 - yin*100
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_POINTCARD_SELLED_NOTICE_01%( jin, yin, tong, int( cardInfo.parValue ) * 100 ), [] )
		else:
			playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_INFO_NOT_CORRECT, str(( cardInfo.cardNo, )) )


	def buyPointCard( self, cardNo, money, playerBaseMB, playerName, buyerAccount ):
		"""
		define method
		玩家购买点卡
		"""
		if not self._checkOperate():
			return
		self._addOperateLimit()
		cardNo = cardNo.lower()
		if cardNo not in self.currentSellCards:
			playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_NOT_EXIST, "" )
			return
		cardInfo = self.currentSellCards[cardNo]
		if cardInfo.isSelling:
			playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_SELLING, str(( cardInfo.cardNo, )) )
			return
		if money < cardInfo.price:
			playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_NOT_ENOUGH_MONEY, "" )
			return
		if playerName == cardInfo.salesName:
			playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_NOT_BUY_SELF_CARD, "" )
			return

		cardInfo.isSelling 		= 1									#标记卡处于买卖状态
		cardInfo.buyerName  	= playerName
		cardInfo.buyerAccount 	= buyerAccount						#买者信息

		playerBaseMB.cell.onBuyPointCard( cardInfo.price )
		playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_TRADE_HANDLEING,"" )
		playerBaseMB.client.removePointCard( cardNo )


		self._buyCard( cardInfo )

	def addCurrentSellCard( self, cardInfo ):
		"""
		把卡加入到出售列表
		"""
		self.currentSellCards[cardInfo.cardNo] = cardInfo

	def addOverTimeCard( self, cardInfo ):
		"""
		"""
		self.overTimeCards[cardInfo.cardNo] = cardInfo

		if self.overTimeTimerID == 0:
			self.overTimeTimerID = self.addTimer( OVERTIME, 0.0, HANDLE_CARD_OVERTIME_CBID )

	def cancelSellingState( self, card ):
		"""
		取消点卡的买卖状态
		"""
		card.isSelling 	= 0
		card.buyerName 	= ""
		card.buyerAccount = ""

		self.addCurrentSellCard( card )
		self.dbc.cancelSellingState( card.cardNo )

	def takeOffCard( self, cardNo ):
		"""
		下架
		"""
		if cardNo in self.currentSellCards:
			del self.currentSellCards[cardNo]
		if cardNo in self.overTimeCards:
			del self.overTimeCards[cardNo]
		if cardNo in self.overAndOverTimeCards:
			del self.overAndOverTimeCards[cardNo]
		self.dbc.takeOffCard( cardNo )


	def queryPointCards( self, playerBaseMB, page ):
		"""
		"""
		minPos = csconst.POINT_CARD_PAGE_SIZE * page
		l = len( self.currentSellCards )

		if minPos > l - 1:
			return

		maxPos = min( minPos + csconst.POINT_CARD_PAGE_SIZE, l )

		for i in self.currentSellCards.values()[minPos:maxPos]:
			playerBaseMB.client.onReceivePointCard( i )


	def queryPointCardsByValue( self, playerBaseMB, page, value ):
		"""
		"""
		minPos = csconst.POINT_CARD_PAGE_SIZE * page

		valueCards = [e for e in self.currentSellCards.itervalues() if e.parValue == value ]


		l = len( valueCards )

		if minPos > l - 1:
			return

		maxPos = min( minPos + csconst.POINT_CARD_PAGE_SIZE, l )

		for i in valueCards[minPos:maxPos]:
			playerBaseMB.client.onReceivePointCard( i )



	#---------------------------------- 私有方法 ---------------------------------------------------------
	def _initCardsFromDB( self ):
		"""
		"""
		self.dbc.initCards( self )

	def _checkCard( self, cardInfo ):
		"""
		检查卡的有效性
		"""
		return self.chargeInstance.easyCardRule( cardInfo )

	def _buyCard( self, cardInfo ):
		"""
		买卡
		"""
		self.requestVendCardNos.append( cardInfo.cardNo )
		if self.vendTimerID == 0:
			self.vendTimerID = self.addTimer( 0.0, 0.0, HANDLE_CARD_SELLING_CBID )


	def _saveToDatabase( self, cardInfo ):
		"""
		存储到数据库中
		"""
		self.dbc.saveSellCard( cardInfo )


	def _checkOperate( self ):
		"""
		"""
		return self.canOperate

	def _addOperateLimit( self ):
		"""
		"""
		self.canOperate = False
		self.addTimer( 0.5, 0, OPERATE_CONTROL_CBID )

	#---------------------------------- 回调方法 ---------------------------------------------------------
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register PointCardMgr Fail!" )
			self.registerGlobally( "PointCardMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["PointCardMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("PointCardMgr Create Complete!")

	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == HANDLE_CARD_SELLING_CBID:
			cardNo = self.requestVendCardNos.pop(0)
			self.dbc.saveSellingCard( self.currentSellCards[cardNo] )
			card = self.currentSellCards[cardNo]
			del self.currentSellCards[cardNo]
			self.threadMgr.addBackgroundTask( RechargeThread( card ) )
			if len( self.requestVendCardNos ) > 0:
				self.vendTimerID = self.addTimer( 1.0, 0.0, HANDLE_CARD_SELLING_CBID )
			else:
				self.vendTimerID = 0

		elif userArg == HANDLE_CARD_OVERTIME_CBID:
			cardNo = self.overTimeCards.keys()[0]
			card = self.overTimeCards[cardNo]
			del self.overTimeCards[cardNo]
			self.threadMgr.addBackgroundTask( OverTimeThread( card ) )
			if len( self.overTimeCards ) > 0:
				self.overTimeTimerID = self.addTimer( OVERTIME, 0.0, HANDLE_CARD_OVERTIME_CBID )
			else:
				self.overTimeTimerID = 0

		elif userArg == HANDLE_CARD_OVERANDOVERTIME_CBID:
			cardNo = self.overAndOverTimeCards.keys()[0]
			card = self.overAndOverTimeCards[cardNo]
			del self.overAndOverTimeCards[cardNo]
			self.overTimeCards.append( card )
			if self.overTimeTimerID == 0:
				self.overTimeTimerID = self.addTimer( OVERTIME, 0.0, HANDLE_CARD_OVERTIME_CBID )

		elif userArg == OPERATE_CONTROL_CBID:
			self.canOperate = True


		elif userArg == HANDLE_CARD_OUT_OF_DATE_CBID:
			curtime = time.time()
			outDateInfos = []
			for cardNo in self.currentSellCards:
				if curtime - self.currentSellCards[cardNo].sellTime  > CARD_VALID_TIME:
					outDateInfos.append( (cardNo, self.currentSellCards[cardNo].salesName) )

			for cardNo in self.overTimeCards:
				if curtime - self.overTimeCards[cardNo].sellTime  > CARD_VALID_TIME:
					outDateInfos.append( (cardNo,  self.overTimeCards[cardNo].salesName ) )

			for cardNo in self.overAndOverTimeCards:
				if curtime - self.overAndOverTimeCards[cardNo].sellTime  > CARD_VALID_TIME:
					outDateInfos.append( ( cardNo,  self.overAndOverTimeCards[cardNo].salesName ) )

			for cardNo, salesName in outDateInfos:
				BigWorld.globalData["MailMgr"].send( None, salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_15, cschannel_msgs.POINT_CARD_INFO_16%cardNo, 0, "" )
				self.takeOffCard( cardNo )


	def onReCharge( self, cardInfo ):
		"""
		充值处理回调
		"""
		if cardInfo.result in RECHARGE_RESULT_PROCESSES:
			RECHARGE_RESULT_PROCESSES[cardInfo.result].do( cardInfo, self )
		else:
			RECHARGE_RESULT_PROCESSES[csdefine.RECHANGE_FAILED].do( cardInfo, self )


	def onOverTime( self, cardInfo ):
		"""
		超时回调处理
		"""
		OVERTIME_RESULT_PROCESSES[cardInfo.overTimeResult].do( cardInfo, self )

	def onOverTimeAgain( self, cardInfo ):
		"""
		超时又超时回调处理
		"""
		self.overAndOverTimeCards[cardInfo.cardNo] = cardInfo
		self.addTimer( OVERANDOVERTIME, 0.0, HANDLE_CARD_OVERANDOVERTIME_CBID )




