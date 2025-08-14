#!/usr/bin/env python3
"""
检查Resolver Rule状态脚本
"""

import boto3
import time
import json

RESOLVER_RULE_ID = "rslvr-rr-4434e3b2252648c2a"
REGION = "us-west-2"

def check_status():
    """检查Resolver Rule状态"""
    client = boto3.client('route53resolver', region_name=REGION)
    
    try:
        response = client.get_resolver_rule(ResolverRuleId=RESOLVER_RULE_ID)
        rule = response['ResolverRule']
        
        print(f"🔍 Resolver Rule状态检查 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 Rule ID: {rule['Id']}")
        print(f"📊 状态: {rule['Status']}")
        print(f"🎯 当前目标IP: {[target['Ip'] + ':' + str(target['Port']) for target in rule.get('TargetIps', [])]}")
        print(f"🕒 修改时间: {rule.get('ModificationTime', 'N/A')}")
        print(f"🏷️  域名: {rule.get('DomainName', 'N/A')}")
        print("-" * 50)
        
        return rule['Status']
        
    except Exception as e:
        print(f"❌ 检查状态失败: {str(e)}")
        return None

def monitor_until_complete(max_wait_minutes=10):
    """监控直到更新完成"""
    print("🚀 开始监控Resolver Rule更新状态...")
    print(f"⏰ 最大等待时间: {max_wait_minutes} 分钟")
    print("=" * 50)
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while True:
        status = check_status()
        
        if status is None:
            print("❌ 无法获取状态，停止监控")
            break
            
        if status == "COMPLETE":
            print("✅ 更新已完成!")
            break
        elif status == "FAILED":
            print("❌ 更新失败!")
            break
        elif status in ["UPDATING", "PENDING"]:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                print(f"⏰ 已等待 {max_wait_minutes} 分钟，停止监控")
                print("💡 更新可能仍在进行中，请稍后手动检查")
                break
            
            print(f"⏳ 仍在更新中，等待30秒后再次检查...")
            time.sleep(30)
        else:
            print(f"❓ 未知状态: {status}")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_until_complete()
    else:
        check_status()
