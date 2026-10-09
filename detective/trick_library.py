"""诡计库。

这是"可生长的配方表"。每条 Trick 描述一个经典机关：
它需要什么前提、必然留下哪些痕迹、揭晓时如何被识破。

扩展方式：往下面按同样结构追加 Trick 即可，生成器会自动纳入。
"""

from __future__ import annotations

from .model import Trace, TraceKind, Trick

_T = TraceKind.TRUE_TELL


def _tell(tid: str, text: str, links: tuple[str, ...], surface: str, tags: tuple[str, ...] = ()) -> Trace:
    return Trace(id=tid, text=text, kind=_T, truth_link=links, surface_reading=surface, tags=tags)


ALL_TRICKS: list[Trick] = [
    # ---------------- 密室类 ----------------
    Trick(
        id="ice_timer",
        name="密室·融冰定时机关",
        category="密室",
        premises=frozenset({"预置机关", "低温环境"}),
        traces=(
            _tell("ice_water", "书桌边缘残留一小滩水渍，边缘已开始蒸发", ("ice_timer",),
                  "窗外飘雨，或是打翻的水杯", ("密室", "物理")),
            _tell("ice_thread", "门闩上缠着一截几乎看不见的细线，末端有水痕", ("ice_timer",),
                  "门缝积下的絮状灰尘", ("密室",)),
        ),
        reveal="水渍的来源被追到制冰盒，认定门闩是被冰融后的外力拉上。",
    ),
    Trick(
        id="key_return",
        name="密室·钥匙回流",
        category="密室",
        premises=frozenset({"预置机关"}),
        traces=(
            _tell("key_line", "钥匙落在房间内侧，但锁孔外缘有细微的拉痕", ("key_return",),
                  "死者反锁时自己刮到的", ("密室",)),
        ),
        reveal="细线从门缝回拉钥匙，制造了'门从内反锁'的假象。",
    ),
    Trick(
        id="self_lock",
        name="密室·死者自己上锁",
        category="密室",
        premises=frozenset({"掌握作息"}),
        traces=(
            _tell("victim_hand", "死者右手拇指有新鲜压痕，与门闩形状吻合", ("self_lock",),
                  "挣扎时撞到了门", ("密室",)),
        ),
        reveal="死者独自进屋后自行反锁，凶手从未进入密室。",
    ),
    # ---------------- 不在场证明类 ----------------
    Trick(
        id="clock_tamper",
        name="不在场·时钟拨动",
        category="不在场证明",
        premises=frozenset({"预置机关", "钟表"}),
        traces=(
            _tell("clock_stop", "座钟停在 2:40，但钟摆的惯性方向显示它是被强行拨停的", ("clock_tamper",),
                  "钟年久失修自己停了", ("时间",)),
        ),
        reveal="现场所有钟表被统一拨慢，行凶时刻被整体前移。",
    ),
    Trick(
        id="recording_alibi",
        name="不在场·录音伪造",
        category="不在场证明",
        premises=frozenset({"录音设备"}),
        traces=(
            _tell("tape_noise", "录音里有一段重复的冰箱压缩机声，间隔不自然", ("recording_alibi",),
                  "老式录音机的底噪", ("不在场",)),
        ),
        reveal="录音是拼接的，凶手行凶时并不在录音所示的房间。",
    ),
    # ---------------- 死亡时间类 ----------------
    Trick(
        id="drug_time",
        name="死亡时间·药物伪装",
        category="死亡时间",
        premises=frozenset({"医学知识", "药物"}),
        conflicts_with=frozenset({"ice_preserve"}),
        traces=(
            _tell("pill_blister", "床头柜少了常规安眠药，但尸检胃里只检出一粒", ("drug_time",),
                  "死者自己多吃了", ("时间",)),
        ),
        reveal="被害人先被药物致昏，真实死亡时间被推后了数小时。",
    ),
    Trick(
        id="ice_preserve",
        name="死亡时间·低温保存尸体",
        category="死亡时间",
        premises=frozenset({"低温环境"}),
        conflicts_with=frozenset({"drug_time"}),
        traces=(
            _tell("body_temp", "尸体核心温度异常低，与室温明显不符", ("ice_preserve",),
                  "死者本身体质偏寒", ("时间",)),
        ),
        reveal="尸体曾被冷藏，法医初判的死亡时间整体前移。",
    ),
    # ---------------- 身份类 ----------------
    Trick(
        id="twin_swap",
        name="身份·双胞胎替身",
        category="身份",
        premises=frozenset({"双人身份"}),
        conflicts_with=frozenset({"double_body"}),
        traces=(
            _tell("photo_double", "死者钱包合照上，有个人被剪掉了半张脸", ("twin_swap",),
                  "旧照片没保管好", ("身份",)),
        ),
        reveal="出现在监控里的人与死者是双胞胎，身份被互换。",
    ),
    Trick(
        id="double_body",
        name="身份·尸体误认",
        category="身份",
        premises=frozenset({"医学知识", "双人身份"}),
        conflicts_with=frozenset({"twin_swap"}),
        traces=(
            _tell("dental_mismatch", "牙齿记录与家属对死者的描述不符", ("double_body",),
                  "家属记错了", ("身份",)),
        ),
        reveal="被认作死者的人其实是另一个人，真死者早已调换。",
    ),
    # ---------------- 心理 / 现场伪装类 ----------------
    Trick(
        id="forged_note",
        name="心理·伪造遗书",
        category="心理",
        premises=frozenset({"伪造文书"}),
        traces=(
            _tell("note_fiber", "遗书纸张的纤维方向与现场便签本不一致", ("forged_note",),
                  "死者用了别的纸", ("心理",)),
        ),
        reveal="遗书是拼接旧信伪造的，动机被伪装成自杀。",
    ),
    Trick(
        id="staged_robbery",
        name="现场·伪装抢劫",
        category="心理",
        premises=frozenset({"布置现场"}),
        traces=(
            _tell("drawer_pattern", "抽屉被翻开，但最值钱的表却留在桌上", ("staged_robbery",),
                  "贼慌了没来得及拿", ("心理",)),
        ),
        reveal="翻动痕迹是事后摆出来的，抢劫只是掩护。",
    ),
]

BY_ID: dict[str, Trick] = {t.id: t for t in ALL_TRICKS}
