# 保持原有功能不变，但添加更多统计函数

def calculate_average_score(records, restaurant_name=None, type_=None, start_date=None, end_date=None):
    """
    计算平均评分
    可以按餐厅名称、类型、日期范围进行筛选
    """
    if not records:
        return 0.0
    
    # 筛选记录
    filtered_records = records
    
    # 按餐厅名称筛选
    if restaurant_name:
        filtered_records = [r for r in filtered_records if r[1] == restaurant_name]
    
    # 按类型筛选
    if type_:
        filtered_records = [r for r in filtered_records if r[2] == type_]
    
    # 按日期范围筛选
    if start_date and end_date:
        filtered_records = [r for r in filtered_records if start_date <= r[3] <= end_date]
    
    if not filtered_records:
        return 0.0
    
    total_score = sum(record[4] for record in filtered_records)
    return total_score / len(filtered_records)

def calculate_restaurant_average_scores(records):
    """
    计算每个餐厅的平均评分
    返回一个列表，包含餐厅名称和平均评分
    """
    if not records:
        return []
    
    # 按餐厅名称分组，计算平均分
    restaurant_scores = {}
    for record in records:
        name = record[1]
        score = record[4]
        if name not in restaurant_scores:
            restaurant_scores[name] = {"total": score, "count": 1}
        else:
            restaurant_scores[name]["total"] += score
            restaurant_scores[name]["count"] += 1
    
    # 计算平均分
    restaurant_averages = []
    for name, data in restaurant_scores.items():
        avg = data["total"] / data["count"]
        restaurant_averages.append((name, avg))
    
    # 按评分从高到低排序
    restaurant_averages.sort(key=lambda x: x[1], reverse=True)
    
    return restaurant_averages

def find_most_common_type(records, start_date=None, end_date=None):
    """
    找出最常打卡的类型
    可以按日期范围筛选
    """
    if not records:
        return "无记录"
    
    # 筛选记录
    filtered_records = records
    
    # 按日期范围筛选
    if start_date and end_date:
        filtered_records = [r for r in filtered_records if start_date <= r[3] <= end_date]
    
    if not filtered_records:
        return "无记录"
    
    type_count = {}
    for record in filtered_records:
        type_ = record[2]
        type_count[type_] = type_count.get(type_, 0) + 1
    
    # 找出出现次数最多的类型
    most_common = max(type_count.items(), key=lambda x: x[1])
    return f"{most_common[0]} ({most_common[1]}次)"

def get_top_restaurants(records, limit=5, type_=None):
    """
    获取评分最高的餐厅
    可以按类型筛选
    """
    if not records:
        return []
    
    # 筛选记录
    filtered_records = records
    
    # 按类型筛选
    if type_:
        filtered_records = [r for r in filtered_records if r[2] == type_]
    
    if not filtered_records:
        return []
    
    # 按餐厅名称分组，计算平均分
    restaurant_scores = {}
    for record in filtered_records:
        name = record[1]
        score = record[4]
        if name not in restaurant_scores:
            restaurant_scores[name] = {"total": score, "count": 1}
        else:
            restaurant_scores[name]["total"] += score
            restaurant_scores[name]["count"] += 1
    
    # 计算平均分
    for name in restaurant_scores:
        restaurant_scores[name]["average"] = restaurant_scores[name]["total"] / restaurant_scores[name]["count"]
    
    # 排序并返回前N个
    top_restaurants = sorted(
        [(name, data["average"]) for name, data in restaurant_scores.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    return top_restaurants[:limit]

# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_records = [
        (1, '海底捞', '火锅', '2023-10-01', 9.5, '服务好'),
        (2, '小四川', '川菜', '2023-10-02', 8.0, '麻辣'),
        (3, '重庆火锅', '火锅', '2023-10-03', 8.5, '正宗'),
        (4, '川味坊', '川菜', '2023-10-04', 7.5, '一般'),
    ]
    
    print("总体平均评分:", calculate_average_score(test_records))
    print("火锅类平均评分:", calculate_average_score(test_records, type_="火锅"))
    print("最常打卡的类型:", find_most_common_type(test_records))
    print("评分最高的餐厅:", get_top_restaurants(test_records, limit=3))