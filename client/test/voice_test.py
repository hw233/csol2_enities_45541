# -*- coding: gb18030 -*-


from Sound import soundMgr
import BigWorld
playTime = 1
stop = False

"""
女娲：土星一战关乎洪荒安危，我届时自会亲自出手，徒儿先与镇元子前往土星。
女娲：徒儿莫慌，为师来了！（女娲出场）
女娲：后土！速速投降，饶你不死！
女娲：徒儿，你且与镇元子继续寻找九冰葵火矿，我先带后土回娲皇宫！
羲和：受死吧，魔道贼子！
羲和：无谓的抵抗，玄铁真金我们势在必得！
羲和：玄铁真金到手，我们继续前进，剿灭魔道余孽！
羲和：帝俊之妻羲和在此，速速投降，饶你不死！
羲和：我已开启传送门，请勇士速回太阳宫报告战况！
琼霄：盘古勇士，请随我与羲和前往土星，夺取玄铁真金。
琼霄：魔道贼子休得猖狂，我定要替圆舒、望舒报仇。
琼霄：哼，谁怕谁，接招！
琼霄：勇士，救我！
祖巫后土：哪里来的小贼，胆敢破坏黑洞！
祖巫后土：吾乃祖巫后土，受魔君罗睺之令看守此地。
祖巫后土：毛头小子也敢口出狂言，我就和你们玩玩！
祖巫后土：黑洞至上，寂灭之力！（技能）
祖巫后土：雨雪飞花，散！（技能）
祖巫后土：看我玄冥踢！（技能）
祖巫后土：今日我寡不敌众，来日再战！（逃走）
祖巫后土：祖巫后土在此，今日必取你们狗命！
祖巫后土：休得胡言乱语，我们手下见真章！
祖巫后土：娲皇饶命，后土愿降！
祖巫后土：有点厉害，不过就到此为止！（技能）
东皇太一：黑洞正在吞噬土星，关闭黑洞迫在眉睫！
东皇太一：勇士莫慌，太一来也！（太一出场）
大巫巫婪：什么人胆敢擅闯土星，受死吧！
大巫巫婪：无影脚！（技能）
大巫巫婪：这不可能……（死亡）
雷音寺精英剑士：不自量力，吃我一剑，喝！
雷音寺精英剑士：统统死在我的剑下吧！
雷音寺精英剑士：后土尊上我失职了……（死亡）
雷音寺弟子：破坏能量塔者，死！
雷音寺弟子：破坏混沌血池者，死！
巫岐：吾乃祖巫帝江手下猛将大巫巫岐，仙道小贼休想再踏前一步！
巫岐：一介女流竟敢如此狂妄，受死吧！
巫岐：死在飞火流星之下吧，哈哈哈！（技能）
巫岐：接我蓄力掌！（技能）
巫岐：帝江祖巫……我败了……（死亡）


"""
data = [("tuxin_voice/nv3/nvwa1"),
		("tuxin_voice/nv3/nvwa2"),
		("tuxin_voice/nv3/nvwa3"),
		("tuxin_voice/nv3/nvwa4"),
		("tuxin_voice/nv2/xihe1"),
		("tuxin_voice/nv2/xihe2"),
		("tuxin_voice/nv2/xihe3"),
		("tuxin_voice/nv2/xihe4"),
		("tuxin_voice/nv2/xihe5"),
		("tuxin_voice/nv1/qxiao1"),
		("tuxin_voice/nv1/qxiao2"),
		("tuxin_voice/nv1/qxiao3"),
		("tuxin_voice/nv1/qxiao4"),
		("tuxin_voice/nv1/zwht1"),
		("tuxin_voice/nv1/zwht2"),
		("tuxin_voice/nv1/zwht3"),
		("tuxin_voice/nv1/zwht4"),
		("tuxin_voice/nv1/zwht5"),
		("tuxin_voice/nv1/zwht6"),
		("tuxin_voice/nv1/zwht7"),
		("tuxin_voice/nv1/zwht8"),
		("tuxin_voice/nv1/zwht9"),
		("tuxin_voice/nv1/zwhtplayTime"),
		("tuxin_voice/nv1/zwht11"),
		("tuxin_voice/nan2/dhty1"),
		("tuxin_voice/nan2/dhty2"),
		("tuxin_voice/nan2/dwwn1"),
		("tuxin_voice/nan2/dwwn2"),
		("tuxin_voice/nan2/dwwn3"),
		("tuxin_voice/nan2/jianshi1"),
		("tuxin_voice/nan2/jianshi2"),
		("tuxin_voice/nan2/jianshi3"),
		("tuxin_voice/nan2/lysdz1"),
		("tuxin_voice/nan2/lysdz2"),
		("tuxin_voice/nan2/wuqi1"),
		("tuxin_voice/nan2/wuqi2"),
		("tuxin_voice/nan2/wuqi3"),
		("tuxin_voice/nan2/wuqi4"),
		("tuxin_voice/nan2/wuqi5"),
		]
i = 0
def playVoice():
	global i,stop
	if stop:
		return
	if len(data) == i:
		i = 0
	name = data[i]
	i+=1
	soundMgr.playVoice(name)
	
	BigWorld.callback( playTime, playVoice )