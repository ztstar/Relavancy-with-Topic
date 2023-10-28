import json
import torch.nn as nn
import torch

# 保存文章
def save_articles(filename, articles):
    # 将以上结果记入实验数据集,写盘
    with open(filename, 'w', encoding="utf-8") as f:
        for article in articles:
            # 逐行写入JSON
            f.write(json.dumps(article, ensure_ascii=False) + '\n')

# 加载数据集
def load_dataset(filename):
    articles = []
    with open(filename, 'r', encoding='UTF-8') as f:
        for line in f:
            # 循环每一篇南京街头文章
            article = json.loads(line.strip())
            articles.append(article)
    
    return articles

class OnTopicRegressionNetwork(nn.Module):
    def __init__(self):
        super(OnTopicRegressionNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(2, 2),
            nn.Sigmoid(),
            nn.Linear(2, 2),
            nn.Sigmoid(),
            nn.Linear(2, 1)
        )
        self.mls = nn.MSELoss()
        self.opt = torch.optim.Adam(params=self.parameters(), lr = 0.001)

    def forward(self, inputs):
        out = self.fc(inputs)
        return out

    def train(self, x, label):
        out = self.forward(x)
        loss = self.mls(out, label)
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

def main():
    # 加载数据
    train_articles = load_dataset('测试集.jsonl')

    # 生成输入和标签
    inputs = []
    labels = []

    answer_type_map = { '是': 1 , '不确定': 2, '否': 3 }
    type_label_map = { 1: '切题', 2: '一般', 3: '走题'}

    for train_article in train_articles:
         # 生成输入
        answers = []
        qas = train_article['qa']
        for qa in qas:
            answer = qa['answer']
            answers.append(answer_type_map[answer])
        
        inputs.append(answers)

        # 生成标签
        on_point = train_article['on_point']
        labels.append(on_point)
    
    # 构造网络
    # net = OnTopicRegressionNetwork()
    # net.load_state_dict(torch.load('切题评价模型.mod'))
    net = torch.load('切题评价模型.mod')

    # 预测并搜集差异文章
    diff_on_topic_articles = []

    for index, input in enumerate(inputs):
        # 这里不加.float()会报错，可能是数据格式的问题吧
        input = torch.Tensor(input)
        ref_label = labels[index]
        predict_label_index = net.forward(input).item()

        # 将预测序号找到与其数值上最接近的下标所对应键
        predict_label = None
        match_label_index = None
        for type_index in type_label_map:
            label = type_label_map[type_index]
            if match_label_index == None:
                match_label_index = type_index
                predict_label = label
                continue
            
            if abs(predict_label_index - type_index) < abs(predict_label_index - match_label_index):
                match_label_index = type_index
                predict_label = label

        # 不一致则进行显示
        if predict_label != ref_label:
            article = train_articles[index]
            diff_on_topic_articles.append(article)

    # 存盘
    save_articles("9模型推测与实际评分有差异文章.jsonl", diff_on_topic_articles)

main()