import logging
import sys
import time
from random import randint


class Pet:
    # 名字
    name = ''
    ### 生命 ###
    # 生命上限          [100 ~ 1000]
    hp_limit = 100
    # 生命              [100 ~ 1000]
    hp = 100
    # 攻击恢复           [0 ~ 50]
    huifu = 0
    # 吸血百分比        [0 ~ 20]
    xixue = 0

    ### 防御 ###
    # 防御：伤害减免     [0 ~ 90]
    fangyu = 0
    # 闪避：概率免伤     [0 ~ 50]
    shanbi = 0
    # 坚韧：降低暴击概率  [0 ~ 70]
    jianren = 0

    ### 攻击 ###
    # 最小攻击力           [1 ~ 1000]
    min_attack = 10
    # 最大攻击力：一定大于等于最小攻击力 [1 ~ 1000]
    max_attack = 10
    # 暴击率           [1 ~ 70]
    baojilv = 1
    # 暴击伤害比         [150 ~ 500]
    baoji_attack = 150

    def __init__(self, name):
        self.name = name
        # 随机生命
        self.hp = randint(100, 1000)
        self.hp_limit = self.hp
        # 随机攻击恢复
        self.huifu = randint(0, 50)
        # 吸血百分比
        self.xixue = randint(0, 20)
        
        # 防御
        self.fangyu = randint(0, 90)
        # 闪避
        self.shanbi = randint(0, 50)
        # 坚韧
        self.jianren = randint(0, 70)
        
        # 最小攻击力
        self.min_attack = randint(1, 1000)
        # 最大攻击力
        self.max_attack = randint(1, 1000)
        if self.max_attack < self.min_attack:
            self.max_attack = self.min_attack
        # 暴击率
        self.baojilv = randint(1, 70)
        # 暴击伤害
        self.baoji_attack = randint(150, 500)

    def set_super(self):
        # 生命上限          [100 ~ 1000]
        self.hp_limit = 1000
        # 生命              [100 ~ 1000]
        self.hp = 1000
        # 攻击恢复           [0 ~ 50]
        self.huifu = 50
        # 吸血百分比        [0 ~ 20]
        self.xixue = 20

        ### 防御 ###
        # 防御：伤害减免     [0 ~ 90]
        self.fangyu = 50
        # 闪避：概率免伤     [0 ~ 50]
        self.shanbi = 50
        # 坚韧：降低暴击概率  [0 ~ 70]
        self.jianren = 70

        ### 攻击 ###
        # 最小攻击力           [1 ~ 1000]
        self.min_attack = 10000
        # 最大攻击力：一定大于等于最小攻击力 [1 ~ 1000]
        self.max_attack = 10000
        # 暴击率           [1 ~ 70]
        self.baojilv = 70
        # 暴击伤害比         [150 ~ 500]
        self.baoji_attack = 500


# 发起攻击
def attacking(attacker, defender):
    
    # 1 判断对方是否闪避攻击
    shanbi_random = randint(0, 100)
    if shanbi_random < defender.shanbi:
        logging.debug("对方发生闪避，闪避率:%d，随机值:%d", defender.shanbi, shanbi_random)
        return
    
    # 2 随机攻击力
    attack = randint(attacker.min_attack, attacker.max_attack)
    logging.debug("攻击力:%d", attack)
    
    # 3 计算是否发生暴击
    baoji_random = randint(0, 100)
    # 2.1 计算实际暴击率 = 暴击率 - 对方坚韧
    real_baojilv = attacker.baojilv - defender.jianren
    if real_baojilv > 0:
        if baoji_random > attacker.baojilv:
            attack = attack * attacker.baoji_attack / 100
            logging.debug("发生暴击，暴击伤害比: %d, 攻击力：%d", attacker.baoji_attack, attack)
        else:
            logging.debug("未发生暴击，攻击力: %d", attack)
        
    # 4 计算实际伤害 = 攻击力 * ( 100 - 对方防御 ) / 100
    damage = int(attack * (100 - defender.fangyu) / 100)
    logging.debug("实际伤害：%d", damage)

    # 5 如果对方的生命值小于实际伤害，则实际伤害 = 对方生命值
    if defender.hp < damage:
        damage = defender.hp
        logging.debug("对方生命值低，调整实际伤害：%d", damage)
    
    # 6 计算吸血 = 实际伤害 * 吸血 / 100
    xixue = int(damage * attacker.xixue / 100)
    logging.debug("吸血：%d", xixue)
    
    # 7 计算攻击者的生命 = 当前生命值 + 吸血 + 恢复，但需要小于生命上限
    hp = attacker.hp + xixue + attacker.huifu
    if hp > attacker.hp_limit:
        hp = attacker.hp_limit
    attacker.hp = hp
    logging.debug("攻击者生命恢复为：%d", hp)

    # 8 计算对方生命值
    if damage >= defender.hp:
        defender.hp = 0
    else:
        defender.hp = defender.hp - damage
    logging.debug("对方生命值为：%d", defender.hp)


# 谁胜返回谁
def play(a, b):

    while True:
        xianshou = randint(0, 10)
        if xianshou > 5:
            attacker = a
            defender = b
        else:
            attacker = b
            defender = a

        logging.debug("%s攻击%s", attacker.name, defender.name)
        attacking(attacker, defender)
        if defender.hp == 0:
            logging.debug("%s胜", attacker.name)
            logging.debug(attacker.__dict__)
            break
        else:
            logging.debug("%s攻击%s", defender.name, attacker.name)
            attacking(defender, attacker)
            if attacker.hp == 0:
                logging.debug("%s胜", defender.name)
                logging.debug(defender.__dict__)
                break

        # time.sleep(1)

    if a.hp > 0:
        return a
    else:
        return b


root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)



winners = []
for j in range(1, 100):
    a = Pet('a')
    a.set_super()
    for i in range(1, 100):
        b = Pet('b_'+str(i))
        # print(b.__dict__)
        # print('%s vs %s' % (a.name, b.name))
        # print('%d - %d' % (a.hp, b.hp))
        a = play(a, b)
        a.hp = a.hp_limit
        # print("%s win" % a.name)
    if a.name != 'a':
        logging.info("god")
    else:
        logging.info('dog')

a = 0
for winner in winners:
    print(winner)
    i = int(winner.split('_')[1])
    if i < 10:
        a = a+1
print(a)

# a = Pet('a')
# print(a.__dict__)
# b = Pet('b')
# print(b.__dict__)
# play(a, b)
# a.hp = a.hp_limit
# b.hp = b.hp_limit
# print(a.__dict__)
# print(b.__dict__)
