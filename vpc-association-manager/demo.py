#!/usr/bin/env python3
"""
Route53 Resolver规则管理Lambda函数演示
"""

import json
import time
from lambda_function import lambda_handler

# 你的具体资源ID
FORWARD_RULE_ID = "rslvr-rr-4434e3b2252648c2a"
SYSTEM_RULE_ID = "rslvr-rr-997b5cb773fa4a39b"
VPC_ID = "vpc-0c443442382a4d7ca"
REGION = "us-west-2"

def print_separator(title):
    """打印分隔符"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_result(event, result):
    """打印结果"""
    print(f"\n输入:")
    print(json.dumps(event, indent=2))
    print(f"\n输出:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 解析结果
    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"\n✅ 操作成功: {body['message']}")
        if 'result' in body:
            result_data = body['result']
            if 'association_id' in result_data:
                print(f"   关联ID: {result_data['association_id']}")
            print(f"   状态: {result_data['status']}")
    else:
        body = json.loads(result['body'])
        print(f"\n❌ 操作失败: {body.get('error', '未知错误')}")
        print(f"   详细信息: {body.get('message', '无详细信息')}")

def demo_complete_workflow():
    """演示完整的工作流程"""
    print_separator("Route53 Resolver规则管理Lambda函数演示")
    
    print(f"""
这个演示将展示Lambda函数的完整功能：

📋 测试环境信息:
   - Forward Rule ID: {FORWARD_RULE_ID}
   - System Rule ID: {SYSTEM_RULE_ID}
   - VPC ID: {VPC_ID}
   - Region: {REGION}

🔄 演示流程:
   1. 测试Forward Rule关联操作
   2. 测试System Rule解除关联操作
   3. 测试System Rule重新关联操作
   4. 测试错误处理
""")
    
    # 1. 测试Forward Rule关联
    print_separator("1. Forward Rule关联操作")
    event = {
        "action": "disassociate",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID,
        "region": REGION
    }
    result = lambda_handler(event, {})
    print_result(event, result)
    
    time.sleep(120)  # 等待AWS操作完成
    
    # 2. 测试System Rule解除关联
    print_separator("2. System Rule解除关联操作")
    event = {
        "action": "associate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID,
        "region": REGION
    }
    result = lambda_handler(event, {})
    print_result(event, result)
    
    time.sleep(2)  # 等待AWS操作完成
    return 
    # 3. 测试System Rule重新关联
    print_separator("3. System Rule重新关联操作")
    event = {
        "action": "associate",
        "resolver_rule_id": SYSTEM_RULE_ID,
        "vpc_id": VPC_ID,
        "region": REGION
    }
    result = lambda_handler(event, {})
    print_result(event, result)
    
    # 4. 测试重复关联（应该返回already_associated）
    print_separator("4. 测试重复关联（幂等性）")
    event = {
        "action": "disassociate",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID,
        "region": REGION
    }
    result = lambda_handler(event, {})
    print_result(event, result)
    
    # 5. 测试错误处理
    print_separator("5. 错误处理演示")
    
    # 5.1 无效action
    print("\n5.1 无效action参数:")
    event = {
        "action": "invalid_action",
        "resolver_rule_id": FORWARD_RULE_ID,
        "vpc_id": VPC_ID,
        "region": REGION
    }
    result = lambda_handler(event, {})
    print_result(event, result)
    
    # 5.2 缺少参数
    print("\n5.2 缺少必需参数:")
    event = {
        "action": "associate",
        "resolver_rule_id": FORWARD_RULE_ID
        # 缺少vpc_id
    }
    result = lambda_handler(event, {})
    print_result(event, result)
    
    # 5.3 不存在的资源
    print("\n5.3 不存在的Resolver Rule:")
    event = {
        "action": "associate",
        "resolver_rule_id": "rslvr-rr-nonexistent123",
        "vpc_id": VPC_ID,
        "region": REGION
    }
    result = lambda_handler(event, {})
    print_result(event, result)
    
    # 总结
    print_separator("演示总结")
    print("""
🎉 演示完成！

✅ Lambda函数成功实现了以下功能:
   • Route53 Resolver规则与VPC的关联和解除关联
   • 智能检查现有关联状态（幂等性）
   • 完整的参数验证和错误处理
   • 详细的日志记录和结构化响应
   • 支持多区域操作

📦 部署建议:
   1. 使用提供的deploy_lambda.sh脚本部署到AWS
   2. 配置适当的IAM权限
   3. 设置CloudWatch监控和告警
   4. 可以通过API Gateway暴露为REST API

🔧 使用方式:
   • 直接调用Lambda函数
   • 通过AWS CLI调用
   • 集成到其他AWS服务中
   • 通过API Gateway提供HTTP接口

这个Lambda函数现在可以在生产环境中使用了！
""")

if __name__ == "__main__":
    demo_complete_workflow()
