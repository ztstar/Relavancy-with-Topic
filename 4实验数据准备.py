import json

# 答案正规化字典
answer_regular_dict = {
    '是': '是',
    '是的': '是',
    '是的。': '是',
    '是街头发生故事或风景': '是',
    '不确定': '不确定',
    '不是': '否',
}

# 保存文章
def save_articles(filename, articles):
    # 将以上结果记入实验数据集,写盘
    with open(filename, 'w', encoding="utf-8") as f:
        for article in articles:
            # 逐行写入JSON
            f.write(json.dumps(article, ensure_ascii=False) + '\n')


# 根据已审校的200篇作文作答情况，抽取较有特征的作文篇章教师试改，得到每篇文章的教师切题水平评价。
def main():
    # 读取文件，将每一行按照JSON解析存入数据集数组
    answer_key_articles_dict = {}

    with open('1南京街头100篇ocr清洗_ERINE信息抽取_已校对.jsonl', 'r', encoding='UTF-8') as f:
        for line in f:
            # 循环每一篇南京街头文章
            article = json.loads(line.strip())

            # 生成文章答案索引
            answer_keys = []
            qas = article['qa']
            for qa in qas:
                # 将各问题答案映射到允许答案（是、否和不确定）上
                raw_answer = qa['answer'].strip()
                if raw_answer not in answer_regular_dict:
                    raise Exception('未在答案正规化字典中找到' + raw_answer + '对应的答案')
                
                answer = answer_regular_dict[raw_answer]
                qa['answer'] = answer
                answer_keys.append(answer)

            # 将教师评价作文分数映射到教师评价切题程度上（切题、一般和走题）上
            score = article['score']
            on_point = None
            if score >= 35 and score <= 50:
                on_point = '切题'
            elif score >= 18 and score <= 34:
                on_point = '一般'
            else:
                on_point = '走题'
            
            article['on_point'] = on_point

            # 按答案索引分类存放
            answer_key = '_'.join(answer_keys)

            if answer_key not in answer_key_articles_dict:
                answer_key_articles_dict[answer_key] = []
            
            answer_key_articles = answer_key_articles_dict[answer_key]
            answer_key_articles.append(article)

    # 加载南京街头 JSONL数据集
    with open('2（2020届九年级）初三下学期学情调研_ERINE信息抽取_已校对.jsonl', 'r', encoding='UTF-8') as f:
        for line in f:
            # 循环每一篇南京街头文章
            article = json.loads(line.strip())

            # 生成文章答案索引
            answer_keys = []
            qas = article['qa']
            for qa in qas:
                # 将各问题答案映射到允许答案（是、否和不确定）上
                raw_answer = qa['answer'].strip()
                if raw_answer not in answer_regular_dict:
                    raise Exception('未在答案正规化字典中找到' + raw_answer + '对应的答案')
                
                answer = answer_regular_dict[raw_answer]
                qa['answer'] = answer
                answer_keys.append(answer)

            # 将教师评价作文分数映射到教师评价切题程度上（切题、一般和走题）上
            answer_key = '_'.join(answer_keys)
            on_point = '一般'
            if answer_key == '是_是':
                on_point = '切题'
            elif answer_key.find('否') != -1:
                on_point = '走题'
            else:
                print(article)
                raise Exception('其他文章中未处理的切题程度情景' + answer_key)
            article['on_point'] = on_point

            # 按答案索引分类存放
            if answer_key not in answer_key_articles_dict:
                answer_key_articles_dict[answer_key] = []
            
            answer_key_articles = answer_key_articles_dict[answer_key]
            answer_key_articles.append(article)


    # 每个分类抽取两篇作为训练集，其他作为测试集
    train_set = []
    test_set = []

    for key in answer_key_articles_dict:
        articles = answer_key_articles_dict[key]
        print(key, len(articles))
        if len(articles) == 1:
            print('注意' + key + '分类的文章只有一篇，只能是训练和测试集里面都有这些文章了')
            train_set += articles
            test_set += articles
        elif len(articles) == 2:
            train_set += articles[1]
            test_set += articles[1:]
        else:
            train_set += articles[0:2]
            test_set += articles[2:]

    save_articles('训练集.jsonl', train_set)
    save_articles('测试集.jsonl', test_set)

main()