import json
def main():
    answer_set = set()

    # 读取文件，将每一行按照JSON解析存入数据集数组
    articles = []
    with open('1南京街头100篇ocr清洗_ERINE信息抽取_已校对.jsonl', 'r', encoding='UTF-8') as f:
        for line in f:
            # 循环每一篇南京街头文章，增加score字段，默认填写0
            article = json.loads(line.strip())
            articles.append(article)

    with open('2（2020届九年级）初三下学期学情调研_ERINE信息抽取_已校对.jsonl', 'r', encoding='UTF-8') as f:
        for line in f:
            # 循环每一篇南京街头文章，增加score字段，默认填写0
            article = json.loads(line.strip())
            articles.append(article)

    # 自集合中取出答案和其他答案按照两两对比列举
    for article in articles:
        qas = article['qa']
        for qa in qas:
            answer = qa['answer'].strip()
            answer_set.add(answer)

    # 列举全部答案
    print(answer_set)

main()