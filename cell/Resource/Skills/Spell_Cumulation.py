# -*- coding:gb18030 -*-

import csstatus
from Spell_BuffNormal import Spell_BuffNormal
from bwdebug import *
import csdefine
from Love3 import g_skills

class Spell_Cumulation( Spell_BuffNormal ):
	"""
	����֮������
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.param1 = 0
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		self.param1 = int( data["param1"] if len( data["param1"] ) > 0 else 0 )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		
		count = receiver.queryTemp( "CUMULATION_COUNT", 0 )
		if count >= self.param1:
			count = self.param1
		if count == 0 :
			self.receiveLinkBuff( caster, receiver )
		else:
			skillID = self.getID()
			skillID += count
			#�Ӷ�Ӧ�ȼ�����̬buff���ۼӣ�
			connectL = g_skills[ skillID ]._buffLink
			for buffData in connectL:
				buff = buffData.getBuff()
				buff.receive( caster, receiver )
		receiver.setTemp( "CUMULATION_COUNT", count + 1 )	