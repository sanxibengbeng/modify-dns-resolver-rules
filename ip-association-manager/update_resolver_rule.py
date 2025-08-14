import boto3
import json
import logging
from typing import List, Dict, Any
from botocore.exceptions import ClientError

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda函数入口点
    
    Args:
        event: Lambda事件，包含resolver_rule_id、target_ips和region
        context: Lambda上下文
    
    Returns:
        响应字典，包含状态码和消息
    """
    try:
        # 解析输入参数
        resolver_rule_id = event.get('resolver_rule_id')
        target_ips = event.get('target_ips', [])
        region = event.get('region')
        
        if not resolver_rule_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'resolver_rule_id is required'
                })
            }
        
        if not target_ips or not isinstance(target_ips, list):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'target_ips must be a non-empty list'
                })
            }
        
        # 调用更新函数
        result = update_resolver_rule_target_ips(resolver_rule_id, target_ips, region)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Resolver rule updated successfully',
                'resolver_rule_id': resolver_rule_id,
                'region': region or 'default',
                'updated_target_ips': target_ips,
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error updating resolver rule: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

def update_resolver_rule_target_ips(resolver_rule_id: str, target_ips: List[str], region: str = None) -> Dict[str, Any]:
    """
    更新Route53 Resolver Rule的目标IP地址
    
    Args:
        resolver_rule_id: Resolver Rule的ID
        target_ips: 新的目标IP地址列表
        region: AWS区域名称，如果未指定则使用默认区域
    
    Returns:
        更新操作的结果
    
    Raises:
        ClientError: AWS API调用失败
        ValueError: 输入参数无效
    """
    # 验证IP地址格式
    for ip in target_ips:
        if not _is_valid_ip(ip):
            raise ValueError(f"Invalid IP address format: {ip}")
    
    # 验证region格式（如果提供）
    if region and not _is_valid_region(region):
        raise ValueError(f"Invalid AWS region format: {region}")
    
    # 创建Route53 Resolver客户端，指定区域
    client_kwargs = {}
    if region:
        client_kwargs['region_name'] = region
        logger.info(f"Using specified region: {region}")
    else:
        logger.info("Using default region from AWS configuration")
    
    route53resolver = boto3.client('route53resolver', **client_kwargs)
    
    try:
        # 首先获取当前的resolver rule信息
        logger.info(f"Getting current resolver rule info for ID: {resolver_rule_id}")
        response = route53resolver.get_resolver_rule(ResolverRuleId=resolver_rule_id)
        current_rule = response['ResolverRule']
        
        logger.info(f"Current rule status: {current_rule['Status']}")
        logger.info(f"Current target IPs: {[target['Ip'] for target in current_rule.get('TargetIps', [])]}")
        
        # 构建新的目标IP配置
        new_target_ips = []
        for ip in target_ips:
            new_target_ips.append({
                'Ip': ip,
                'Port': 53  # DNS默认端口
            })
        
        # 更新resolver rule
        logger.info(f"Updating resolver rule {resolver_rule_id} with new target IPs: {target_ips}")
        update_response = route53resolver.update_resolver_rule(
            ResolverRuleId=resolver_rule_id,
            Config={
                'TargetIps': new_target_ips
            }
        )
        
        logger.info("Resolver rule update initiated successfully")
        
        # 处理ModificationTime，可能是datetime对象或字符串
        modification_time = update_response['ResolverRule']['ModificationTime']
        if hasattr(modification_time, 'isoformat'):
            modification_time_str = modification_time.isoformat()
        else:
            modification_time_str = str(modification_time)
        
        return {
            'resolver_rule_id': resolver_rule_id,
            'region': region or boto3.Session().region_name or 'us-east-1',
            'status': update_response['ResolverRule']['Status'],
            'modification_time': modification_time_str,
            'new_target_ips': target_ips
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS API Error - Code: {error_code}, Message: {error_message}")
        
        if error_code == 'ResourceNotFoundException':
            raise ValueError(f"Resolver rule not found: {resolver_rule_id}")
        elif error_code == 'InvalidParameterException':
            raise ValueError(f"Invalid parameter: {error_message}")
        elif error_code == 'AccessDeniedException':
            raise ValueError(f"Access denied: {error_message}")
        else:
            raise
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

def _is_valid_ip(ip: str) -> bool:
    """
    验证IP地址格式是否有效
    
    Args:
        ip: IP地址字符串
    
    Returns:
        True如果IP地址有效，否则False
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def _is_valid_region(region: str) -> bool:
    """
    验证AWS区域格式是否有效
    
    Args:
        region: AWS区域字符串
    
    Returns:
        True如果区域格式有效，否则False
    """
    import re
    # AWS区域格式：us-east-1, eu-west-1, ap-southeast-1等
    region_pattern = r'^[a-z]{2,3}-[a-z]+-\d+$'
    return bool(re.match(region_pattern, region))

# 用于本地测试的示例函数
def test_locally():
    """
    本地测试函数
    """
    # 示例事件
    test_event = {
        'resolver_rule_id': 'rslvr-rr-xxxxxxxxx',
        'target_ips': ['8.8.8.8', '8.8.4.4'],
        'region': 'us-east-1'  # 可选参数
    }
    
    # 模拟Lambda上下文
    class MockContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.aws_request_id = 'test-request-id'
    
    context = MockContext()
    
    # 调用Lambda处理函数
    result = lambda_handler(test_event, context)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    test_locally()
