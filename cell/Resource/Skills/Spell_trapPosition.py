# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)�������õ�positionλ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *
import random
import string

class Spell_trapPosition( Spell ):
	"""
	ϵͳ����
	����һ��AreaRestrictTransducer��entity(���幦��entity)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.lifetime = 0				# ��������ʱ��
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���
		self.positionList = []			# ���������position list
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.lifetime = int( dict[ "param1" ] )
		self.radius = float( dict[ "param2" ] )
		spellStr = str( dict["param3"] )
		self.enterSpell = int( spellStr.split(";")[0] )
		self.leaveSpell = int( spellStr.split(";")[1] )
		positionStr = str( dict[ "param4" ] )
		positionStrList = positionStr.split(";")
		for e in positionStrList:
			pos = e.split(",")
			self.positionList.append( tuple( (string.atof(pos[0]), string.atof(pos[1]), string.atof(pos[2])) ) )
		self.modelNumber = str( dict[ "param5" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if receiver.isReal():
			dict = { "radius" : self.radius, "enterSpell" : self.enterSpell, "leaveSpell" : self.leaveSpell, "destroySpell" : self.leaveSpell, "modelNumber" : self.modelNumber, "lifetime" : self.lifetime, "uname" : self.getName() }
			index = random.randrange(len(self.positionList))
			trap = caster.createEntityNearPlanes( "AreaRestrictTransducer", self.positionList[index], (0, 0, 0), dict )
			trap.setTemp( "trapArea", { 0:'a',1:'b',2:'c',3:'d',4:'e' }.get(index) )		# ����������±�0 1 2 3 4��5���±꣬���밴˳���Ӧ
			caster.setTemp("trapPosition", self.positionList[index])	# ���������λ�ã�����AI�ߵ����positionλ����
		else:	# �����ghost��֧�֡�17:31 2009-1-16��wsf
			receiver.receiveOnReal( caster.id, self )
