import sqlite3
from datetime import datetime

class DakaDatabase:
    def __init__(self, db_name='daka_records.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()
    
    def _create_table(self):
        """创建打卡记录表"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                date DATE NOT NULL,
                score REAL NOT NULL,
                comment TEXT,
                image_path TEXT
            )
        ''')
        self.conn.commit()
    
    def add_record(self, name, type_, date, score, comment, image_path=None):
        """添加新的打卡记录"""
        try:
            self.cursor.execute('''
                INSERT INTO records (name, type, date, score, comment, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, type_, date, score, comment, image_path))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加记录失败: {e}")
            return False
    
    def delete_record(self, identifier):
        """删除记录（通过ID或名称）"""
        try:
            # 尝试按ID删除
            if identifier.isdigit():
                self.cursor.execute('DELETE FROM records WHERE id = ?', (identifier,))
            else:
                # 按名称删除
                self.cursor.execute('DELETE FROM records WHERE name = ?', (identifier,))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"删除记录失败: {e}")
            return False
    
    def get_all_records(self):
        """获取所有记录"""
        self.cursor.execute('SELECT * FROM records ORDER BY date DESC')
        return self.cursor.fetchall()
    
    def search_by_name(self, keyword):
        """按名称关键词搜索"""
        self.cursor.execute('''
            SELECT * FROM records 
            WHERE name LIKE ? 
            ORDER BY date DESC
        ''', (f'%{keyword}%',))
        return self.cursor.fetchall()
    
    def filter_by_type(self, type_):
        """按类型筛选"""
        self.cursor.execute('''
            SELECT * FROM records 
            WHERE type = ? 
            ORDER BY date DESC
        ''', (type_,))
        return self.cursor.fetchall()
    
    def get_records_sorted_by_score(self, descending=True):
        """按评分排序获取记录"""
        order = "DESC" if descending else "ASC"
        self.cursor.execute(f'''
            SELECT * FROM records 
            ORDER BY score {order}
        ''')
        return self.cursor.fetchall()
        
    def get_records_by_date_range(self, start_date, end_date):
        """按日期范围筛选记录"""
        self.cursor.execute('''
            SELECT * FROM records 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date DESC
        ''', (start_date, end_date))
        return self.cursor.fetchall()
        
    def get_records_by_restaurant(self, restaurant_name):
        """获取特定餐厅的所有记录"""
        self.cursor.execute('''
            SELECT * FROM records 
            WHERE name = ? 
            ORDER BY date DESC
        ''', (restaurant_name,))
        return self.cursor.fetchall()
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

# 测试代码
if __name__ == "__main__":
    db = DakaDatabase()
    # 添加测试数据
    db.add_record("海底捞火锅", "火锅", "2023-10-01", 9.5, "服务很好")
    db.add_record("小四川", "川菜", "2023-10-05", 8.0, "麻辣鲜香")
    print("所有记录:", db.get_all_records())
    db.close()