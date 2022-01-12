# -*- coding: gb18030 -*-
#
# $Id: SkillBase.py,v 1.16 2008-08-06 06:09:32 qilan Exp $

"""
���ܣ������������ܣ���Buff�Ļ����ࡣ
"""
import BigWorld
import csstatus
import csdefine
from SpellPose import SpellPose
from event.EventCenter import *
from gbref import rds

class SkillBase:
	def __init__( self ):
		self.pose = 0				    # ���ܶ���Ч��
		self._datas = {}
		self._uid = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			����һ��python �ֵ�����
		@type dict:				python dict�� like {"key":value,...}
		"""
		self._datas = dict
		self.pose = SpellPose()

	def getID( self ):
		return self._datas["ID"]

	def getUID( self ):
		return self._uid

	def getName( self ):
		return self._datas["Name"]

	def getLevel( self ):
		return self._datas["Level"]

	def getMaxLevel( self ):
		"""
		��ȡ�˼��ܵ����ȼ�

		@return: int
		"""
		return self._datas["MaxLevel"]

	def getType( self ):
		"""
		��ü������͡�
		"""
		return self._datas["Type"]

	def setUID( self, uid ):
		"""
		uid��ֹ���ֶ����ã�
		"""
		self._uid = uid

	def getIcon( self ):
		return rds.spellEffect.getIcon( self.getID() )

	def getDescription( self ):
		return self._datas["Description"]

	def getPosture( self ) :
		"""
		��ȡ������ķ�
		"""
		return csdefine.ENTITY_POSTURE_NONE

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_UNKNOW

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "id" : self.getID(), "param" : None, "uid" : self.getUID() }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		return self

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				return

		# �ص��˺���Ϣ ��һ���˺���HP ������0 �������� ����Ȼ���˺�
		target.onReceiveDamage( casterID, self, damageType, damage  )
		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage  )
		# ֪ͨ�˺�ͳ��ģ��
		rds.damageStatistic.receiveDamage( self, caster, target, damageType, damage  )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		���ܲ����˺�ʱ�Ķ���Ч���ȴ���
		@param player:			����Լ�
		@type player:			Entity
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		@param caster:			Buffʩ���� ����ΪNone
		@type castaer:			Entity
		@param damageType:		�˺�����
		@type damageType:		Integer
		@param damage:			�˺���ֵ
		@type damage:			Integer
		"""
		pass




# $Log: not supported by cvs2svn $
# Revision 1.15  2008/08/06 03:31:16  kebiao
# ����receiveDamage�ӿڲ��� skill.receiveSpell ȥ��skillID
#
# Revision 1.14  2008/08/05 02:02:15  qilan
# ������_receiveDamageAE()����Ϊ_SkillAE()
# ȥ��ϵͳ��Ϣ��ص���������_receiveDamageSysInfo()/_receiveDamageFlyText()
# ע���˺�ϵͳ��Ϣ�ŵ��ܷ��ߵ�entity��
#
# Revision 1.13  2008/07/22 08:54:35  qilan
# method modify��_receiveDamageSysInfo��

#
# Revision 1.12  2008/07/22 07:08:42  qilan
# method modify��_receiveDamageSysInfo�����A�������B������B������A�Ĺ�����ս����Ϣ��ʾΪA������B�Ĺ������޸ķ�ʽ��������������XX��XX���͡�XX���������XX��λ�õ���
#
# Revision 1.11  2008/07/21 03:04:31  huangyongwei
# caster.pcg_getOutPet(),
# ��Ϊ
# caster.pcg_getActPet(),
#
# Revision 1.10  2008/07/15 06:54:32  kebiao
# ���ܲ���ͳһʹ��section ��Ϊpython����������������ڴ棬Language.section
# ��C�ṹ�洢 ���ή���ڴ�����
#
# Revision 1.9  2008/07/09 01:33:35  kebiao
# ����˺��ص�����
#
# Revision 1.8  2008/07/08 09:20:09  yangkai
# ������ ��Ч���ü��ط�ʽ
#
# Revision 1.7  2008/07/04 01:06:43  zhangyuxing
# ���������󣬲�����ʾ��Ϣ
#
# Revision 1.6  2008/06/30 06:20:09  kebiao
# ����    self._receiveDamageAE( player, target, caster, param1, param2, skillID )
# UnboundLocalError: local variable 'caster' referenced before assignment
#
# Revision 1.5  2008/04/01 01:11:54  kebiao
# ���ӽ�ɫ�ܹ���ʱ�� �˺���ʾ
#
# Revision 1.4  2008/03/31 09:05:00  kebiao
# �޸�receiveDamage��֪ͨ�ͻ��˽���ĳ���ܽ���ֿ�
# ����ͨ��receiveSpell֪ͨ�ͻ���ȥ���֣�֧�ָ����ܲ�ͬ�ı���
#
# Revision 1.3  2008/03/18 07:52:11  kebiao
# �����˳��﹥���������ʾ��Ϣ
#
# Revision 1.2  2008/02/28 08:33:24  kebiao
# ��Ϊskill���ܺ�BUFFҲ������˺�������Ϣ��ʾ,��˰Ѳ��ֽӿ�ת�Ƶ�skillbase
# ��Ϊ��ӿ�
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
#
