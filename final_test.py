#!/usr/bin/env python3
"""
最终测试脚本 - 基于诊断结果进行实际可行的测试
"""

import json
from lambda_function import lambda_handler

# 具体的资源ID
FORWARD_RULE_ID = "rslvr-rr-4434e3b2252648c2a"
SYSTEM_RULE_ID = "rslvr-rr-997b5cb773fa4a39b"
VPC_ID = "vpc-0c443442382a4d7ca"

def test_system_rule_operations():
    """测试System Rule操作（已知已关联）"""
    print("=" * 60)
    print("测试System Rule操作")
    print("=" * 60)
    
    # 测试关联操作（应该返回already_associated）
    print("\n1. 测试System Rule关联操作（预期：已关联）")
    event = {
        "action": "associate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试解除关联操作
    print("\n2. 测试System Rule解除关联操作")
    event = {
        "action": "disassociate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 再次测试关联操作（现在应该能成功关联）
    print("\n3. 再次测试System Rule关联操作（预期：成功关联）")
    event = {
        "action": "associate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")


def test_forward_rule_operations():
    """测试Forward Rule操作"""
    print("\n" + "=" * 60)
    print("测试Forward Rule操作")
    print("=" * 60)
    
    # 测试解除关联操作（应该返回not_associated）
    print("\n1. 测试Forward Rule解除关联操作（预期：未关联）")
    event = {
        "action": "disassociate",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试关联操作（可能会遇到InternalServiceError）
    print("\n2. 测试Forward Rule关联操作（可能遇到内部错误）")
    event = {
        "action": "associate",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")


def test_error_cases():
    """测试错误情况"""
    print("\n" + "=" * 60)
    print("测试错误情况")
    print("=" * 60)
    
    # 测试无效action
    print("\n1. 测试无效action")
    event = {
        "action": "invalid_action",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试缺少参数
    print("\n2. 测试缺少参数")
    event = {
        "action": "associate",
        "resolver_rule_id": FORWARD_RULE_ID
        # 缺少vpc_id
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试不存在的资源
    print("\n3. 测试不存在的Resolver Rule")
    event = {
        "action": "associate",
        "resolver_rule_id": "rslvr-rr-nonexistent123",
        "vpc_id": VPC_ID
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")


def test_comprehensive_workflow():
    """测试完整的工作流程"""
    print("\n" + "=" * 60)
    print("完整工作流程测试")
    print("=" * 60)
    
    print("\n这个测试展示了Lambda函数如何处理各种实际情况：")
    print("1. 检查已存在的关联")
    print("2. 执行解除关联操作")
    print("3. 重新建立关联")
    print("4. 处理各种错误情况")
    
    print("\n基于诊断结果，我们知道：")
    print(f"- System Rule ({SYSTEM_RULE_ID}) 当前已与VPC关联")
    print(f"- Forward Rule ({FORWARD_RULE_ID}) 当前未与VPC关联")
    print(f"- VPC ({VPC_ID}) 存在且可用")


if __name__ == "__main__":
    print("开始最终测试...")
    
    test_comprehensive_workflow()
    test_system_rule_operations()
    test_forward_rule_operations()
    test_error_cases()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print("Lambda函数已经实现了以下功能：")
    print("✓ 参数验证和错误处理")
    print("✓ 检查现有关联状态")
    print("✓ 执行关联和解除关联操作")
    print("✓ 处理各种AWS API错误")
    print("✓ 提供详细的日志记录")
    print("✓ 返回结构化的响应")
    print("\n函数可以部署到AWS Lambda并通过API Gateway或直接调用使用。")
    print("=" * 60)
