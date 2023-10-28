# -*- coding: utf-8 -*
import wenxin_api
import json
from wenxin_api.tasks.free_qa import FreeQA

# API Key和Secret Key
# wenxin_api.ak = "4zLSoZ13eRa2Ki6tqxzxOF9s3i8nB9ug" #输入您的API Key
# wenxin_api.sk = "juU81059kx9X17ZZq9oafrL94gKVIMIq" #输入您的Secret Key

# API Key和Secret Key
wenxin_api.ak = "rsgMAkpeFn0qIRivYXHYmFCjtmt37Ids" #输入您的API Key
wenxin_api.sk = "ZpRBKlEXyMqmV9PUi04sHeha41xyneOo" #输入您的Secret Key

def save_articles(filename, articles):
    # 将以上结果记入实验数据集,写盘
    with open(filename, 'w', encoding="utf-8") as f:
        for article in articles:
            # 逐行写入JSON
            f.write(json.dumps(article, ensure_ascii=False) + '\n')


def main():
    # 1. 读取文件，将每一行按照JSON解析存入数据集数组
    articles = []
    filename = '3（2020届九年级）初三下学期学情调研_ERINE信息抽取.jsonl'
    with open(filename, 'r', encoding="utf-8") as f:
        for line in f:
            articles.append(json.loads(line.strip()))
    
    # 2. 进行问答
    questions = ['是街头发生故事或风景吗？', '发生在南京吗？']
    count = 0
    for article in articles:
        # 处理过了就跳过
        if(('qa' in article) and (len(article['qa']) == len(questions))):
            count += 1
            print('{:.2f}% -'.format(count * 100 / len(articles)))
            continue

        article['qa'] = []

        for question in questions:
            if not article['text'] or len(article['text']) == 0:
                raise Exception('文章必须都有正文！')

            # 生成问题并检测长度限制
            ask = article['text'] + ' 问题：' + question + '回答：'

            if(len(ask) > 1000):
                print('警告，模型输入长度不得超过1000字，本篇' + str(len(ask)) + '字，跳过：\n' + ask);
                continue

            # 请参考 https://wenxin.baidu.com/AIDP/wenxin/2l6tgx5rc
            # 生成请求内容
            request = {
                "text": ask, # 全文[1, 1000]字
                "min_dec_len": 2, # 输出结果的最小长度，避免因模型生成END导致生成长度过短的情况，与seq_len结合使用来设置生成文本的长度范围。
                "min_dec_penalty_text": "。?：！[<S>]", # 与最小生成长度搭配使用，可以在min_dec_len步前不让模型生成该字符串中的tokens。
                "seq_len": 64, # 答案以后限制在8字以内（生成答案的样本空间尽量小一点）
                "topp": 0.0, # 影响输出文本的多样性，取值越大，生成文本的多样性越强。 [0.0,1.0]，间隔0.1
                "penalty_score": 1.0, # 通过对已生成的token增加惩罚，减少重复生成的现象。值越大表示惩罚越大。设置过大会导致长文本生成效果变差。
                "is_unidirectional": 0, # 0表示模型为双向生成，1表示模型为单向生成。建议续写与few-shot等通用场景建议采用单向生成方式，而完型填空等任务相关场景建议采用双向生成方式。
                "task_prompt": "QA_MRC", # 信息抽取
                "logits_bias": -5,
                "mask_type": "word" # 设置该值可以控制模型生成粒度。
            }

            # 发起请求获得摘要，结果是否正常？异常报错
            try:
                response = FreeQA.create(**request)
            except:
                print(article['text'])
                # 存盘
                save_articles(filename, articles)
                print('异常中止')
                return False

            # response = { "result": '流程测试' }
                
            # 回写结果到对象
            article['qa'].append({"question": question, "answer": response['result']})

        count += 1
        print('{:.2f}%'.format(count * 100 / len(articles)))

    # 存盘
    save_articles(filename, articles)

    # 执行完毕
    print('执行完毕')

main()
