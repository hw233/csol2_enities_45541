# -*- coding: gb18030 -*-

"""
�㿨����client���Խű�
���Խӿڣ�
	cell/Role.py
		class Role
			sellPointCard
			buyPointCard
"""

from PointCardInfo import PointCardInfo
import BigWorld
from Function import Functor


cardsInfo = {
			0 : { "cardNo" 	: '1234567', 				"password" : 'ttue', 		"price" : 1000, 	"serverName" : "����֮��",
			"sellResult"	: "��ϵͳ���㿨�����ţ�1234567����Ϣ����ȷ�����������롣",
			"buyResult"		: "��ϵͳ���õ㿨�����ڻ����Ѿ������ߡ�",
			"info"			: "���ſ��Ŀ���С��20λ������Ӧ����ʧ�ܵ�"},

			1 : { "cardNo" 	: '12345678901234567890', 	"password" : 'ttue', 		"price" : 1000, 	"serverName" : "����֮��",
			"sellResult"	: "��ϵͳ���㿨�����ţ�12345678901234567890����Ϣ����ȷ�����������롣",
			"buyResult"		: "��ϵͳ���õ㿨�����ڻ����Ѿ������ߡ�",
			"info"			: "���ſ��Ŀ���ǰ4λ����'haaa',����Ӧ����ʧ�ܵ�"},

			2 : { "cardNo" 	: 'HAAAW000000154587797', 	"password" : 'ttue', 		"price" : 1000, 	"serverName" : "����֮��",
			"sellResult"	: "��ϵͳ���㿨�����ţ�HAAAW000000154587797����Ϣ����ȷ�����������롣",
			"buyResult"		: "��ϵͳ���õ㿨�����ڻ����Ѿ������ߡ�",
			"info"			: "���ſ��Ŀ��ŵ�5λ����ֵ������[e,f,b,d,p]�е�����һ��,����Ӧ����ʧ�ܵ�"},


			3 : { "cardNo"  : 'HAAAB000000156816952', 	"password" : 'ttue', 	"price" : 1000, 	"serverName" : "����֮��",
			"sellResult"	:"��ϵͳ���㿨�����ţ�HAAAB000000156816952�����۳ɹ�����ϵͳ����ʧȥ5��ҡ�",
			"buyResult"		:"��ʾ�鿴�ʼ����鿴�ʼ���������Ѻ��û�գ�����ȡ�ؽ�Ǯ",
			"info"			: "���ſ������벻��ȷ,�����ǳɹ��ģ�������ʧ�ܵġ���Ʒ�¼ܣ�������Ѻ��û�գ�����ͨ���ʼ���ȡ���á�"},


			4 : { "cardNo"  : 'HAAAB000000154587798', 	"password" : 'RUFSXKBD', 	"price" : 1000, 	"serverName" : "����֮��",
			"sellResult"	:"��ϵͳ���㿨�����ţ�HAAAB000000154587798�����۳ɹ�����ϵͳ����ʧȥ5��ҡ�",
			"buyResult"		:"��ʾ�鿴�ʼ����鿴�ʼ���������Ѻ��û�գ�����ȡ�ؽ�Ǯ",
			"info"			: "���ſ����ù���,���۳ɹ���������ʧ�ܵġ���Ʒ�¼ܣ�������Ѻ��û�գ�����ͨ���ʼ���ȡ����"},


			5 : { "cardNo"  : 'HAAAD000000158577331', 	"password" : 'IPOLCLCG', 	"price" : 1000, 	"serverName" : "����С��",
			"sellResult"	:"��ϵͳ���㿨�����ţ�HAAAB000000154587798�����۳ɹ�����ϵͳ����ʧȥ5��ҡ�",
			"buyResult"		:"��ʾ�鿴�ʼ����鿴�ʼ���������Ѻ��û�գ�����ȡ�ؽ�Ǯ",
			"info"			: "���ſ����ù���,���۳ɹ���������ʧ�ܵġ���Ʒ�¼ܣ�������Ѻ��û�գ�����ͨ���ʼ���ȡ����"},
			}


def makeCards():
	"""
	���쿨
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
	���ۿ�
	"""
	card = cards[num]
	BigWorld.player().cell.sellPointCard( card.cardNo, card.passWord, card.serverName, card.price )

def buyCard( num ):
	"""
	����
	"""
	BigWorld.player().cell.buyPointCard( cards[num].cardNo )

def sellCardsFast( minNum, maxNum ):
	"""
	���ٳ���һ����
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.player().cell.sellCard( cards[i] )

def buyCardsFast( minNum, maxNum ):
	"""
	���ٹ���һ����
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.player().cell.buyPointCard( cards[i].cardNo )

def sellCardsSlow( minNum, maxNum ):
	"""
	���ٳ���һ����
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.callback( 2.0 * i, Functor( sellCard, i ) )

def buyCardsSlow( minNum, maxNum ):
	"""
	���ٹ���һ����
	"""
	for i in xrange( minNum, maxNum ):
		BigWorld.callback( 2.0 * i, Functor( buyCard, i ) )