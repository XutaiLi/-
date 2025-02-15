import pandas as pd

# 读取CSV文件
df = pd.read_csv('hotels_hefei.csv')

# 按照id列去重,保留第一次出现的记录
df_deduplicated = df.drop_duplicates(subset=['id'], keep='first')

# 保存去重后的数据到新的CSV文件
df_deduplicated.to_csv('hotels_hefei_single.csv', index=False, encoding='utf-8-sig')

print('去重完成!')
print(f'原始数据条数: {len(df)}')
print(f'去重后数据条数: {len(df_deduplicated)}')
