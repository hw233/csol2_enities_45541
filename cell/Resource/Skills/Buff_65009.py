# -*- coding:gb18030 -*-


from bwdebug import *
import BigWorld
import csconst
import csdefine
import csstatus
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_JUMP


class Buff_65009( Buff_Normal ):
	"""
	����������ͷ������������%���Է�Χ�ڵжԵ�λ����˺��������ƶ�
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0			# ��������������߱���
		self._p2 = 0			# buff����Χ������ɵĹ̶��˺�ֵ
		self._p3 = 0			# ��Ѱ���˵İ뾶
		
	def init( self, dict ):
		"""
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0 ) * csconst.FLOAT_ZIP_PERCENT
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )
		self._p3 = float( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		receiver.magic_armor_percent += self._p1
		receiver.calcMagicArmor()
		receiver.armor_percent += self._p1
		receiver.calcArmor()
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		if receiver.isMoving():
			receiver.stopMoving()
		
		entityList = receiver.entitiesInRangeExt( self._p3, None, receiver.position )	
		for entity in entityList:
			if receiver.queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE:
				damage = self.calcDotDamage( receiver, entity, csdefine.DAMAGE_TYPE_MAGIC, self._p2 )
				entity.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				entity.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
				
	def doLoop( self, receiver, buffData ):
		"""
		"""
		entityList = receiver.entitiesInRangeExt( self._p3, None, receiver.position )	
		for entity in entityList:
			if receiver.queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE:
				damage = self.calcDotDamage( receiver, entity, csdefine.DAMAGE_TYPE_MAGIC, self._p2 )
				entity.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				entity.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		receiver.magic_armor_percent -= self._p1
		receiver.calcMagicArmor()
		receiver.armor_percent -= self._p1
		receiver.calcArmor()
		receiver.actCounterDec( STATES )
		
		entityList = receiver.entitiesInRangeExt( self._p3, None, receiver.position )	
		for entity in entityList:
			if receiver.queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE:
				damage = self.calcDotDamage( receiver, entity, csdefine.DAMAGE_TYPE_MAGIC, self._p2 )
				entity.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				entity.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
				