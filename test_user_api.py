"""测试用户管理 API"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_create_user():
    """测试创建用户"""
    print("=" * 50)
    print("测试创建用户")
    print("=" * 50)
    
    # 测试数据
    user_data = {
        "username": "test_user",
        "password": "test_password_123",
        "api_key": "test_api_key_optional"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/create_user",
            json=user_data
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✓ 创建用户成功")
            return response.json()
        else:
            print(f"✗ 创建用户失败: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保 web_app.py 正在运行")
        return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def test_list_users():
    """测试获取用户列表"""
    print("\n" + "=" * 50)
    print("测试获取用户列表")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/users")
        
        print(f"状态码: {response.status_code}")
        users = response.json()
        print(f"用户数量: {len(users)}")
        print(f"响应: {json.dumps(users, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✓ 获取用户列表成功")
            return users
        else:
            print(f"✗ 获取用户列表失败: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保 web_app.py 正在运行")
        return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def test_get_user(user_id: int):
    """测试根据 ID 获取用户"""
    print("\n" + "=" * 50)
    print(f"测试获取用户 ID={user_id}")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/users/{user_id}")
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✓ 获取用户成功")
            return response.json()
        else:
            print(f"✗ 获取用户失败: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保 web_app.py 正在运行")
        return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def test_duplicate_username():
    """测试重复用户名"""
    print("\n" + "=" * 50)
    print("测试重复用户名（应该失败）")
    print("=" * 50)
    
    user_data = {
        "username": "test_user",  # 使用已存在的用户名
        "password": "another_password",
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/create_user",
            json=user_data
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 400:
            print("✓ 正确拒绝了重复用户名")
        else:
            print("✗ 应该拒绝重复用户名，但返回了其他状态码")
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保 web_app.py 正在运行")
    except Exception as e:
        print(f"✗ 错误: {e}")


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("用户管理 API 测试")
    print("=" * 50)
    print("\n请确保 web_app.py 正在运行（uvicorn web_app:app）")
    print("按 Enter 继续...")
    input()
    
    # 测试创建用户
    user = test_create_user()
    
    # 测试获取用户列表
    users = test_list_users()
    
    # 如果创建成功，测试获取单个用户
    if user:
        test_get_user(user["id"])
    
    # 测试重复用户名
    test_duplicate_username()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
