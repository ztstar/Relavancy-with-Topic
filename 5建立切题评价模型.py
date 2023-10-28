import json
import torch.nn as nn
import torch
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
    train_articles = load_dataset('训练集.jsonl')

    # 生成输入和标签
    inputs = []
    labels = []

    answer_type_map = { '是': 1 , '不确定': 2, '否': 3 }
    label_type_map = { '切题': 1, '一般': 2, '走题': 3}

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
        labels.append([label_type_map[on_point]])
    
    # 构造网络
    net = OnTopicRegressionNetwork()
    for i in range(10000):
        for index, input in enumerate(inputs):
            # 这里不加.float()会报错，可能是数据格式的问题吧
            input = torch.Tensor(input)
            label = torch.Tensor(labels[index])
            net.train(input, label)

    torch.save(net, '切题评价模型.mod')

main()