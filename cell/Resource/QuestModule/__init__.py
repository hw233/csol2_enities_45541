# -*- coding: gb18030 -*-

from Quest import Quest
from QuestRandom import QuestRandom
from QuestRandomGroup import QuestRandomGroup
from QuestDirectFinish import QuestDirectFinish
from QuestFixedLoop import QuestFixedLoop
from QuestPotential import QuestPotential
from QuestLoopGroup import QuestLoopGroup
from QuestDart import QuestDart
from QuestRob import QuestRob
from QuestMemberDart import QuestMemberDart
from QuestMerchant import QuestMerchant
from QuestTongNormal import QuestTongNormalLoopGroup
from QuestImperialExamination import QuestImperialExamination
from QuestTongNormal import QuestTongFeteGroup
from QuestTongNormal import QuestTongBuildGroup
from Quest108Star import Quest108Star
from QuestFamilyDart import QuestFamilyDart
from QuestTongDart import QuestTongDart
from QuestNewYearGroup import QuestNewYearGroup
from QuestCompleteFixCount import QuestCompleteFixCount
from QuestTongSpaceCopyGroup import QuestTongSpaceCopyGroup
from QuestTongFuBen import QuestTongFuBen
from QuestPotentialSpecial import QuestPotentialSpecial
from QuestAbandonAtNPC import QuestAbandonAtNPC
from QuestNormal import QuestNormal
from QuestCampActivity import QuestCampActivity
from QuestCampDaily import QuestCampDaily
from QuestAuto import QuestAuto

#from QuestRandom import QuestRandom
#from QuestRandomGroup import QuestRandomGroup

map_type = {
		""						: Quest,
		"normal"				: Quest,										#��ͨ����
		"random"				: QuestRandom,									#������
		"random_group"			: QuestRandomGroup,								#�ͽ��ַ�����
		"fixed_loop"			: QuestFixedLoop,								#�̶���������
		"direct_finish" 		: QuestDirectFinish,							#ֱ����ɵ�����
		"potential"				: QuestPotential,								#Ǳ������
		"loop_group"			: QuestLoopGroup,								#������
		"quest_dart"			: QuestDart,									#��������
		"quest_rob"				: QuestRob,										#��������
		"quest_member_dart"		: QuestMemberDart,								#��Ա��������
		"quest_merchant" 		: QuestMerchant,
		"quest_tongnormal"		: QuestTongNormalLoopGroup,						#����ճ�����
		"questimperialexamination" : QuestImperialExamination,					#�ƾ�
		"quest_tongfete" 		: QuestTongFeteGroup,							#��Ὠ������
		"quest_tongbuild"		: QuestTongBuildGroup,
		"quest_108star"			: Quest108Star,									#�̶���������
		"quest_family_dart"		: QuestFamilyDart,								#��������
		"quest_tong_dart"		: QuestTongDart,								# �������
		"quest_new_year"		: QuestNewYearGroup,							#�����Ե����
		"complete_fixed"		: QuestCompleteFixCount,						#����������
		"tong_space_copy"		: QuestTongFuBen,								# ��ḱ��������
		"tong_space_copy_grp"	: QuestTongSpaceCopyGroup,						# ��ḱ��������
		"potential_special"		: QuestPotentialSpecial,						# Ǳ�ܸ�����������
		"quest_abandonatnpc"	: QuestAbandonAtNPC,							# ֻ�ܵ�ָ��NPC������������
		"normal1"				: QuestNormal,									# ��ͨ����1( �ȼ����10������Ȼ����ʾ��ɫ��̾�ŵĽ�ȡ������ʾ )
		"quest_campactivity"	: QuestCampActivity,							# ��Ӫ�����
		"quest_campdaily"		: QuestCampDaily,								# ��Ӫ�ճ�����
		"auto"					: QuestAuto,									# �Զ�����
	}

def getQuestModule( questType ):
	return map_type.get( questType, Quest )