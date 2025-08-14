两个变更思路说明：
1. 日常保持两个resolver rule ，一个forward, 一个system, 需要切换的时候，把system 绑定vpc，然后把forward 的vpc绑定移除；【生效需要等一段时间，具体时间需要再调整代码实测一下】
    a. 这里要关注，如果两个rule的域名是一样的，必须等一个解绑成功之后，另一个才可绑定，否则会报错 internal error
    b. resolver rule 绑定和解绑VPC的过程大概需要1秒钟；
2. 日常一个resolver rule ，forward， 如果业务判定需要切换，用代码修改forward的目标ip到其他dns；【这里可以考虑改成一些公开dns 如 8.8.8.8作为infoblox不可用的时候的兜底，可能损失防护功能，但是保障了业务可用性】


在us-west-2 有一个route 53 resolver rule, id 是 rslvr-rr-439063a14ec246eb8
希望实现两个python函数，实现将这个rule 从 forward 改成system 以及从system 修改回forward

实现一个python函数要在lambda使用；功能层面，支持输入route53 的resolver rule 的id  和vpc id，触发绑定和解绑动作。

forward rule: rslvr-rr-4434e3b2252648c2a

System rule: rslvr-rr-997b5cb773fa4a39b

vpc id: vpc-0c443442382a4d7ca
测试region 在美西2

 写一个aws  cli 实现 route53 resolver rule 绑定vpc SYSTEM_RULE_ID = "rslvr-rr-997b5cb773fa4a39b"
VPC_ID = "vpc-0c443442382a4d7ca"
REGION = "us-west-2"



实现一个python函数要在lambda使用；功能层面，支持输入route53 的resolver rule 的id 和ip列表 将这个resolver rule的target ip 变更成ip列表

ruleid 是 rslvr-rr-4434e3b2252648c2a ,us-west-2 , 实现一个demo.py， 调用相关方法，将targetip修改成 ['8.8.8.8', '8.8.4.4']