# -*- coding: gb18030 -*-
"""
�ر�ͼ��Ʒ�ࡣ
"""

import BigWorld
import csconst
import csstatus
import ItemAttrClass
import SkillTargetObjImpl
import skills
import event.EventCenter as ECenter

from gbref import rds
from CItemBase import CItemBase
from ItemSystemExp import EquipQualityExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CItemTreasureMap


class CItemTreasureMap( CItemBase ):
	"""
	�ر�ͼ��Ʒ��
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: ��Ʒ��ԭʼ����
		"""
		CItemBase.__init__( self, srcData )

	def description( self, reference ):
		"""
		��������

		@param reference: ���entity,��ʾ��˭����Ϊ���������Ĳ�����
		@type  reference: Entity
		@return:          ��Ʒ���ַ�������
		@rtype:           ARRAY of str
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# ��ʾ��Ʒ���֣�������Ʒ��Ʒ�ʾ�����Ʒ���ֵ���ɫ
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = EquipQualityExp.instance().getColorByQuality( self.getQuality() ) )
		self.desFrame.SetDescription("name" , nameDes)
		# ��Ʒ����
		desType = attrMap["type"].description( self, reference )
		self.desFrame.SetDescription( "type", desType )
		# ��������
		reqCredits = attrMap["reqCredit"].descriptionDict( self, reference )
		if reqCredits:
			reqCreditsDes = reqCredits.keys()
			for index in xrange( len( reqCreditsDes) ):
				if not reqCredits[ reqCreditsDes[index] ]:
					reqCreditsDes[ index ] = PL_Font.getSource( reqCreditsDes[ index ] , fc = "c3" )
			self.desFrame.SetDesSeveral( "reqCredit", reqCreditsDes )
		#�Ƿ��
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			self.desFrame.SetDescription( "bindType", desBind )
		#�Ƿ�Ψһ
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CItemTreasureMap[1] )
		# �Ƿ�ɳ���
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CItemTreasureMap[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )

		# �ر�ͼ��������Ϣ
		treasure_spaceName = ""
		treasure_position = ""
		if self.extra.has_key( "treasure_space" ) and self.extra.has_key( "treasure_position" ):
			spaceName = self.query("treasure_space")
			treasure_space = rds.mapMgr.getWholeArea( spaceName, reference.position[1] )
			treasure_spaceName = treasure_space.spaceName
			treasure_position = self.query("treasure_position")
			treasure_position = eval( treasure_position )
			treasure_position = str( int(treasure_position[0]) ) + ':' + str( int(treasure_position[2]) )

		# ȡ�ö��������1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			des1 = des1 % ( treasure_spaceName, treasure_position )
			self.desFrame.SetDescription( "describe1", des1 )
		# ȡ�ö��������2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
			des2 = des2 % self.getLevel()
			self.desFrame.SetDescription( "describe2", des2 )
		# ȡ�ö��������3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
			self.desFrame.SetDescription( "describe3", des3 )

		return self.desFrame.GetDescription()

	def use( self, owner, target, position = (0.0, 0.0, 0.0) ):
		"""
		ʹ����Ʒ

		@param    owner: ����ӵ����
		@type     owner: Entity
		@param   target: ʹ��Ŀ��
		@type    target: Entity
		@param position: Ŀ��λ��,����ΪNone
		@type  position: tuple or VECTOR3
		@return: STATE CODE
		@rtype:  UINT16
		"""
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			if checkResult == csstatus.SKILL_TREASURE_POS_NOT_VALID:
				ECenter.fireEvent( "EVT_ON_SHOW_AUTO_FIND_PATH_MENU", self.getOrder() )
			return checkResult

		sk = skills.getSkill( self.query( "spell" ) )
		state = sk.useableCheck( owner, SkillTargetObjImpl.createTargetObjEntity(target) )
		return csconst.SKILL_STATE_TO_ITEM_STATE.get( state,state )

	def checkUse( self, owner ):
		"""
		���ʹ�����Ƿ���ʹ�ø���Ʒ
		�ж�����ڱ�λ���Ƿ�Ϸ���������Ϸ�����򿪡���·�䡢�Զ�Ѱ·���˵�
		"""

		state = CItemBase.checkUse( self, owner )
		if state != csstatus.SKILL_GO_ON:
			return state
		if not self.isTreasurePosValid():
			return csstatus.SKILL_TREASURE_POS_NOT_VALID
		return csstatus.SKILL_GO_ON

	def isTreasurePosValid( self, offset = 20 ):
		"""
		�������ڱ�λ���Ƿ�Ϸ�(�Ƿ���ĳ����ͼspaceName������position��Χ��)copy from Spell_322398002.py,change a little

		@param 	offset		:	����ķ�Χ��࣬����Ϊ��ֵ
		@type 	offset		:	Tuple
		"""
		treasureSpace = self.query( "treasure_space", "" )		# ȡ���ر�ͼ�еĵ�ͼ��Ϣ
		treasurePosStr = self.query( "treasure_position", None )# ȡ���ر�ͼ�е�������Ϣ
		treasurePos = eval( treasurePosStr )

		player = BigWorld.player()
		if player.getSpaceLabel() != treasureSpace:
			return False
		negativeOffset = 0 - offset
		currPos = player.position
		x = float(currPos[0]) - float(treasurePos[0])
		z = float(currPos[2]) - float(treasurePos[2])
		return ( x >= negativeOffset and x <= offset and z >= negativeOffset and z <= offset )
