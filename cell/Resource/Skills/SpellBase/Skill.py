# -*- coding: gb18030 -*-
#
# $Id: Skill.py,v 1.25 2008-02-29 09:26:00 kebiao Exp $

"""
���������ࡣ
"""
import csdefine
from bwdebug import *
import csstatus
import new
import random
import copy

from Function import newUID

class Skill:
	"""
	���м���Ч���Ļ����࣬���еļ��ܡ�������buff��Ч�����ص�ʱ��Ӧ�ô�����һ��ȫ�ֵĻ����б��С�
	������Ϊ�����еļ���Ч������ʹ�ã���ʹ�ù����ǡ�ʩչ��use����->�����գ�receive��������˻�����ֻ�С�ʩչ���͡����ա��Ľӿڣ��Լ���顰��ʩչ�����useableCheck�����Ľӿڡ�
	�����ںܶ༼��Ч�������ܻ���Ҫ�ȸ���entity���ϣ����ض�������Ż���С�ʩչ���򡰽��ա����������������attach()��detach()�ӿ��ṩճ�����ܡ�
	����"Skill"�����"Skill_"��ͷ
	define SKILLID INT32
	"""
	# ȫ�����ݼ���; key is Skill::_id and value is instance of Skill or derive from it.
	skillLoader = None
	def __init__( self ):
		"""
		���캯����
		"""
		self._id = 0										# ����ID
		self._uid = 0										# ���ܵ�uid
		self._name = ""										# ��������
		self._description = ""								# ��������
		
	@staticmethod
	def instance( id ):
		"""
		ͨ�� skill id ��ȡskillʵ��
		"""
		return Skill.skillLoader[id]

	@staticmethod
	def setInstance( skillLoader ):
		"""
		����ȫ�ֵ����ݼ��ϣ���ͨ����skill loader����

		@param datas: dict
		"""
		Skill.skillLoader = skillLoader

	@staticmethod
	def register( id, instance ):
		"""
		ע��һ��skillʵ��
		"""
		Skill.skillLoader.register( id, instance )
		
	def init( self, dictDat ):
		"""
		virtual method;
		��ȡ��������
		@param dictDat: ��������
		@type  dictDat: python dict
		"""
		self._id = long( dictDat["ID"] )
		self._description = dictDat[ "Description" ]
		self._name = dictDat["Name"]
			
	def getID( self ):
		"""
		"""
		return self._id
	
	def getUID( self ):
		"""
		"""
		return self._uid
	
	def setUID( self, uid ):
		"""
		uid��ֹ���ֶ����ã� 
		ֻ�Ǽ����ڴ������Ĺ��̺�����һ��cell��Ӧ��
		�ָ�����ԭ��һֱӵ�е�uid, ���ʱ�����������õ�
		"""
		self._uid = uid
		
	def getName( self ):
		"""
		virtual method;
		ȡ�øü��ܵ����� ʵ����������ʵ��
		"""
		return self._name
		
	def getDescription( self ):
		"""
		virtual method;
		ȡ�øü��ܵ����� ʵ����������ʵ��
		"""
		return self._description

	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		pass

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		pass

	def use( self, caster, target ):
		"""
		virtual method = 0.
		����� target/position ʩչһ���������κη�����ʩ������ɴ˽���
		dstEntity��position�ǿ�ѡ�ģ����õĲ�����None���棬���忴���������Ƕ�Ŀ�껹��λ�ã�һ��˷���������client����ͳһ�ӿں���ת������
		Ĭ��ɶ��������ֱ�ӷ��ء�
		ע���˽ӿڼ�ԭ���ɰ��е�cast()�ӿ�
		@param   caster: ʩ����
		@type    caster: Entity
		
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		pass

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_UNKNOW
		
	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�
		ͨ������´˽ӿ�����onArrive()���ã��������п�����SpellUnit::receiveOnreal()�������ã�
		���ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣�������Ƿ���Ҫ��real entity���Ͻ��գ�
		�ɼ����������receive()�����йضϣ������ṩ��ػ��ơ�
		
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		pass

	def springOnDamage( self, caster, receiver, skill, damage ):
		"""
		virtual method.
		���˺�����󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ���ܵ��˺��Ժ��ٴ�����Ч����

		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   skill: ����ʵ��
		@type    skill: Entity
		@param   damage: ʩ������ɵ��˺�
		@type    damage: int32
		"""
		pass
	
	def springOnHit( self, caster, receiver, damageType ):
		"""
		��������ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   damageType: �˺����
		@type    damageType: uint32
		"""
		pass

	def springOnDodge( self, caster, receiver, damageType ):
		"""
		���ܱ�����ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   damageType: �˺����
		@type    damageType: uint32
		"""
		pass
		
	def springOnDoubleHit( self, caster, receiver, damageType ):
		"""
		���ܱ���ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   damageType: �˺����
		@type    damageType: uint32
		"""
		pass
		
	def springOnResistHit( self, caster, receiver, damageType ):
		"""
		���ܱ��м�ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   damageType: �˺����
		@type    damageType: uint32
		"""
		pass
	
	def getNewObj( self ):
		"""
		virtual method.
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		obj.setUID( newUID() )
		return obj
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return {  "param" : None }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		return self

# Skill.py
