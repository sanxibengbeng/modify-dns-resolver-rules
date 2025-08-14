#!/usr/bin/env python3
"""
使用具体资源ID测试Lambda函数
"""

import json
import boto3
from lambda_function import lambda_handler

# 具体的资源ID
FORWARD_RULE_ID = "rslvr-rr-4434e3b2252648c2a"
SYSTEM_RULE_ID = "rslvr-rr-997b5cb773fa4a39b"
VPC_ID = "vpc-0c443442382a4d7ca"
REGION = "us-west-2"

def test_forward_rule_associate():
    """测试Forward Rule关联操作"""
    event = {
        "action": "associate",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    context = {}
    
    print("测试Forward Rule关联操作:")
    print(f"Resolver Rule ID: {FORWARD_RULE_ID}")
    print(f"VPC ID: {VPC_ID}")
    print(f"Region: {REGION}")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    try:
        result = lambda_handler(event, context)
        print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    print("-" * 60)


def test_system_rule_associate():
    """测试System Rule关联操作"""
    event = {
        "action": "associate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    context = {}
    
    print("测试System Rule关联操作:")
    print(f"Resolver Rule ID: {SYSTEM_RULE_ID}")
    print(f"VPC ID: {VPC_ID}")
    print(f"Region: {REGION}")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    try:
        result = lambda_handler(event, context)
        print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    print("-" * 60)


def test_forward_rule_disassociate():
    """测试Forward Rule解除关联操作"""
    event = {
        "action": "disassociate",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    context = {}
    
    print("测试Forward Rule解除关联操作:")
    print(f"Resolver Rule ID: {FORWARD_RULE_ID}")
    print(f"VPC ID: {VPC_ID}")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    try:
        result = lambda_handler(event, context)
        print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    print("-" * 60)


def test_system_rule_disassociate():
    """测试System Rule解除关联操作"""
    event = {
        "action": "disassociate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID
    }
    
    context = {}
    
    print("测试System Rule解除关联操作:")
    print(f"Resolver Rule ID: {SYSTEM_RULE_ID}")
    print(f"VPC ID: {VPC_ID}")
    print(f"输入: {json.dumps(event, indent=2)}")
    
    try:
        result = lambda_handler(event, context)
        print(f"输出: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    print("-" * 60)


def check_current_associations():
    """检查当前的关联状态"""
    print("检查当前关联状态:")
    
    try:
        # 设置区域
        resolver_client = boto3.client('route53resolver', region_name=REGION)
        
        # 检查Forward Rule关联
        print(f"\n检查Forward Rule ({FORWARD_RULE_ID}) 关联:")
        forward_associations = resolver_client.list_resolver_rule_associations(
            Filters=[
                {
                    'Name': 'ResolverRuleId',
                    'Values': [FORWARD_RULE_ID]
                }
            ]
        )
        
        if forward_associations['ResolverRuleAssociations']:
            for assoc in forward_associations['ResolverRuleAssociations']:
                print(f"  关联ID: {assoc['Id']}")
                print(f"  VPC ID: {assoc['VPCId']}")
                print(f"  状态: {assoc['Status']}")
        else:
            print("  无关联")
        
        # 检查System Rule关联
        print(f"\n检查System Rule ({SYSTEM_RULE_ID}) 关联:")
        system_associations = resolver_client.list_resolver_rule_associations(
            Filters=[
                {
                    'Name': 'ResolverRuleId',
                    'Values': [SYSTEM_RULE_ID]
                }
            ]
        )
        
        if system_associations['ResolverRuleAssociations']:
            for assoc in system_associations['ResolverRuleAssociations']:
                print(f"  关联ID: {assoc['Id']}")
                print(f"  VPC ID: {assoc['VPCId']}")
                print(f"  状态: {assoc['Status']}")
        else:
            print("  无关联")
            
    except Exception as e:
        print(f"检查关联状态时出错: {str(e)}")
    
    print("-" * 60)


def get_resolver_rule_info():
    """获取Resolver规则信息"""
    print("获取Resolver规则信息:")
    
    try:
        resolver_client = boto3.client('route53resolver', region_name=REGION)
        
        # 获取Forward Rule信息
        print(f"\nForward Rule ({FORWARD_RULE_ID}) 信息:")
        try:
            forward_rule = resolver_client.get_resolver_rule(
                ResolverRuleId=FORWARD_RULE_ID
            )
            rule = forward_rule['ResolverRule']
            print(f"  名称: {rule.get('Name', 'N/A')}")
            print(f"  类型: {rule.get('RuleType', 'N/A')}")
            print(f"  域名: {rule.get('DomainName', 'N/A')}")
            print(f"  状态: {rule.get('Status', 'N/A')}")
        except Exception as e:
            print(f"  获取Forward Rule信息失败: {str(e)}")
        
        # 获取System Rule信息
        print(f"\nSystem Rule ({SYSTEM_RULE_ID}) 信息:")
        try:
            system_rule = resolver_client.get_resolver_rule(
                ResolverRuleId=SYSTEM_RULE_ID
            )
            rule = system_rule['ResolverRule']
            print(f"  名称: {rule.get('Name', 'N/A')}")
            print(f"  类型: {rule.get('RuleType', 'N/A')}")
            print(f"  域名: {rule.get('DomainName', 'N/A')}")
            print(f"  状态: {rule.get('Status', 'N/A')}")
        except Exception as e:
            print(f"  获取System Rule信息失败: {str(e)}")
            
    except Exception as e:
        print(f"获取规则信息时出错: {str(e)}")
    
    print("-" * 60)


if __name__ == "__main__":
    print("开始测试具体资源的Lambda函数...")
    print("=" * 60)
    print(f"测试区域: {REGION}")
    print(f"Forward Rule ID: {FORWARD_RULE_ID}")
    print(f"System Rule ID: {SYSTEM_RULE_ID}")
    print(f"VPC ID: {VPC_ID}")
    print("=" * 60)
    
    # 首先检查当前状态
    get_resolver_rule_info()
    check_current_associations()
    
    # 测试关联操作
    test_forward_rule_associate()
    test_system_rule_associate()
    
    # 再次检查状态
    check_current_associations()
    
    # 测试解除关联操作
    test_forward_rule_disassociate()
    test_system_rule_disassociate()
    
    # 最终检查状态
    check_current_associations()
    
    print("测试完成!")
