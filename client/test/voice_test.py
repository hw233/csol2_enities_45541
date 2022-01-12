# -*- coding: gb18030 -*-


from Sound import soundMgr
import BigWorld
playTime = 1
stop = False

"""
Ů洣�����һս�غ���İ�Σ���ҽ�ʱ�Ի����Գ��֣�ͽ��������Ԫ��ǰ�����ǡ�
Ů洣�ͽ��Ī�ţ�Ϊʦ���ˣ���Ů洳�����
Ů洣�����������Ͷ�������㲻����
Ů洣�ͽ������������Ԫ�Ӽ���Ѱ�Ҿű���������ȴ�������活ʹ���
�˺ͣ������ɣ�ħ�����ӣ�
�˺ͣ���ν�ĵֿ�����������������ڱصã�
�˺ͣ���������֣����Ǽ���ǰ��������ħ��������
�˺ͣ��ۿ�֮���˺��ڴˣ�����Ͷ�������㲻����
�˺ͣ����ѿ��������ţ�����ʿ�ٻ�̫��������ս����
�������̹���ʿ�����������˺�ǰ�����ǣ���ȡ�������
������ħ�������ݵò����Ҷ�Ҫ��Բ�桢���汨��
�������ߣ�˭��˭�����У�
��������ʿ�����ң�
���׺�������������С���������ƻ��ڶ���
���׺������������׺�������ħ���޲T֮��ش˵ء�
���׺�����ëͷС��Ҳ�ҿڳ����ԣ��Ҿͺ��������棡
���׺������ڶ����ϣ�����֮���������ܣ�
���׺�������ѩ�ɻ���ɢ�������ܣ�
���׺�����������ڤ�ߣ������ܣ�
���׺����������ҹѲ����ڣ�������ս�������ߣ�
���׺��������׺����ڴˣ����ձ�ȡ���ǹ�����
���׺������ݵú�������������¼����£�
���׺�����活�����������Ը����
���׺������е������������͵���Ϊֹ�������ܣ�
����̫һ���ڶ������������ǣ��رպڶ�����ü�ޣ�
����̫һ����ʿĪ�ţ�̫һ��Ҳ����̫һ������
����������ʲô�˵����ô����ǣ������ɣ�
������������Ӱ�ţ������ܣ�
�����������ⲻ���ܡ�����������
�����¾�Ӣ��ʿ����������������һ�����ȣ�
�����¾�Ӣ��ʿ��ͳͳ�����ҵĽ��°ɣ�
�����¾�Ӣ��ʿ������������ʧְ�ˡ�����������
�����µ��ӣ��ƻ��������ߣ�����
�����µ��ӣ��ƻ�����Ѫ���ߣ�����
��᪣��������׵۽������ͽ�������᪣��ɵ�С��������̤ǰһ����
��᪣�һ��Ů��������˿����������ɣ�
��᪣����ڷɻ�����֮�°ɣ��������������ܣ�
��᪣����������ƣ������ܣ�
��᪣��۽����ס����Ұ��ˡ�����������


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