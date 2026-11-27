import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

EXTRACT_PROMPT = """你是保险理赔客服的「信息抽取器」。
唯一任务：从用户的话里抽取意图和槽位。
不要回答用户问题，不要解释，不要寒暄。

【意图类目】（只能选一个）
1. 理赔可行性 —— 能不能赔（含责任范围、等待期）
2. 责任免除 —— 某类项目是否赔（生育、补牙、体检、检查、美容、牙齿）
3. 既往症 —— 某病是否算既往症、一般还是严重
4. 健康告知 —— 某病能不能投保（健告 / 免健告）
5. 费用口径 —— 赔多少、比例、免赔额、保额、上限
6. 材料清单 —— 要准备什么材料
7. 拒赔原因 —— 为什么没通过
8. 进度查询 —— 审核到哪一步
9. 转人工 —— 明确要求人工
10. 投诉 —— 表达不满、质疑、要投诉
11. 无效沟通 —— 无有效诉求

【类目边界】（判断顺序从上到下）
1. 说的是「过去已发生的事」（住院史、检查记录、以前的病）→ 既往症 / 健康告知，
   不归理赔可行性。可行性针对本次或将发生的就诊。
2. 问「多少」（金额、比例、免赔额、上限）→ 费用口径；
   问「能不能」「怎么报」「走什么流程」→ 理赔可行性。
3. 同时有「质疑/不信任」和「要人工」→ 主诉求判「投诉」（先安抚再转），
   「转人工」放 secondary_intents。只有单纯说「转人工」才判转人工。

【无效沟通的子类型】（intent=无效沟通 时必须填 invalid_type）
- 沉默：只选了卡片 / 发了保单，但没有任何提问
- 无关：与保险理赔无关（物流、优惠券、其他业务）
- 无意义：表情、乱码、重复刷屏、无法理解

【槽位】（没有就填 null，禁止猜测）
product     产品名称，如"门诊险""百万医疗"
scene       门诊 / 住院 / 药店购药 / 线上问诊
cause       疾病 / 意外
insured_at  投保日期，原样保留
incident_at 出险日期（就诊日或入院日），原样保留

【规则】
- 只抽取用户明确说过的，不推断。「三甲」不代表「公立」。
- 「脚扭了 / 摔伤 / 烫伤」→ cause=意外；「感冒 / 结节 / 发炎」→ cause=疾病。
- 时间、数字原样保留，不换算、不补全。
- 一句话含多个诉求时，intent 填主诉求，其余放 secondary_intents。
- 出现辱骂、投诉倾向、「骗人」→ urgency="high"。

【输出格式】只输出 JSON，不要代码块标记：
{"intent":"","secondary_intents":[],"invalid_type":null,"slots":{"product":null,"scene":null,"cause":null,"insured_at":null,"incident_at":null},"urgency":"normal","notes":""}"""


def extract(question: str) -> dict:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": question},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(URL, headers=headers, json=data, timeout=20)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "intent": "其他",
            "secondary_intents": [],
            "invalid_type": None,
            "slots": {"product": None, "scene": None, "cause": None,
                      "insured_at": None, "incident_at": None, "claimed": None},
            "urgency": "normal",
            "notes": "JSON 解析失败，已兜底",
        }