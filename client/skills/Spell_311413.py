# -*- coding: gb18030 -*-
#
# $Id: Spell_311413.py,v 1.12 2008-08-06 06:11:18 kebiao Exp $

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
from event.EventCenter import *
import ItemTypeEnum
import csstatus
from Function import Functor
import Math



class Spell_311413( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )
		self.dist = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		self.multiple = 1	#��漼��ר�ã�self.multipleΪѰ·����/ֱ�߾���ı���

		Spell.init( self, dict )
		
		if dict[ "param1" ] == "":return
		else:self.multiple = float ( dict[ "param1" ] )
		

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
		if target is None:return
		if  hasattr( caster, "vehicleDBID" ) and caster.vehicleDBID:
			return csstatus.SKILL_CANT_USE_ON_VEHICLE
	 	
		#�����������
		path_distance = caster.disToPos( target.getObject().position )
		if path_distance > ( Math.Vector3().distTo( caster.position - target.getObject().position ) * self.multiple ): 
			return csstatus.SKILL_NO_PATH   #ս��Ƶ����ʾ û�п��н�·��
		return Spell.useableCheck( self, caster, target )

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		# ���������������˵ ��û��moveTo�� ������ҵ��ƶ��������ǵĿͻ���֪ͨ�������ı��
		if caster.id == BigWorld.player().id:
			def moveOver( success ):
				caster.onAssaultEnd()						# ԭ��Ϊ��onMovetoProtect����������Ϊ onAssaultEnd( hyw -- 09.01.12 )
				if success:
					# ����˲���ƶ���ʱ�����ɿ� Ӱ��������ɫʧ�� ����������Ҫ������Ϣ����һ��
					fireEvent( "EVT_ON_ROLE_MP_CHANGED", caster.MP, caster.MP_Max )
				else:
					DEBUG_MSG( "player move is failed." )
			
			#��ֹ�ص����������Ǿͳ嵽��Ŀ��һ�ξ���ĵط�����һ�����Ƶ���ײ
			temp_position = None
			dis_pos = 0
			targetEntity = targetObject.getObject()
			dis_pos = caster.distanceBB( caster ) + targetEntity.distanceBB( targetEntity ) #�ͷ�����ʩչ����BoundingBox�ľ���
			target_position = targetObject.getObjectPosition()
			caster_position = caster.position
			dir_position = Math.Vector3(target_position - caster_position)
			dir_position.normalise()
			temp_position = target_position + dis_pos * dir_position 
			
			caster.onAssaultStart()							# ԭ��Ϊ��onMovetoProtect����������Ϊ onAssaultStart( hyw -- 09.01.12 )
			caster.moveTo( temp_position, moveOver )


#
# $Log: not supported by cvs2svn $
# Revision 1.11  2008/05/27 08:48:48  kebiao
# �����˳��
#
# Revision 1.9  2008/05/22 06:43:34  kebiao
# no message
#
# Revision 1.8  2008/05/20 03:47:06  kebiao
# no message
#
# Revision 1.7  2008/05/20 02:46:11  kebiao
# ��������ڿ��������û���ƶ���Ŀ���������
#
# Revision 1.6  2008/04/30 03:46:16  kebiao
# ���ӿ������ɫ����
#
# Revision 1.5  2008/02/03 06:44:07  kebiao
# ���������������˵ ��û��moveTo�� ������ҵ��ƶ��������ǵĿͻ���֪ͨ�������ı��
#
# Revision 1.4  2008/01/05 03:47:30  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
# Revision 1.3  2008/01/03 07:33:06  kebiao
# ����������ؽӿ�
#
# Revision 1.2  2007/12/29 04:18:38  kebiao
# add:getFlySpeed
#
# Revision 1.1  2007/12/29 03:37:38  kebiao
# ���ӳ��֧��
#
# Revision 1.11  2007/12/14 01:22:42  kebiao
# ���ӳټ�������0.05�����
#
# Revision 1.10  2007/06/14 10:44:53  huangyongwei
# ������ȫ�ֶ���
#
# Revision 1.9  2007/03/22 09:38:58  phw
# method added: getIcon(), �����˵ײ㺯����ʵ��ͳһ����
#
# Revision 1.8  2007/03/17 04:26:40  phw
# method added: isNormalAttack()
#
# Revision 1.7  2007/03/17 02:42:44  phw
# ȥ��һЩ����Ҫ��ģ������
#
# Revision 1.6  2007/01/11 07:23:08  kebiao
# ���µ������������Ȼ�ɴ�ģ���ж�
#
# Revision 1.5  2007/01/06 04:27:48  kebiao
# ȥ����������жϣ������ϲ�attack.py�ڹ�����ʱ���ж�
#
# Revision 1.4  2006/10/16 09:44:47  phw
# no message
#
# Revision 1.3  2006/07/06 09:35:54  phw
# ɾ��ԭ�����Զ��������룬����roleͳһʵ��
#
# Revision 1.2  2006/06/08 09:25:15  phw
# ȡ��������Ϣ
#
# Revision 1.1  2006/06/07 05:53:09  phw
# no message
#
#