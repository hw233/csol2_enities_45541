# -*- coding: gb18030 -*-

"""
点卡寄售client测试脚本
测试接口：
	cell/Role.py
		class Role
			sellPointCard
			buyPointCard
"""

from PointCardInfo import PointCardInfo
import BigWorld
from Function import Functor


cardsInfo = {
			0 : { "cardNo" 	: '1234567', 				"password" : 'ttue', 		"price" : 1000, 	"serverName" : "永恒之光",
			"sellResult"	: "【系统】点卡（卡号：1234567）信息不正确，请重新输入。",
			"buyResult"		: "【系统】该点卡不存在或者已经被买走。",
			"info"			: "这张卡的卡号小于20位，寄售应该是失败的"},

			1 : { "cardNo" 	: '12345678901234567890', 	"password" : 'ttue', 		"price" : 1000, 	"serverName" : "永恒之光",
			"sellResult"	: "【系统】点卡（卡号：12345678901234567890）信息不正确，请重新输入。",
			"buyResult"		: "【系统】该点卡不存在或者已经被买走。",
			"info"			: "这张卡的卡号前4位不是'haaa',寄售应该是失败的"},

			2 : { "cardNo" 	: 'HAAAW000000154587797', 	"password" : 'ttue', 		"price" : 1000, 	"serverName" : "永恒之光",
			"sellResult"	: "【系统】点卡（卡号：HAAAW000000154587797）信息不正确，请重新输入。",
			"buyResult"		: "【系统】该点卡不存在或者已经被买走。",
			"info"			: "这张卡的卡号第5位（面值）不是[e,f,b,d,p]中的任意一个,寄售应该是失败的"},


			3 : { "cardNo"  : 'HAAAB000000156816952', 	"password" : 'ttue', 	"price" : 1000, 	"serverName" : "永恒之光",
			"sellResult"	:"【系统】点卡（卡号：HAAAB000000156816952）寄售成功。【系统】您失去5金币。",
			"buyResult"		:"提示查看邮件，查看邮件结果：买家押金没收，卖家取回金钱",
			"info"			: "这张卡的密码不正确,寄售是成功的，交易是失败的。商品下架，寄售者押金没收，买着通过邮件获取费用。"},


			4 : { "cardNo"  : 'HAAAB000000154587798', 	"password" : 'RUFSXKBD', 	"price" : 1000, 	"serverName" : "永恒之光",
			"sellResult"	:"【系统】点卡（卡号：HAAAB000000154587798）寄售成功。【系统】您失去5金币。",
			"buyResult"		:"提示查看邮件，查看邮件结果：买家押金没收，卖家取回金钱",
			"info"			: "这张卡是用过的,寄售成功，交易是失败的。商品下架，寄售者押金没收，买着通过邮件获取费用"},


			5 : { "cardNo"  : 'HAAAD000000158577331', 	"password" : 'IPOLCLCG', 	"price" : 1000, 	"serverName" : "永恒小光",
			"sellResult"	:"【系统】点卡（卡号：HAAAB000000154587798）寄售成功。【系统】您失去5金币。",
			"buyResult"		:"提示查看邮件，查看邮件结果：买家押金没收，卖家取回金钱",
			"info"			: "这张卡是用过的,寄售成功，交易是失败的。商品下架，寄售者押金没收，买着通过邮件获取费用"},
			}


def makeCards():
	"""
	制造卡
	"""
	global cardsInfo
	cards = []
	for i in cardsInfo.itervalues():
		card = PointCardInfo()
		card.cardNo 	= i["cardNo"]
		card.passWord 	= i["password"]
		card.price		= i["price"]
		card.serverName = i["serverName"]
		card.sellResult = i["sellResult"]
		card.buyResult	= i["buyResult"]
		card.info		= i["info"]
		cards.append( card )
	return cards



cards = makeCards()


def sellCard( num ):
	"""
	出售卡
	"""
	card = cards[num]
	BigWorld.player().cell.sellPointCard( card.cardNo, card.passWord, card.serverName, card.price )

def buyCard( num ):
	"""
	购买卡
	"""
	BigWorld.player().cell.buyPointCard( cards[num].cardNo )

def sellCardsFast( minNum, maxNum ):
	"""
	快速出售一批卡
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.player().cell.sellCard( cards[i] )

def buyCardsFast( minNum, maxNum ):
	"""
	快速购买一批卡
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.player().cell.buyPointCard( cards[i].cardNo )

def sellCardsSlow( minNum, maxNum ):
	"""
	慢速出售一批卡
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.callback( 2.0 * i, Functor( sellCard, i ) )

def buyCardsSlow( minNum, maxNum ):
	"""
	慢速购买一批卡
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.callback( 2.0 * i, Functor( buyCard, i ) )