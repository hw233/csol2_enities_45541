# -*- coding: gb18030 -*-
#
# $Id: RoleFacade.py,v 1.51 2008-08-21 08:26:22 fangpengjun Exp $


import BigWorld
import Language
import csdefine
import csconst
import csstatus
import ShareTexts
from bwdebug import *
from event.EventCenter import *

class RoleFacade:
	@staticmethod
	def reset():
		RoleFacade.teamProtected = True
		RoleFacade.copsProtected = True
		RoleFacade.freePick = True
		RoleFacade.orderPick = True

g_RoleFacade = RoleFacade()


# --------------------------------------------------------------------
# �����õײ����
# --------------------------------------------------------------------
def onRoleEnterWorld( player ):
	"""
	@type 		player : RolePlayer
	@type 		player : role
	@return			   : None
	"""
	fireEvent( "EVT_ON_ROLE_ENTER_WORLD", player )

	fireEvent( "EVT_ON_ROLE_HP_CHANGED", player.id, player.HP, player.HP_Max )
	fireEvent( "EVT_ON_ROLE_MP_CHANGED", player.MP, player.MP_Max )
	#fireEvent( "EVT_ON_ROLE_EXP_CHANGED", player.EXP, player.getEXPMax() )
	fireEvent( "EVT_ON_ROLE_LEVEL_CHANGED", player.getLevel(), player.getLevel() )
	fireEvent( "EVT_ON_ROLE_MONEY_CHANGED", 0, player.money )
	fireEvent( "EVT_ON_ROLE_GOLD_CHANGED", 0, player.gold )
	fireEvent( "EVT_ON_ROLE_SILVER_CHANGED", 0, player.silver )
	fireEvent( "EVT_ON_ROLE_BANK_MONEY_CHANGED", 0, player.bankMoney )
	fireEvent( "EVT_ON_ROLE_POTENTIAL_CHANGED", 0, player.potential )
	fireEvent( "EVT_ON_ROLE_PKVALUE_CHANGED", player.pkValue )	# wsf��pkֵ�ı�
	fireEvent( "EVT_ON_ROLE_GOODNESS_CHANGE", player.goodnessValue )
	fireEvent( "EVT_ON_ROLE_CREDIT_CHANGED", player.teachCredit )
	fireEvent( "EVT_ON_ROLE_HONOR_CHANGED", player.honor )
	fireEvent( "EVT_ON_ROLE_VIM_CHANGED", player.vim )
#	fireEvent( "EVT_ON_ROLE_DAMAGE_CHANGED", player.damage )
#	fireEvent( "EVT_ON_ROLE_DAMAGE_PARAM_CHANGED", player.damage_param )
#	fireEvent( "EVT_ON_ROLE_ARMOR_IGNORE_CHANGED", player.armor_ignore )
#	fireEvent( "EVT_ON_ROLE_EXTRA_ATTACK_CHANGED", player.extra_attack_damage )
#	fireEvent( "EVT_ON_ROLE_EXTRA_HIT_CHANGED", player.extra_hits_damage )
	fireEvent( "EVT_ON_ROLE_DODGE_CHANGED", player.dodge_probability )
	fireEvent( "EVT_ON_ROLE_HITTED_CHANGED", player.hitProbability )
#	fireEvent( "EVT_ON_ROLE_VIGOUR_CHANGED", player.vigour )
#	fireEvent( "EVT_ON_ROLE_RIP_CHANGED", player.rip )
#	fireEvent( "EVT_ON_ROLE_DAMAGE_PLUS_CHANGED", player.damage_param )
#	fireEvent( "EVT_ON_ROLE_DAO_XING_CHANGED", player.dao_xing )
	fireEvent( "EVT_ON_ROLE_PKSTATE_CHANGED",player.pkState )
	fireEvent( "EVT_ON_ROLE_PKMODE_CHANGED",player, player.pkMode )

	fireEvent( "EVT_ON_ROLE_STRENGTH_CHANGE", player.strength )
	fireEvent( "EVT_ON_ROLE_DEXTER_CHANGE", player.dexterity )
	fireEvent( "EVT_ON_ROLE_CORPORE_CHANGE", player.corporeity )
	fireEvent( "EVT_ON_ROLE_INTELLECT_CHANGE", player.intellect )

	fireEvent( "EVT_ON_ROLE_MINDAMAGE_CHANGED", player.damage_min )
	fireEvent( "EVT_ON_ROLE_MAXDAMAGE_CHANGED", player.damage_max )
	fireEvent( "EVT_ON_ROLE_MAGDAMAGE_CHANGED", player.magic_damage )
	fireEvent( "EVT_ON_ROLE_ARMOR_CHANGED", player.armor )
	fireEvent( "EVT_ON_ROLE_MAGARMOR_CHANGED", player.magic_armor )
	fireEvent( "EVT_ON_ROLE_DOUBLE_DAM_CHANGED", player.double_hit_probability )
	fireEvent( "EVT_ON_ROLE_RESIST_CHANGED", player.resist_hit_probability )
	fireEvent( "EVT_ON_ROLE_MAG_HITTED_CHANGED", player.magic_hitProbability )
	fireEvent( "EVT_ON_ROLE_MAG_DOUBLE_CHANGED", player.magic_double_hit_probability )

	fireEvent( "EVT_ON_ROLE_RES_GIDDY_CHANGED", player.resist_giddy_probability )
	fireEvent( "EVT_ON_ROLE_RES_SLEEP_CHANGED", player.resist_sleep_probability )
	fireEvent( "EVT_ON_ROLE_RES_FIX_CHANGED", player.resist_fix_probability )
	fireEvent( "EVT_ON_ROLE_RES_HUSH_CHANGED", player.resist_chenmo_probability )
	fireEvent( "EVT_ON_ROLE_ROLL_STATE_CHANGE", player.rollState )

def onRoleLeaveWorld( player ) :
	"""
	@type 		player : RolePlayer
	@type 		player : role
	@return			   : None
	"""
	fireEvent( "EVT_ON_ROLE_LEAVE_WORLD", player )

# -------------------------------------------
def onRoleMoved( isMoving ):
	"""
	�ƶ�״̬�ı�
	"""
	fireEvent( "EVT_ON_ROLE_MOVED", isMoving )

# -----------------------------------------------------
def onRoleHPChanged( oldHP, roleID, currHP, maxHP ):
	"""
	�����ı�
	"""
	margin = currHP - oldHP
	if margin > 0 :
		fireEvent( "EVT_ON_SHOW_HEALTH_VALUE", roleID, "+" + str( margin ) )
	elif margin < 0:
		fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", roleID, str( abs( margin ) ) )
	fireEvent( "EVT_ON_ROLE_HP_CHANGED", roleID, currHP, maxHP )

def onRoleMPChanged( oldMP, roleID, currMP, maxMP ):
	"""
	mp�ı�
	"""
	margin = currMP - oldMP
	if margin > 0:
		fireEvent( "EVT_ON_SHOW_MP_VALUE", roleID, "+" + str( margin ) )
	elif margin < 0:
		fireEvent( "EVT_ON_SHOW_MP_VALUE", roleID, str( margin ) )
	fireEvent( "EVT_ON_ROLE_MP_CHANGED", currMP, maxMP )

def onRoleExpChanged( oldExp, currExp, expMax ):
	"""
	����ֵ�ı�
	"""
	pass
	fireEvent( "EVT_ON_ROLE_EXP_CHANGED", currExp, expMax )

def onRoleLevelChanged( oldLevel, level ):
	"""
	level�ı�
	"""
	fireEvent( "EVT_ON_ROLE_LEVEL_CHANGED", oldLevel, level )
	BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_CURRENT_LEVEL, level )

def onRoleMoneyChanged( oldValue, newValue, reason ):
	"""
	��ҽ�Ǯ�ı�֪ͨ
	"""
	dispersion = newValue - oldValue
	if dispersion == 0:return
	fireEvent( "EVT_ON_ROLE_MONEY_CHANGED", oldValue, newValue )

	def makeString( dispersion ):
		dispersion = abs( dispersion )
		gold = dispersion / 10000
		silver = dispersion / 100 - gold * 100
		coin = dispersion - gold * 10000 - silver * 100
		tempString = ""
		if gold > 0:
			tempString = " %i %s" % ( gold, ShareTexts.MONEY_GOLD_COIN )
		if silver > 0:
			tempString += " %i %s" % ( silver, ShareTexts.MONEY_SILVER_COIN )
		if coin > 0:
			tempString += " %i %s" % ( coin, ShareTexts.MONEY_COPPER_COIN )
		return tempString

	tempString = makeString( dispersion )
	if reason == csdefine.CHANGE_MONEY_INITIAL:
		return
	elif reason == csdefine.CHANGE_MONEY_STORE:		# �����Ǯ
		BigWorld.player().statusMessage( csstatus.CIB_MSG_STORE_MONEY_TO_BANK, tempString )
	elif reason == csdefine.CHANGE_MONEY_FETCH:		# ȡ����Ǯ
		BigWorld.player().statusMessage( csstatus.CIB_MSG_FETCH_MONEY_FROM_BANK, tempString )
	elif reason == csdefine.CHANGE_MONEY_DEPOSIT_RETURN:	# ����Ѻ��
		BigWorld.player().statusMessage( csstatus.CIB_MSG_FETCH_MONEY_FROM_DEPOSIT, tempString )
	elif reason == csdefine.CHANGE_MONEY_LUCKYBOXJINBAO:
		BigWorld.player().statusMessage( csstatus.CIB_JINBAO_ADD_REWARD, tempString )
	elif reason == csdefine.CHANGE_MONEY_LUCKYBOXZHAOCAI:
		BigWorld.player().statusMessage( csstatus.CIB_ZHAOCAI_ADD_REWARD, tempString )
	else:
		if dispersion > 0 :
			BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_GAIN_MONEY, tempString )
		if dispersion < 0:
			BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_LOST_MONEY, tempString )



def onRoleGoldChanged( oldValue, newValue, reason ):
	"""
	��ҽ�Ԫ���ı�֪ͨ
	"""
	fireEvent( "EVT_ON_ROLE_GOLD_CHANGED", oldValue, newValue )
	if reason == csdefine.CHANGE_GOLD_INITIAL:
		return
	goldDisper = newValue - oldValue
	if goldDisper > 0:
		BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_GAIN_GOLD, goldDisper )
	else:
		BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_LOST_GOLD, -goldDisper )


def onRoleSilverChanged( oldValue, newValue, reason ):
	"""
	�����Ԫ���ı�֪ͨ
	"""
	fireEvent( "EVT_ON_ROLE_SILVER_CHANGED", oldValue, newValue )
	if reason == csdefine.CHANGE_SILVER_INITIAL:
		return
	goldDisper = newValue - oldValue
	if goldDisper > 0:
		BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_GAIN_SILVER, goldDisper )
	else:
		BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_LOST_SILVER, -goldDisper )


def onPotentialChanged( oldValue, newValue ) :
	fireEvent( "EVT_ON_ROLE_POTENTIAL_CHANGED", oldValue, newValue )

def onPickUpStateChange( pickUpState ):
	"""
	"""
	fireEvent( "EVT_ON_ROLE_PICKUPSTATE_CHANGED", pickUpState )

def setPickUpState( pickUpState ):
	player = BigWorld.player()
#	if not isChecked : return
	if not player.isCaptain(): return
	if player.pickUpState == pickUpState: return
	player.base.changePickUpState( pickUpState )

# -----------------------------------------------------
def onRoleDamageChanged( value ):
	"""
	�����ı�
	"""
	fireEvent( "EVT_ON_ROLE_DAMAGE_CHANGED", value )

def onRoleDodgeChanged( value ):
	"""
	���ܸı�
	"""
	fireEvent( "EVT_ON_ROLE_DODGE_CHANGED", value )

def onRoleHittedChanged( oldValue, newValue ) :
	"""
	���иı�
	"""
	fireEvent( "EVT_ON_ROLE_HITTED_CHANGED", newValue )

def onRoleDoubleDamageChanceChanged( value ):
	"""
	����һ������
	"""
	fireEvent( "EVT_ON_ROLE_DOUBLE_DAMAGE_CHANCE_CHANGED", value )

def onRoleArmorIgnore( value ):
	"""
	���������ʸı�
	"""
	fireEvent( "EVT_ON_ROLE_ARMOR_IGNORE_CHANGED", value )

def onRoleExtraAttackChange( value ):
	"""
	�˺��ӳɸı�
	"""
	fireEvent( "EVT_ON_ROLE_EXTRA_ATTACK_CHANGED", value )

def onRoleExtraHitChange( value ):
	"""
	���˼ӳɸı�
	"""
	fireEvent( "EVT_ON_ROLE_EXTRA_HIT_CHANGED", value )

def onRoleVigourChange( value ):
	"""
	���Ƹı�
	"""
	fireEvent( "EVT_ON_ROLE_VIGOUR_CHANGED", value )

def onRoleRipChange( value ):
	"""
	�����ı�
	"""
	fireEvent( "EVT_ON_ROLE_RIP_CHANGED", value )

def onRoleDamageParamChanged( value ):
	"""
	�չ��ӳ�
	"""
	fireEvent( "EVT_ON_ROLE_DAMAGE_PARAM_CHANGED", value )

def onRoleDaoXingChange( value ):
	"""
	���иı�
	"""
	fireEvent( "EVT_ON_ROLE_DAO_XING_CHANGED", value )

# -----------------------------------------------------
def onSkillIntonate( lastTime ) :
	"""
	lastTime : time intonate last
	"""
	fireEvent( "EVT_ON_ROLE_INTONATE", lastTime )


def onRoleSpellInterrupted() :
	"""
	when spell interrupted, it will be called
	"""
	fireEvent( "EVT_ON_ROLE_INTONATE_DISTURBED" )

def onFishingBegin( player, reason ):
	"""
	��ҽ������״̬
	"""
	fireEvent( "EVT_ON_ROLE_BEGIN_FISHING", player, reason )

def onFishingEnd( player ):
	"""
	����˳�����״̬
	"""
	fireEvent( "EVT_ON_ROLE_END_FISHING" )
