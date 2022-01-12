# -*- coding: gb18030 -*-


from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus
import random

from SpellBase import *

class Spell_drawTrap( Spell ):
	"""
	�ӵ�������͹���
	"""
	def __init__( self ):
		Spell.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.radius = float( dict[ "param1" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		entityList = caster.entitiesInRangeExt( self.radius, "MonsterTrap", caster.position )		# �ҵ���Χ�ڵ������͹�
		usedIDList = caster.queryTemp( "usedIDList", [] )	# �Ѿ��ù����͹���������
		for e in entityList:
			if e.id in usedIDList:
				entityList.remove( e )
		
		if len( entityList ) > 0:
			entity = random.choice( entityList )	# ���ѡ��һ���͹�
			receiver.position = entity.position		# ��receiver�ӵ��͹���
			usedIDList.append( entity.id )
			caster.setTemp( "usedIDList", usedIDList )
#