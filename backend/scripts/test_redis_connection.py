"""
Redis 连接测试脚本
用于验证 Redis 配置是否正确
"""
import sys
import os

# 添加后端路径到 sys.path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

try:
    import redis
    from config import settings
    
    print("=" * 50)
    print("Redis 连接测试")
    print("=" * 50)
    
    # 显示配置
    print(f"\n📋 当前配置:")
    print(f"   REDIS_URL: {settings.REDIS_URL}")
    
    try:
        # 创建连接
        print(f"\n🔌 正在连接 Redis...")
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # 测试 ping
        print(f"   发送 PING...")
        response = r.ping()
        print(f"   ✅ 收到响应: {response}")
        
        # 测试写入
        print(f"\n📝 测试写入操作...")
        test_key = "omnimarket:test:connection"
        test_value = "Redis connection test successful!"
        r.set(test_key, test_value, ex=60)  # 60秒后过期
        print(f"   ✅ 写入成功: {test_key} = {test_value}")
        
        # 测试读取
        print(f"\n📖 测试读取操作...")
        retrieved_value = r.get(test_key)
        print(f"   ✅ 读取成功: {retrieved_value}")
        
        # 测试删除
        print(f"\n🗑️  清理测试数据...")
        r.delete(test_key)
        print(f"   ✅ 删除成功")
        
        # 获取 Redis 信息
        print(f"\n📊 Redis 服务器信息:")
        info = r.info()
        print(f"   版本: {info.get('redis_version', 'N/A')}")
        print(f"   运行模式: {info.get('redis_mode', 'N/A')}")
        print(f"   已用内存: {info.get('used_memory_human', 'N/A')}")
        print(f"   键数量: {r.dbsize()}")
        print(f"   连接数: {info.get('connected_clients', 'N/A')}")
        
        # 测试TTL
        print(f"\n⏱️  测试 TTL (生存时间)...")
        ttl_test_key = "omnimarket:test:ttl"
        r.setex(ttl_test_key, 10, "This key expires in 10 seconds")
        ttl = r.ttl(ttl_test_key)
        print(f"   ✅ TTL 设置成功: {ttl} 秒")
        r.delete(ttl_test_key)
        
        print(f"\n" + "=" * 50)
        print(f"✅ Redis 配置正确！系统已就绪！")
        print(f"=" * 50)
        print(f"\n💡 提示:")
        print(f"   - Redis 缓存已启用")
        print(f"   - 系统性能将显著提升")
        print(f"   - API 调用将大幅减少")
        print(f"\n🚀 现在可以启动 OmniMarket 系统了！\n")
        
        sys.exit(0)
        
    except redis.ConnectionError as e:
        print(f"\n❌ Redis 连接失败: {e}\n")
        print(f"请检查:")
        print(f"  1. Redis 服务是否正在运行")
        print(f"     Windows: sc query Memurai")
        print(f"     Docker:  docker ps | findstr redis")
        print(f"     WSL2:    sudo service redis-server status")
        print(f"\n  2. REDIS_URL 配置是否正确")
        print(f"     当前: {settings.REDIS_URL}")
        print(f"     正确格式:")
        print(f"       - redis://localhost:6379")
        print(f"       - redis://:password@localhost:6379")
        print(f"\n  3. 防火墙是否阻止连接")
        print(f"     端口: 6379")
        print(f"\n  4. 查看详细文档:")
        print(f"     REDIS_SETUP_GUIDE.md")
        print(f"\n")
        sys.exit(1)
        
    except redis.AuthenticationError as e:
        print(f"\n❌ Redis 认证失败: {e}\n")
        print(f"请检查:")
        print(f"  1. Redis 密码是否正确")
        print(f"  2. REDIS_URL 格式:")
        print(f"     有密码: redis://:your-password@localhost:6379")
        print(f"     无密码: redis://localhost:6379")
        print(f"\n")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 未知错误: {e}\n")
        print(f"请查看完整错误信息并检查配置")
        print(f"\n")
        sys.exit(1)
        
except ImportError as e:
    print(f"\n❌ 导入错误: {e}\n")
    print(f"请确保已安装 redis 包:")
    print(f"  pip install redis")
    print(f"\n")
    sys.exit(1)
