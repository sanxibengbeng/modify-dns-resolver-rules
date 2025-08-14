#!/usr/bin/env python3
"""
诊断Route53 Resolver规则的详细信息
"""

import json
import boto3
from botocore.exceptions import ClientError

# 具体的资源ID
FORWARD_RULE_ID = "rslvr-rr-4434e3b2252648c2a"
SYSTEM_RULE_ID = "rslvr-rr-997b5cb773fa4a39b"
VPC_ID = "vpc-0c443442382a4d7ca"
REGION = "us-west-2"

def diagnose_resolver_rules():
    """诊断Resolver规则"""
    print("=" * 60)
    print("Route53 Resolver规则诊断")
    print("=" * 60)
    
    resolver_client = boto3.client('route53resolver', region_name=REGION)
    
    # 检查Forward Rule
    print(f"\n1. 检查Forward Rule: {FORWARD_RULE_ID}")
    try:
        response = resolver_client.get_resolver_rule(ResolverRuleId=FORWARD_RULE_ID)
        rule = response['ResolverRule']
        print(f"   ✓ 规则存在")
        print(f"   名称: {rule.get('Name', 'N/A')}")
        print(f"   类型: {rule.get('RuleType', 'N/A')}")
        print(f"   域名: {rule.get('DomainName', 'N/A')}")
        print(f"   状态: {rule.get('Status', 'N/A')}")
        print(f"   创建者账户: {rule.get('CreatorRequestId', 'N/A')}")
        print(f"   所有者账户: {rule.get('OwnerId', 'N/A')}")
        print(f"   共享状态: {rule.get('ShareStatus', 'N/A')}")
        
        # 检查目标IP
        if 'TargetIps' in rule:
            print(f"   目标IP:")
            for target in rule['TargetIps']:
                print(f"     - {target.get('Ip', 'N/A')}:{target.get('Port', 'N/A')}")
    except ClientError as e:
        print(f"   ✗ 错误: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
    
    # 检查System Rule
    print(f"\n2. 检查System Rule: {SYSTEM_RULE_ID}")
    try:
        response = resolver_client.get_resolver_rule(ResolverRuleId=SYSTEM_RULE_ID)
        rule = response['ResolverRule']
        print(f"   ✓ 规则存在")
        print(f"   名称: {rule.get('Name', 'N/A')}")
        print(f"   类型: {rule.get('RuleType', 'N/A')}")
        print(f"   域名: {rule.get('DomainName', 'N/A')}")
        print(f"   状态: {rule.get('Status', 'N/A')}")
        print(f"   创建者账户: {rule.get('CreatorRequestId', 'N/A')}")
        print(f"   所有者账户: {rule.get('OwnerId', 'N/A')}")
        print(f"   共享状态: {rule.get('ShareStatus', 'N/A')}")
    except ClientError as e:
        print(f"   ✗ 错误: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
    
    # 检查VPC
    print(f"\n3. 检查VPC: {VPC_ID}")
    try:
        ec2_client = boto3.client('ec2', region_name=REGION)
        response = ec2_client.describe_vpcs(VpcIds=[VPC_ID])
        vpc = response['Vpcs'][0]
        print(f"   ✓ VPC存在")
        print(f"   CIDR: {vpc.get('CidrBlock', 'N/A')}")
        print(f"   状态: {vpc.get('State', 'N/A')}")
        print(f"   默认VPC: {vpc.get('IsDefault', False)}")
    except ClientError as e:
        print(f"   ✗ 错误: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
    
    # 检查当前关联
    print(f"\n4. 检查当前关联状态")
    
    # Forward Rule关联
    print(f"   Forward Rule ({FORWARD_RULE_ID}) 关联:")
    try:
        associations = resolver_client.list_resolver_rule_associations(
            Filters=[
                {
                    'Name': 'ResolverRuleId',
                    'Values': [FORWARD_RULE_ID]
                }
            ]
        )
        if associations['ResolverRuleAssociations']:
            for assoc in associations['ResolverRuleAssociations']:
                print(f"     - 关联ID: {assoc['Id']}")
                print(f"       VPC ID: {assoc['VPCId']}")
                print(f"       状态: {assoc['Status']}")
        else:
            print(f"     - 无关联")
    except ClientError as e:
        print(f"     ✗ 错误: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
    
    # System Rule关联
    print(f"   System Rule ({SYSTEM_RULE_ID}) 关联:")
    try:
        associations = resolver_client.list_resolver_rule_associations(
            Filters=[
                {
                    'Name': 'ResolverRuleId',
                    'Values': [SYSTEM_RULE_ID]
                }
            ]
        )
        if associations['ResolverRuleAssociations']:
            for assoc in associations['ResolverRuleAssociations']:
                print(f"     - 关联ID: {assoc['Id']}")
                print(f"       VPC ID: {assoc['VPCId']}")
                print(f"       状态: {assoc['Status']}")
        else:
            print(f"     - 无关联")
    except ClientError as e:
        print(f"     ✗ 错误: {e.response['Error']['Code']} - {e.response['Error']['Message']}")


def test_manual_association():
    """测试手动关联操作"""
    print(f"\n5. 测试手动关联操作")
    
    resolver_client = boto3.client('route53resolver', region_name=REGION)
    
    # 测试Forward Rule关联
    print(f"   测试Forward Rule关联:")
    try:
        response = resolver_client.associate_resolver_rule(
            ResolverRuleId=FORWARD_RULE_ID,
            VPCId=VPC_ID
        )
        print(f"     ✓ 关联成功")
        print(f"     关联ID: {response['ResolverRuleAssociation']['Id']}")
        print(f"     状态: {response['ResolverRuleAssociation']['Status']}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"     ✗ 关联失败: {error_code} - {error_message}")
        
        # 分析错误原因
        if error_code == 'ResourceNotFoundException':
            print(f"       → 资源不存在（规则或VPC）")
        elif error_code == 'InvalidRequestException':
            print(f"       → 无效请求（可能是规则类型不支持手动关联）")
        elif error_code == 'ResourceExistsException':
            print(f"       → 关联已存在")
        elif error_code == 'LimitExceededException':
            print(f"       → 超出限制")
    
    # 测试System Rule关联
    print(f"   测试System Rule关联:")
    try:
        response = resolver_client.associate_resolver_rule(
            ResolverRuleId=SYSTEM_RULE_ID,
            VPCId=VPC_ID
        )
        print(f"     ✓ 关联成功")
        print(f"     关联ID: {response['ResolverRuleAssociation']['Id']}")
        print(f"     状态: {response['ResolverRuleAssociation']['Status']}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"     ✗ 关联失败: {error_code} - {error_message}")
        
        # 分析错误原因
        if error_code == 'ResourceNotFoundException':
            print(f"       → 资源不存在（规则或VPC）")
        elif error_code == 'InvalidRequestException':
            print(f"       → 无效请求（System规则通常不能手动关联）")
        elif error_code == 'ResourceExistsException':
            print(f"       → 关联已存在")
        elif error_code == 'LimitExceededException':
            print(f"       → 超出限制")


def list_all_resolver_rules():
    """列出所有Resolver规则"""
    print(f"\n6. 列出所有Resolver规则")
    
    resolver_client = boto3.client('route53resolver', region_name=REGION)
    
    try:
        response = resolver_client.list_resolver_rules()
        rules = response['ResolverRules']
        
        print(f"   找到 {len(rules)} 个规则:")
        for rule in rules:
            print(f"     - ID: {rule['Id']}")
            print(f"       名称: {rule.get('Name', 'N/A')}")
            print(f"       类型: {rule.get('RuleType', 'N/A')}")
            print(f"       域名: {rule.get('DomainName', 'N/A')}")
            print(f"       状态: {rule.get('Status', 'N/A')}")
            print(f"       所有者: {rule.get('OwnerId', 'N/A')}")
            print()
    except ClientError as e:
        print(f"   ✗ 错误: {e.response['Error']['Code']} - {e.response['Error']['Message']}")


if __name__ == "__main__":
    diagnose_resolver_rules()
    test_manual_association()
    list_all_resolver_rules()
    
    print("\n" + "=" * 60)
    print("诊断完成!")
    print("=" * 60)
