#!/usr/bin/env python3
"""
包含区域参数的测试脚本
"""

import json
from lambda_function import lambda_handler

# 具体的资源ID
FORWARD_RULE_ID = "rslvr-rr-4434e3b2252648c2a"
SYSTEM_RULE_ID = "rslvr-rr-997b5cb773fa4a39b"
VPC_ID = "vpc-0c443442382a4d7ca"
REGION = "us-west-2"

def test_with_region():
    """测试包含区域参数的操作"""
    print("=" * 60)
    print("测试包含区域参数的操作")
    print("=" * 60)
    
    # 测试解除关联操作（应该成功）
    print("\n1. 测试解除关联操作（包含区域参数）")
    event = {
        "action": "disassociate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID,
        "region": REGION
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试关联操作
    print("\n2. 测试关联操作（包含区域参数）")
    event = {
        "action": "associate",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID,
        "region": REGION
    }
    
    result = lambda_handler(event, {})
    print(f"输入: {json.dumps(event, indent=2)}")
    print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    test_with_region()
