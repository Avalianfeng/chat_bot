import requests
import json

BASE_URL = "http://localhost:8000"

# 1. 创建会话
session = requests.Session()

# 2. 登录
print("正在登录...")
login_response = session.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)

print(f"登录状态码: {login_response.status_code}")
if login_response.status_code != 200:
    print(f"登录失败: {login_response.text}")
    exit(1)

login_data = login_response.json()
print(f"登录成功！当前用户: {login_data.get('user', {}).get('username')}\n")

# 3. 获取用户输入
username_input = input("请输入要搜索的用户名（输入 0 查看全部账户）: ").strip()

if not username_input:
    print("输入为空，退出程序")
    exit(0)

# 4. 根据输入决定调用哪个接口
if username_input == "0":
    # 获取所有用户
    print("\n正在获取所有用户...")
    response = session.get(
        f"{BASE_URL}/admin/users",
        params={"skip": 0, "limit": 1000}  # 获取最多1000个用户
    )
    search_type = "全部用户"
else:
    # 搜索用户
    print(f"\n正在搜索用户名包含 '{username_input}' 的用户...")
    response = session.get(
        f"{BASE_URL}/admin/users/search",
        params={"username": username_input, "limit": 1000}
    )
    search_type = f"包含 '{username_input}' 的用户"

# 5. 检查响应状态
if response.status_code != 200:
    print(f"请求失败 (状态码: {response.status_code}): {response.text}")
    exit(1)

# 6. 解析并显示结果
try:
    users = response.json()
    
    # 检查返回的是否是列表
    if not isinstance(users, list):
        print(f"错误: 预期返回列表，但收到: {type(users)}")
        print(f"实际内容: {users}")
        exit(1)
    
    if len(users) == 0:
        print(f"\n未找到 {search_type}")
    else:
        print(f"\n找到 {len(users)} 个{search_type}:\n")
        print("-" * 80)
        print(f"{'ID':<6} {'用户名':<20} {'API Key状态':<15} {'创建时间':<20}")
        print("-" * 80)
        
        for user in users:
            if isinstance(user, dict):
                user_id = user.get('id', 'N/A')
                username = user.get('username', 'N/A')
                api_key = user.get('api_key')
                created_at = user.get('created_at', 'N/A')
                
                # 格式化 API Key 状态
                if api_key:
                    try:
                        api_keys = json.loads(api_key) if isinstance(api_key, str) else api_key
                        if isinstance(api_keys, dict):
                            providers = [k for k, v in api_keys.items() if v]
                            api_status = ", ".join(providers) if providers else "已配置"
                        else:
                            api_status = "已配置"
                    except:
                        api_status = "已配置"
                else:
                    api_status = "未配置"
                
                # 格式化创建时间（只显示日期和时间部分）
                if created_at and created_at != 'N/A':
                    try:
                        created_at = created_at.split('T')[0] + ' ' + created_at.split('T')[1].split('.')[0]
                    except:
                        pass
                
                print(f"{user_id:<6} {username:<20} {api_status:<15} {created_at:<20}")
            else:
                print(f"  警告: 用户数据格式异常: {user}")
        
        print("-" * 80)
        print(f"\n总计: {len(users)} 个用户")
            
except json.JSONDecodeError as e:
    print(f"JSON 解析错误: {e}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"发生错误: {type(e).__name__}: {e}")
    print(f"响应内容: {response.text}")