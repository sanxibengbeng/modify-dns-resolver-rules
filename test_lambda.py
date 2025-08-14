#!/usr/bin/env python3
"""
测试Lambda函数的脚本
"""

import json
from lambda_function import lambda_handler

def test_associate():
    """测试关联操作"""
    event = {
        "action": "associate",
        "resolver_rule_id": "rslvr-rr-4434e3b2252648c2a",
        "vpc_id": "vpc-0c443442382a4d7ca"
    }
    
    context = {}  # Lambda context对象，测试时可以为空
    
    print("测试关联操作:")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    result = lambda_handler(event, context)
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print("-" * 50)


def test_disassociate():
    """测试解除关联操作"""
    event = {
        "action": "disassociate",
        "resolver_rule_id": "rslvr-rr-example123456",
        "vpc_id": "vpc-example123456"
    }
    
    context = {}
    
    print("测试解除关联操作:")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    result = lambda_handler(event, context)
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print("-" * 50)


def test_invalid_action():
    """测试无效操作"""
    event = {
        "action": "invalid_action",
        "resolver_rule_id": "rslvr-rr-example123456",
        "vpc_id": "vpc-example123456"
    }
    
    context = {}
    
    print("测试无效操作:")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    result = lambda_handler(event, context)
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print("-" * 50)


def test_missing_parameters():
    """测试缺少参数"""
    event = {
        "action": "associate",
        "resolver_rule_id": "rslvr-rr-example123456"
        # 缺少vpc_id
    }
    
    context = {}
    
    print("测试缺少参数:")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    result = lambda_handler(event, context)
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print("-" * 50)


if __name__ == "__main__":
    print("开始测试Lambda函数...")
    print("=" * 50)
    
    # 注意: 这些测试会尝试调用真实的AWS API
    # 确保你有适当的AWS凭证配置
    
    test_associate()
    test_disassociate()
    test_invalid_action()
    test_missing_parameters()
    
    print("测试完成!")
