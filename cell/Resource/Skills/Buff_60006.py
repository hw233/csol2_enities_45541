# -*- coding:gb18030 -*-

from SpellBase import *
from bwdebug import *
from Buff_Normal import Buff_Normal
import csdefine
from Function import newUID

class Buff_60006( Buff_Normal ):
	"""
	�����������������ɫ��BUFF������BUFF������ʩ��AOE��ը����
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0		# ���ı���
		self._p3 = 0		# AOE���ܵ��˺�����
		self._p4 = 0		# AOE���ܵ��˺���Χ
		self._p5 = 0		# AOE���ܶ�������ɵ����˱���
		self.NPCOldModelScale = 1.0	# ��¼modelScale�ı�ǰ��Ĭ��scale�Ա�ָ�
		
	def init( self, dict ):
		"""
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] )		# ���ı���
		tempList2 = dict[ "Param2" ].split( ";" )
		self._p3 = float( tempList2[0] ) / 100		# AOE���ܵ��˺�����
		self._p4 = int( tempList2[1] )				# AOE���ܵ��˺���Χ
		self._p5 = float( int( tempList2[2] ) ) / 100	# AOE���ܶ�������ɵ����˱���
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		self.NPCOldModelScale = receiver.modelScale
		receiver.modelScale = self._p1
		receiver.addFlag( csdefine.ENTITY_FLAG_CHANG_COLOR_RED )
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		receiver.removeFlag( csdefine.ENTITY_FLAG_CHANG_COLOR_RED )
		receiver.modelScale = self.NPCOldModelScale
		entityList = receiver.entitiesInRangeExt( self._p4, None, receiver.position )
		entityCount = 10
		for entity in entityList:
			if receiver.queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE:
				damage = self.calcDotDamage( receiver, entity, csdefine.DAMAGE_TYPE_MAGIC, self._p3*entity.HP_Max )
				entity.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				entity.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
				entityCount -= 1
				if entityCount == 0:
					break
					
		# ��������ɵ��˺�
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_MAGIC, self._p5*receiver.HP_Max )
		receiver.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
		receiver.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
		Buff_Normal.doEnd( self, receiver, buffData )
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self.NPCOldModelScale }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_60006()
		obj.__dict__.update( self.__dict__ )

		obj.NPCOldModelScale = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
