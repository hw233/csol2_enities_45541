# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import random
from Spell_Item import Spell_Item
from bwdebug import *
import BigWorld
import Math

class Spell_PlantTree( Spell_Item ):
	"""
	��ֲ����
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.p1 = ""
		self.p2 = ""
		self.p3 = ""
		self.p4 = ""
		self.p5 = ""

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.p1 = str( dict[ "param1" ] )					# ������ģ�ͱ��
		self.p2 = int( dict[ "param2" ] )      				# �������ӵ�ID
		if dict[ "param3" ]:
			self.p3 = str( dict[ "param3" ] )				# ������ֲλ������
		if dict[ "param4" ]:
			self.p4 = float( dict[ "param4" ] )				# ������ֲ��Χ����
		if dict[ "param5" ]:
			self.p5 = str( dict[ "param5" ] ).split(";")	# ������ֲ��ͼ����

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if caster.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):
			return csstatus.FRUIT_PLANT_NOT_AREA

		if len( caster.entitiesInRangeExt( csconst.FRUIT_PLANT_DISTANCE, "FruitTree", caster.position ) ):
			return csstatus.FRUIT_PLANT_NEED_FAR

		if self.p5:
			if caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in self.p5:
				return csstatus.FRUIT_PLANT_WRONG_MAP

		if self.p3:
			posData = self.p3.split("|")
			posDatas = []
			for i in posData:
				j = eval(i)
				posDatas.append( j )
			canPlantTree = False
			for k in posDatas:
				if caster.position.distTo( k ) <= self.p4: canPlantTree = True
			if canPlantTree == False:
				return csstatus.FRUIT_PLANT_WRONG_POS
			else: return csstatus.SKILL_GO_ON

		if caster.state == csdefine.ENTITY_STATE_FIGHT:
			return csstatus.FRUIT_PLANT_WRONG
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		��������Ҫ��������
		���Ƕ��Լ�ʹ�õ���Ʒ���ܣ����receiver�϶���real entity
		"""
		position = Math.Vector3( receiver.position )
		param = { "modelNumber" : self.p1, "fruitseedID" : self.p2, "planterDBID" : receiver.databaseID, "planterName" : receiver.getName() }
		receiver.createEntityNearPlanes( "FruitTree", position, ( 0, 0, 0 ), param )

