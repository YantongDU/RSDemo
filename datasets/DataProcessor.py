import csv
import operator
import os.path
import pickle

dataset = './sample_train-item-views.csv'
sess_clicks = {}
with open(dataset, "r") as f:
    reader = csv.DictReader(f, delimiter=';')
    for data in reader:
        session_id = data['session_id']
        item = data['item_id'], int(data['timeframe'])
        if session_id in sess_clicks:
            sess_clicks[session_id] += [item]
        else:
            sess_clicks[session_id] = [item]

    for i in list(sess_clicks):
        sorted_clicks = sorted(sess_clicks[i], key=operator.itemgetter(1))
        sess_clicks[i] = [c[0] for c in sorted_clicks]

# 统计每一个item出现的次数
item_stats = {}
for i in list(sess_clicks):
    session = sess_clicks[i]
    for session_id in session:
        if session_id in item_stats:
            item_stats[session_id] += 1
        else:
            item_stats[session_id] = 1
print('The number of Session is [%d]' % len(sess_clicks))
print('Total item number is [%d]' % len(item_stats))

# 先去掉session中出现次数少于5次的item，然后过滤掉session长度小于2的session
for s in list(sess_clicks):
    item_seq = sess_clicks[s]
    seq = list(filter(lambda x: item_stats[x] >= 5, item_seq))
    if len(seq) < 2:
        del sess_clicks[s]
    else:
        sess_clicks[s] = seq

item_map = {}
sess_data = {}
session_cnt = 0
item_cnt = 1

for i in sess_clicks:
    session_detail = sess_clicks[i]
    item_seq = []
    for item in session_detail:
        if item not in item_map:
            item_map[item] = item_cnt
            item_cnt += 1
        item_seq.append(item_map[item])
    sess_data[session_cnt] = item_seq
    session_cnt += 1

# 取前n个item作为input，最后一个item作为label
session_num = len(sess_data)
split = session_num * 0.8

train_set = []
train_labels = []
test_set = []
test_labels = []

for i in sess_data:
    if i < split:
        train_set.append(sess_data[i][:-1])
        train_labels.append(sess_data[i][-1])
    else:
        test_set.append(sess_data[i][:-1])
        test_labels.append(sess_data[i][-1])

print('#train_set:[%d]' % len(train_set))
print('#test_set: [%d]' % len(test_set))
print('#sess_data:[%d]' % len(sess_data))
print('finish')
train = (train_set, train_labels)
test = (test_set, test_labels)

if not os.path.exists('./datasets/sample'):
    os.makedirs('./datasets/sample')
pickle.dump(train, open('./datasets/sample/train.txt', 'wb'))
pickle.dump(test, open('./datasets/sample/test.txt', 'wb'))

