# -*- coding:gb18030 -*-

from Spell_Item import Spell_Item
from bwdebug import *
import random

class Spell_Item_AICommandRange( Spell_Item ):
	"""
	ͨ��������һ����Χ���ض��Ĺ��﷢��AIָ��
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.classNames = []								# ָ��Ͷ���
		self.commandString = 0								# AIָ��
		self.range = 0.0									# ������Χ
		self.amount = 0										# ��������
		
	def init( self, data ):
		"""
		"""
		Spell_Item.init( self, data )
		self.classNames = data["param1"].split( "|" )
		self.commandString = int( data["param2"] ) if len( data["param2"] ) > 0 else 0
		self.range = float( data["param3"] ) if data["param3"] else 0.0
		self.amount = int( data["param4"] ) if data["param4"] else 0
		
	def receive( self, caster, receiver ):
		"""
		"""
		if  not self.commandString:
			ERROR_MSG( "Skill %i config error, param2 is None "  % self.getID() )
			return
		
		receiver.sendAICommand( receiver.id, self.commandString )							# ���۷��Ͷ����������Χ��ʲô�������߶����Լ���ָ��
		
		if ( len( self.classNames ) == 0 or self.classNames == [""] ) and not self.range: 	# ��classNameΪ�գ��ҷ�ΧΪ0����ֻ�������߷�ָ��
			return
		
		sendList= []
		monsterList = receiver.entitiesInRangeExt( self.range, None, receiver.position )
		for e in monsterList:																# �Ƚ����������Ĺ���ɸѡ����
			if len( self.classNames ) == 0 or self.classNames == [""]:						# ��classNameΪ�գ���Ĭ�ϸ���������ͬ���͵Ĺ��﷢ָ��
				if e.className == receiver.className:
					sendList.append( e )
			else:
				if e.className in self.classNames:											# ��classNames��Ϊ�գ�����AIָ���ָ���Ĺ���
					sendList.append( e )
		
		amount = 1
		while( len( sendList ) ):
			if self.amount and amount >= self.amount:										# ���з����������ƣ����������󷵻�
				return
			i = random.randint( 0, len( sendList ) - 1 )									# ���ѡ����Ŀ��
			e = sendList[ i ]
			e.sendAICommand( e.id, self.commandString )
			amount += 1
			sendList.remove( e )
