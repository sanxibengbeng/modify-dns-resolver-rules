#!/usr/bin/env python3
"""
简化版Demo：直接调用本地函数更新Route53 Resolver Rule的目标IP
"""

import json
from update_resolver_rule import update_resolver_rule_target_ips, lambda_handler

# 配置参数
RESOLVER_RULE_ID = "rslvr-rr-4434e3b2252648c2a"
TARGET_IPS = ['8.8.8.8', '8.8.4.4']
REGION = "us-west-2"

def demo_direct_call():
    """
    直接调用核心函数
    """
    print("=" * 60)
    print("直接调用核心函数Demo")
    print("=" * 60)
    
    print(f"Resolver Rule ID: {RESOLVER_RULE_ID}")
    print(f"Target IPs: {TARGET_IPS}")
    print(f"Region: {REGION}")
    print("-" * 40)
    
    try:
        result = update_resolver_rule_target_ips(RESOLVER_RULE_ID, TARGET_IPS, REGION)
        print("✅ 函数调用成功!")
        print(f"结果: {json.dumps(result, indent=2, default=str)}")
        
    except Exception as e:
        print(f"❌ 函数调用失败: {str(e)}")
        import traceback
        traceback.print_exc()

def demo_lambda_handler():
    """
    模拟Lambda处理函数调用
    """
    print("=" * 60)
    print("模拟Lambda处理函数调用Demo")
    print("=" * 60)
    
    # 构建事件
    event = {
        'resolver_rule_id': RESOLVER_RULE_ID,
        'target_ips': TARGET_IPS,
        'region': REGION
    }
    
    # 模拟上下文
    class MockContext:
        def __init__(self):
            self.function_name = 'demo-function'
            self.aws_request_id = 'demo-request-id'
    
    context = MockContext()
    
    print(f"Event: {json.dumps(event, indent=2)}")
    print("-" * 40)
    
    try:
        result = lambda_handler(event, context)
        print("✅ Lambda处理函数调用成功!")
        print(f"响应: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Lambda处理函数调用失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数
    """
    print("选择Demo类型:")
    print("1) 直接调用核心函数")
    print("2) 模拟Lambda处理函数调用")
    print("3) 两种方式都执行")
    
    choice = input("请选择 (1, 2, 或 3，默认为3): ").strip() or "3"
    
    if choice == "1":
        demo_direct_call()
    elif choice == "2":
        demo_lambda_handler()
    elif choice == "3":
        demo_direct_call()
        print("\n" + "=" * 60 + "\n")
        demo_lambda_handler()
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
