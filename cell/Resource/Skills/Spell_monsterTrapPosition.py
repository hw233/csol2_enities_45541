# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��MonsterTrap��entity(���幦��entity)�������õ�positionλ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *
import random
import string

class Spell_monsterTrapPosition( Spell ):
	"""
	ϵͳ����
	����һ��AreaRestrictTransducer��entity(���幦��entity)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.classNameList = []			# ����monsterTrap��className
		self.lifetime = 0				# ��������ʱ��
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		classNameStr = str( dict[ "param1" ] )
		classNameStrList = classNameStr.split(";")
		for e in classNameStrList:
			self.classNameList.append( e )
		self.lifetime = int( dict[ "param2" ] )
		self.radius = float( dict[ "param3" ] )
		spellStr = str( dict["param4"] )
		self.enterSpell = int( spellStr.split(";")[0] )
		self.leaveSpell = int( spellStr.split(";")[1] )


	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if receiver.isReal():
			spaceBase = BigWorld.cellAppData["spaceID.%i" % receiver.spaceID]
			try:
				spaceEntity = BigWorld.entities[ spaceBase.id ]
			except:
				DEBUG_MSG( "not find the spaceEntity!" )
			
			# �����㣬�����͹�
			spaceEntity.base.spawnMonsters( { "entityName" : random.choice( self.classNameList ), "level": spaceEntity.params["copyLevel"], "radius" : self.radius, "enterSpell" : self.enterSpell, "leaveSpell" : self.leaveSpell, "destroySpell" : self.leaveSpell, "lifetime" : self.lifetime } )
		else:
			receiver.receiveOnReal( caster.id, self )
