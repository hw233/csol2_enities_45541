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


socket.setdefaulttimeout(5.0)	#���ó�ʱʱ��

HANDLE_CARD_SELLING_CBID 			= 10000		#������
HANDLE_CARD_OVERTIME_CBID			= 10001		#����ʱ
HANDLE_CARD_OVERANDOVERTIME_CBID 	= 10002		#��ʱ��������Ȼ��ʱ
OPERATE_CONTROL_CBID 				= 10003		#�ٶȿ��ƻص�
HANDLE_CARD_OUT_OF_DATE_CBID		= 10004		#���ڵ㿨���ص�


OUTOFDATECHECKSPEED			= 3600.0			#���ڵ㿨���
OVERTIME			= 60.0
OVERANDOVERTIME		= 3600.0

CARD_VALID_TIME		= 24 * 3600		# һ��

#BigWorld.globalData["pointCardWord"] = "tempString"
#BigWorld.globalData["pointCardAddr"]					#��ֵ�˿� �磺http://transfer.gyyx.cn:81/CsServiceTest/CSCarConsignment.asmx
#BigWorld.globalData["pointCardWord"]					#��ֵУ����
class PointCharge:
	def easyCardRule( self, cardInfo ):
		"""
		#����򵥵ĵ㿨�����ж�
		�򵥹���
			20����ĸ��ǰ4����ĸΪhaaa,��5����ĸ����㿨��ֵ��6-20�������
			��ĸ����ĵ㿨��ֵΪ��
			E       10.0 ����10Ԫ��ֵ��(������)

			F       30.0 ����30Ԫ��ֵ��(������)

			B       10.0 ����10Ԫ��ֵ��

			D      30.0 ����30Ԫ��ֵ��

			P       10.0 ��Ѷ10Ԫ��ֵ��

		@return  (bool�� value)
			1.�Ƿ���Ч
			2.������ֵ
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
		��ֵ
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
		#���� + ���� + ������ + �û��� + �������� + ����������� + ����IP + ��ֵ + BigWorld.globalData["pointCardWord"]
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
	��ʱ����
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
	��ֵ�߳�
	"""
	def __init__( self, cardInfo ):
		"""
		"""
		self.cardInfo = cardInfo
		BackgroundTask.BackgroundTask.__init__( self )


	def doBackgroundTask( self, mgr ):
		#��ȡ��ҳ�ַ�
		#��Ч->�ر���ҳ�ַ�
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
	����ʱ�߳�
	"""
	def __init__( self, cardInfo ):
		"""
		"""
		self.cardInfo = cardInfo
		BackgroundTask.BackgroundTask.__init__( self )


	def doBackgroundTask( self, mgr ):
		#��ȡ��ҳ�ַ�
		#��Ч->�ر���ҳ�ַ�
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
	��ֵ�ɹ�
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "�忨�ɹ�"
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
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		jin	= price/10000
		yin = price/100 - jin*100
		tong = price - jin*10000 - yin*100
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_SUCCESSFUL, str(( cardNo, jin, yin, tong, )) )
		BigWorld.lookUpBaseByName( "Role", buyerName, Functor( self._onCardBuySuccessful, parValue ) )

	def _onCardBuySuccessful( self, parValue, callResult ):
		"""
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
			count = str( int( parValue ) * 100 )
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_BUY_SUCCESSFUL, str( (count, )) )




class NoOrPwdFailedResult( RechargeResultHandle ):
	"""
	�ʺź���������³�ֵʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "�ʺź���������³�ֵʧ��"
		ERROR_MSG( "���۵㿨�����ʺź���������³�ֵʧ�ܡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_6%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )

		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )

class UsedFailedResult( RechargeResultHandle ):
	"""
	�㿨�Ѿ�ʹ�õ��³�ֵʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "���۵㿨���󣺵㿨�Ѿ�ʹ�õ��³�ֵʧ�ܡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_9%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )

		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )

class AccountNotActivitiedFailedResult( RechargeResultHandle ):
	"""
	�ʺ��ڸ���û�м���³�ֵʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "�ʺ��ڸ���û�м���³�ֵʧ��"
		ERROR_MSG( "���۵㿨���������ϲ������ʺ��ڸ���û�м���³�ֵʧ�ܵķ��أ��������ڷ����ˡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )

class AccountNotHaveFailedResult( RechargeResultHandle ):
	"""
	û������ʺŵ��³�ֵʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "û������ʺŵ��³�ֵʧ��"
		ERROR_MSG( "���۵㿨���������ϲ�����'û������ʺ�'���³�ֵʧ�ܵķ��أ��������ڷ����ˡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class RechangeFailedResult( RechargeResultHandle ):
	"""
	��ͨ��ֵʧ�ܣ�δ֪����
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "��ͨ��ֵʧ��"
		ERROR_MSG( "���۵㿨����δ֪ԭ��ĳ�ֵʧ�ܡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class MD5FailedResult( RechargeResultHandle ):
	"""
	MD5���ʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "MD5���ʧ��"
		ERROR_MSG( "���۵㿨���������ϲ�����'MD5���ʧ��'���³�ֵʧ�ܵķ��أ��������ڷ����ˡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class ParamsFailedResult( RechargeResultHandle ):
	"""
	������������ֵ����
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "������������ֵ����"
		ERROR_MSG( "���۵㿨���������ϲ�����'������������ֵ����'���³�ֵʧ�ܵķ��أ��������ڷ����ˡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )




class ServerNameFailedResult( RechargeResultHandle ):
	"""
	�����ڵķ���������ֵ����
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "�����ڵķ���������ֵ����"
		ERROR_MSG( "���۵㿨���󣺷��������ֲ��ԡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class OrderDuplicateFailedResult( RechargeResultHandle ):
	"""
	�����ظ���ֵ����
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "�����ظ���ֵ����"

		ERROR_MSG( "���۵㿨�������ɵ���������ظ�������(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )




class IPFailedResult( RechargeResultHandle ):
	"""
	IP���󣬷������������ͷ�������IP��Ӧ����
	�������������
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "IP���󣬷������������ͷ�������IP��Ӧ����"
		ERROR_MSG( "���۵㿨����IP���󣬷������������ͷ�������IP��Ӧ���ϡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )




class AccountMsgFailedResult( RechargeResultHandle ):
	"""
	��ȡ�ʺ���Ϣʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "���۵㿨���󣺻�ȡ�ʺ���Ϣʧ�ܡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class CardLockedFailedResult( RechargeResultHandle ):
	"""
	�ѷ�ŵĿ�
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "�ѷ�ŵĿ�"
		ERROR_MSG( "���۵㿨�����ѷ�ŵĿ�������(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_11%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )


		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )



class LoggedFailedResult( RechargeResultHandle ):
	"""
	д���ֵ��־ʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "���۵㿨����д���ֵ��־ʧ�ܡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )


class CardNotExistFailedResult( RechargeResultHandle ):
	"""
	�������� �� ��δ����
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "���۵㿨���󣺿������� �� ��δ�������(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_12%cardInfo.cardNo, 0, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_13, cardInfo.price, "" )

		BigWorld.lookUpBaseByName( "Role", cardInfo.salesName, Functor( self._onCardSellFailed, cardInfo.cardNo  ) )


	def _onCardSellFailed( self, cardNo, callResult ):
		"""
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
			playerBase.client.onStatusMessage( csstatus.POINT_CARD_SELL_FAILED, str( (cardNo, )) )


class SendYuanbaoFailedResult( RechargeResultHandle ):
	"""
	�����ɹ������Ƿ���Ԫ��ʧ��
	�������Ϊ�ɹ��������ֵ���ֻ�������ԣ�ֱ���ɹ���
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "�����ɹ������Ƿ���Ԫ��ʧ��"
		ERROR_MSG( "���۵㿨���󣺲����ɹ������Ƿ���Ԫ��ʧ�ܡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.takeOffCard( cardInfo.cardNo )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_1, cschannel_msgs.POINT_CARD_INFO_2%cardInfo.cardNo, cardInfo.price + csconst.SELL_POINT_CARD_YAJIN, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_3, cschannel_msgs.POINT_CARD_INFO_4, 0, "" )



class CardValueFailedResult( RechargeResultHandle ):
	"""
	��ֵ����
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		#print "��ֵ����"
		ERROR_MSG( "���۵㿨���������ϲ����ڡ���ֵ������������أ��������ڷ����ˡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.salesName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_5, cschannel_msgs.POINT_CARD_INFO_14%cardInfo.cardNo, cardInfo.price + csconst.SELL_POINT_CARD_YAJIN, "" )

		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_8, cardInfo.price, "" )

		pointCardMgr.takeOffCard( cardInfo.cardNo )

class OverTimeResult( RechargeResultHandle ):
	"""
	��ֵ��ʱ
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "���۵㿨���󣺳�ֵ��ʱ������(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		pointCardMgr.addOverTimeCard( cardInfo )


class OverTimeCheckHandle:
	"""
	��ʱ����
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
	��ʱ�����س�ʱ
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		pointCardMgr.onOverTimeAgain( cardInfo )


class OverTimeCheckSuccess( OverTimeCheckHandle ):
	"""
	��ʱ�����سɹ�
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
	��ʱ������ʧ��
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "���۵㿨����δ֪ԭ��ĳ�ֵʧ�ܡ�����(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )



class OverTimeCheckOrderFailed( OverTimeCheckHandle ):
	"""
	��ʱ������û���������
	"""
	def do( self, cardInfo, pointCardMgr):
		"""
		"""
		ERROR_MSG( "���۵㿨���󣺳�ʱ������û���������������(%s), ����(%s), ����(%s)"%(cardInfo.cardNo, cardInfo.salesName, cardInfo.buyerName) )
		BigWorld.globalData["MailMgr"].send( None, cardInfo.buyerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
						cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.POINT_CARD_INFO_7, cschannel_msgs.POINT_CARD_INFO_10, cardInfo.price, "" )

		pointCardMgr.cancelSellingState( cardInfo )



#��ֵ���ش���
RECHARGE_RESULT_PROCESSES = {	csdefine.RECHANGE_SUCCESS					:	SuccessResult(),							# �㿨���۳ɹ�
							csdefine.RECHANGE_NO_OR_PWD_FAILED				:	NoOrPwdFailedResult(),						# ���Ż��������
							csdefine.RECHANGE_USED_FAILED					:	UsedFailedResult(),							# ��ʹ�õĿ�
							csdefine.RECHANGE_ACCOUNT_NOT_ACTIVITIED_FAILED	:	AccountNotActivitiedFailedResult(),			# �ʺ�δ�ڸ�������
							csdefine.RECHANGE_ACCOUNT_NOT_HAVE_FAILED		:	AccountNotHaveFailedResult(),				# �ʺŲ�����
							csdefine.RECHANGE_FAILED						:	RechangeFailedResult(),						# ��ֵʧ��
							csdefine.RECHANGE_MD5_FAILED					:	MD5FailedResult(),							# MD5У��ʧ��
							csdefine.RECHANGE_PARAMS_FAILED					:	ParamsFailedResult(),						# ����������
							csdefine.RECHANGE_SERVER_NAME_FAILED			:	ServerNameFailedResult(),					# �����ڵķ�������
							csdefine.RECHANGE_OVER_DUPLICATE_FAILED			:	OrderDuplicateFailedResult(),				# �������ظ�
							csdefine.RECHANGE_TEN_YUAN						:	SuccessResult(),							# 10Ԫ��ֵ�Ŀ�
							csdefine.RECHANGE_IP_FAILED						:	IPFailedResult(),							# IP���󣬷������������ͷ�������IP��Ӧ����
							csdefine.RECHANGE_ACCOUNT_MSG_FALIED			:	AccountMsgFailedResult(),					# ��ȡ�ʺ���Ϣʧ��
							csdefine.RECHANGE_CARD_LOCKED_CARD				:	CardLockedFailedResult(),					# �ѷ�ŵĿ�
							csdefine.RECHANGE_LOGGED_FALID					:	LoggedFailedResult(),						# д���ֵ��־ʧ��
							csdefine.RECHANGE_CARD_NOT_EXIST_CARD			:	CardNotExistFailedResult(),					# �������� �� ��δ����
							csdefine.RECHANGE_SEND_YUANBAO_FAILED			:	SendYuanbaoFailedResult(),					# �����ɹ������Ƿ���Ԫ��ʧ��
							csdefine.RECHANGE_THIRTY						:	SuccessResult(),							# 30Ԫ��ֵ�Ŀ�
							csdefine.RECHANGE_CARD_VALUE_FAILED				:	CardValueFailedResult(),					# ��ֵ����
							csdefine.RECHANGE_OVERTIME_FAILED				:	OverTimeResult(),							# ��ʱ����
						}


OVERTIME_RESULT_PROCESSES = {	csdefine.OVERTIME_OVERTIME_FAILED			:	OverTimeCheckOverTime(),					# ��ʱ��⻹�ǳ�ʱ
							csdefine.OVERTIME_RECHANGE_SUCCESS				:	OverTimeCheckSuccess(),						# ��ʱ����ֵ�ɹ�
							csdefine.OVERTIME_RECHANGE_FAILED				:	OverTimeCheckFailed(),						# ��ʱ����ֵʧ��
							csdefine.OVERTIME_NO_ORDER_FAILED				:	OverTimeCheckOrderFailed(),					# ��ʱ���û�����������
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
		�������ݿ���ص�����

		param tableName:	���ɵı������
		type tableName:		STRING
		"""
		if errstr:
			# ���ɱ�����Ĵ���
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
	#�㿨���۹�����
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.currentSellCards 			= {}					#���ڼ��۵Ŀ���������
		self.requestVendCardNos			= []					#�������б�	key: �㿨ID�� value: ��ɫ��Ϣ
		self.overTimeCards				= {}					#ͨѶ��ʱ�Ŀ�
		self.overAndOverTimeCards 		= {}					#ͨѶ��ʱ�ֳ�ʱ�Ŀ�
		self.vendTimerID 				= 0						#����timerID (�����޶���������)
		self.overTimeTimerID 			= 0						#����ʱ��ֵ��timerID
		self.canOperate					= True					#�ٶȿ���
		self.dbc = PointCardDataBaseControl()					#���ݿ����
		self.chargeInstance = PointCharge()
		self.threadMgr = BackgroundTask.Manager()				#�̹߳�����
		self.threadMgr.startThreads( 10 )						#����10���߳�
		self.registerGlobally( "PointCardMgr", self._onRegisterManager )

		self._initCardsFromDB()
		self.addTimer( OUTOFDATECHECKSPEED, OUTOFDATECHECKSPEED, HANDLE_CARD_OUT_OF_DATE_CBID )

	#---------------------------------- �ӿ� ---------------------------------------------------------
	def sellPointCard( self, cardInfo, playerBaseMB ):
		"""
		defined method
		��Ҽ��۵㿨
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
			playerBaseMB.cell.onSellPointCard()																		#�洢�����ݿ���
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
		��ҹ���㿨
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

		cardInfo.isSelling 		= 1									#��ǿ���������״̬
		cardInfo.buyerName  	= playerName
		cardInfo.buyerAccount 	= buyerAccount						#������Ϣ

		playerBaseMB.cell.onBuyPointCard( cardInfo.price )
		playerBaseMB.client.onStatusMessage( csstatus.POINT_CARD_TRADE_HANDLEING,"" )
		playerBaseMB.client.removePointCard( cardNo )


		self._buyCard( cardInfo )

	def addCurrentSellCard( self, cardInfo ):
		"""
		�ѿ����뵽�����б�
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
		ȡ���㿨������״̬
		"""
		card.isSelling 	= 0
		card.buyerName 	= ""
		card.buyerAccount = ""

		self.addCurrentSellCard( card )
		self.dbc.cancelSellingState( card.cardNo )

	def takeOffCard( self, cardNo ):
		"""
		�¼�
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



	#---------------------------------- ˽�з��� ---------------------------------------------------------
	def _initCardsFromDB( self ):
		"""
		"""
		self.dbc.initCards( self )

	def _checkCard( self, cardInfo ):
		"""
		��鿨����Ч��
		"""
		return self.chargeInstance.easyCardRule( cardInfo )

	def _buyCard( self, cardInfo ):
		"""
		��
		"""
		self.requestVendCardNos.append( cardInfo.cardNo )
		if self.vendTimerID == 0:
			self.vendTimerID = self.addTimer( 0.0, 0.0, HANDLE_CARD_SELLING_CBID )


	def _saveToDatabase( self, cardInfo ):
		"""
		�洢�����ݿ���
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

	#---------------------------------- �ص����� ---------------------------------------------------------
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register PointCardMgr Fail!" )
			self.registerGlobally( "PointCardMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["PointCardMgr"] = self		# ע�ᵽ���еķ�������
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
		��ֵ����ص�
		"""
		if cardInfo.result in RECHARGE_RESULT_PROCESSES:
			RECHARGE_RESULT_PROCESSES[cardInfo.result].do( cardInfo, self )
		else:
			RECHARGE_RESULT_PROCESSES[csdefine.RECHANGE_FAILED].do( cardInfo, self )


	def onOverTime( self, cardInfo ):
		"""
		��ʱ�ص�����
		"""
		OVERTIME_RESULT_PROCESSES[cardInfo.overTimeResult].do( cardInfo, self )

	def onOverTimeAgain( self, cardInfo ):
		"""
		��ʱ�ֳ�ʱ�ص�����
		"""
		self.overAndOverTimeCards[cardInfo.cardNo] = cardInfo
		self.addTimer( OVERANDOVERTIME, 0.0, HANDLE_CARD_OVERANDOVERTIME_CBID )




