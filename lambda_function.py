import json
import boto3
import logging
from botocore.exceptions import ClientError

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda函数处理Route53 Resolver规则与VPC的绑定/解绑操作
    
    期望的event格式:
    {
        "action": "associate" | "disassociate",
        "resolver_rule_id": "rslvr-rr-xxxxxxxxx",
        "vpc_id": "vpc-xxxxxxxxx"
    }
    """
    
    try:
        # 解析输入参数
        action = event.get('action')
        resolver_rule_id = event.get('resolver_rule_id')
        vpc_id = event.get('vpc_id')
        
        # 参数验证
        if not all([action, resolver_rule_id, vpc_id]):
            raise ValueError("缺少必需参数: action, resolver_rule_id, vpc_id")
        
        if action not in ['associate', 'disassociate']:
            raise ValueError("action必须是 'associate' 或 'disassociate'")
        
        # 创建Route53 Resolver客户端
        region = event.get('region', 'us-west-2')  # 默认使用us-west-2
        resolver_client = boto3.client('route53resolver', region_name=region)
        
        logger.info(f"开始执行操作: {action}, Resolver Rule ID: {resolver_rule_id}, VPC ID: {vpc_id}")
        
        if action == 'associate':
            result = associate_resolver_rule(resolver_client, resolver_rule_id, vpc_id)
        else:
            result = disassociate_resolver_rule(resolver_client, resolver_rule_id, vpc_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'操作 {action} 成功完成',
                'result': result
            }, ensure_ascii=False)
        }
        
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': '参数错误',
                'message': str(e)
            }, ensure_ascii=False)
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS API错误: {error_code} - {error_message}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'AWS API错误',
                'code': error_code,
                'message': error_message
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': '内部服务器错误',
                'message': str(e)
            }, ensure_ascii=False)
        }


def associate_resolver_rule(resolver_client, resolver_rule_id, vpc_id):
    """
    将Resolver规则与VPC关联
    """
    try:
        # 检查是否已经关联
        existing_associations = resolver_client.list_resolver_rule_associations(
            Filters=[
                {
                    'Name': 'ResolverRuleId',
                    'Values': [resolver_rule_id]
                },
                {
                    'Name': 'VPCId',
                    'Values': [vpc_id]
                }
            ]
        )
        
        if existing_associations['ResolverRuleAssociations']:
            logger.info(f"Resolver规则 {resolver_rule_id} 已经与VPC {vpc_id} 关联")
            return {
                'association_id': existing_associations['ResolverRuleAssociations'][0]['Id'],
                'status': 'already_associated'
            }
        
        # 创建新的关联
        response = resolver_client.associate_resolver_rule(
            ResolverRuleId=resolver_rule_id,
            VPCId=vpc_id
        )
        
        association_id = response['ResolverRuleAssociation']['Id']
        logger.info(f"成功创建关联: {association_id}")
        
        return {
            'association_id': association_id,
            'status': 'associated'
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceExistsException':
            logger.info(f"关联已存在: Resolver规则 {resolver_rule_id} 与VPC {vpc_id}")
            return {
                'status': 'already_associated'
            }
        elif error_code == 'ResourceNotFoundException':
            # 检查是否是因为规则不存在或VPC不存在
            logger.error(f"资源未找到: Resolver规则 {resolver_rule_id} 或 VPC {vpc_id} 不存在")
            raise
        elif error_code == 'InvalidRequestException':
            # 可能是System规则不能手动关联
            logger.error(f"无效请求: 可能是System规则不能手动关联到VPC")
            raise
        elif error_code == 'InternalServiceErrorException':
            # AWS内部服务错误，可能是临时的
            logger.error(f"AWS内部服务错误: {e.response['Error']['Message']}")
            raise
        elif error_code == 'LimitExceededException':
            # 超出关联限制
            logger.error(f"超出关联限制: {e.response['Error']['Message']}")
            raise
        else:
            raise


def disassociate_resolver_rule(resolver_client, resolver_rule_id, vpc_id):
    """
    解除Resolver规则与VPC的关联
    """
    try:
        # 查找现有关联
        associations = resolver_client.list_resolver_rule_associations(
            Filters=[
                {
                    'Name': 'ResolverRuleId',
                    'Values': [resolver_rule_id]
                },
                {
                    'Name': 'VPCId',
                    'Values': [vpc_id]
                }
            ]
        )
        
        if not associations['ResolverRuleAssociations']:
            logger.info(f"未找到Resolver规则 {resolver_rule_id} 与VPC {vpc_id} 的关联")
            return {
                'status': 'not_associated'
            }
        
        # 解除关联
        association_id = associations['ResolverRuleAssociations'][0]['Id']
        
        response = resolver_client.disassociate_resolver_rule(
            VPCId=vpc_id,
            ResolverRuleId=resolver_rule_id
        )
        
        logger.info(f"成功解除关联: {association_id}")
        
        return {
            'association_id': association_id,
            'status': 'disassociated'
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info(f"关联不存在: Resolver规则 {resolver_rule_id} 与VPC {vpc_id}")
            return {
                'status': 'not_associated'
            }
        raise


def get_resolver_rule_info(resolver_client, resolver_rule_id):
    """
    获取Resolver规则信息（辅助函数）
    """
    try:
        response = resolver_client.get_resolver_rule(
            ResolverRuleId=resolver_rule_id
        )
        return response['ResolverRule']
    except ClientError:
        return None


def list_vpc_associations(resolver_client, resolver_rule_id):
    """
    列出指定Resolver规则的所有VPC关联（辅助函数）
    """
    try:
        response = resolver_client.list_resolver_rule_associations(
            Filters=[
                {
                    'Name': 'ResolverRuleId',
                    'Values': [resolver_rule_id]
                }
            ]
        )
        return response['ResolverRuleAssociations']
    except ClientError:
        return []
