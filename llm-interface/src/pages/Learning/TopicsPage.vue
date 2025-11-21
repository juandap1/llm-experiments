<template>
  <div class="layout-container">
    <default-navbar />
    <div class="layout-main">
      <default-sidebar></default-sidebar>
      <div class="content-container">
        <q-scroll-area class="content-scroller" dark>
          <div class="max-w-3xl mx-auto py-8">
            <h1 class="font-bold mb-6 text-center">AWS Solutions Architect Topics</h1>

            <div
              v-for="(topic, index) in topics"
              :key="index"
              class="mb-4 border rounded-2xl shadow-sm"
            >
              <button
                class="w-full flex justify-between items-center px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-2xl"
              >
                <span class="text-lg font-semibold text-gray-800">{{ topic.name }}</span>
                <span
                  class="text-gray-500 transition-transform"
                  :class="{ 'rotate-180': openIndex === index }"
                >
                  ▼
                </span>
              </button>

              <ul class="px-6 py-3 space-y-2">
                <li
                  v-for="(sub, i) in topic.subtopics"
                  :key="i"
                  class="flex items-start text-gray-700"
                >
                  <span class="mr-2 text-blue-500">•</span>
                  <span>{{ sub }}</span>
                </li>
              </ul>
            </div>
          </div>
        </q-scroll-area>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
// import HomeNavbar from 'src/components/TabsNavbar.vue'
import DefaultNavbar from 'src/components/DefaultNavbar.vue'
import DefaultSidebar from 'src/components/DefaultSidebar.vue'

const skills = {
  'AWS Solutions Architect Exam': {
    'Domain 1: Design Secure Architectures (30%)': {
      '1.1 Design secure access to AWS resources': [
        'IAM users, groups, and roles',
        'IAM policies and permission boundaries',
        'Temporary credentials (STS, AssumeRole)',
        'Resource-based policies (S3 bucket policies, Lambda permissions)',
        'Identity federation (SAML, Cognito)',
        'AWS Organizations and Service Control Policies (SCPs)',
      ],
      '1.2 Design secure workloads and applications': [
        'Encryption at rest and in transit (KMS, SSL/TLS)',
        'Key management and rotation',
        'Secrets management (Secrets Manager, SSM Parameter Store)',
        'Network security (Security Groups, NACLs, WAF, Shield)',
        'VPC endpoints and private connectivity',
        'Monitoring and logging (CloudTrail, GuardDuty, Config, Security Hub)',
      ],
      '1.3 Determine appropriate data security controls': [
        'S3 encryption options (SSE-S3, SSE-KMS, client-side)',
        'Database and EBS encryption',
        'Data classification and access controls',
        'Backup and compliance strategies (AWS Backup, cross-region replication)',
      ],
    },
    'Domain 2: Design Resilient Architectures (26%)': {
      '2.1 Design highly available and fault-tolerant architectures': [
        'Multi-AZ vs Multi-Region architectures',
        'Load balancing (ALB, NLB, Global Accelerator)',
        'Auto Scaling and elasticity',
        'Failover strategies (Route 53 routing policies, health checks)',
        'Stateless design and session management',
      ],
      '2.2 Design decoupling mechanisms using AWS services': [
        'Asynchronous messaging (SQS, SNS, EventBridge)',
        'Stream processing (Kinesis, MSK)',
        'Service-to-service communication (API Gateway, AppSync)',
        'Loose coupling and microservices patterns',
      ],
      '2.3 Choose appropriate resilient storage': [
        'S3 durability and storage classes',
        'EBS snapshots and multi-AZ replication',
        'RDS Multi-AZ and read replicas',
        'Backup, restore, and disaster recovery strategies',
      ],
    },
    'Domain 3: Design High-Performing Architectures (24%)': {
      '3.1 Identify elastic and scalable compute solutions': [
        'EC2 instance types and families',
        'Auto Scaling groups and lifecycle hooks',
        'Container services (ECS, EKS, Fargate)',
        'Serverless compute (Lambda, Step Functions)',
      ],
      '3.2 Select high-performing and scalable storage solutions': [
        'S3 performance optimization (multipart upload, prefixes)',
        'EBS throughput vs IOPS optimization',
        'EFS vs FSx vs instance storage',
        'Caching (CloudFront, ElastiCache)',
      ],
      '3.3 Select high-performing networking solutions': [
        'VPC design and subnetting',
        'Direct Connect, VPN, Transit Gateway',
        'Hybrid connectivity and edge networking',
        'Route 53 routing and latency optimization',
      ],
      '3.4 Select high-performing database solutions': [
        'RDS engine selection and tuning',
        'Aurora scaling and read replicas',
        'DynamoDB partitioning, DAX, on-demand vs provisioned',
        'Caching strategies for performance',
      ],
    },
    'Domain 4: Design Cost-Optimized Architectures (20%)': {
      '4.1 Design cost-optimized storage': [
        'S3 lifecycle policies, Intelligent-Tiering',
        'Glacier and archival strategies',
        'EBS volume types (gp3, io2, sc1, etc.)',
      ],
      '4.2 Design cost-optimized compute': [
        'EC2 pricing models (On-Demand, Reserved, Spot, Savings Plans)',
        'Right-sizing and instance scheduling',
        'Container and serverless cost efficiency',
      ],
      '4.3 Design cost-optimized database and network architectures': [
        'RDS instance classes and Aurora Serverless',
        'DynamoDB on-demand vs provisioned capacity',
        'CloudFront and data transfer optimization',
        'PrivateLink vs NAT Gateway cost considerations',
      ],
      '4.4 Identify cost optimization tools': [
        'AWS Cost Explorer, Budgets, Trusted Advisor',
        'Compute Optimizer, Pricing Calculator',
        'Resource tagging and cost allocation tracking',
      ],
    },
  },
}

const topics = [
  {
    name: 'Compute',
    subtopics: [
      'EC2',
      'Auto Scaling',
      'Elastic Load Balancing (ALB, NLB)',
      'Elastic Beanstalk',
      'Lambda',
      'ECS',
      'EKS',
      'Fargate',
      'AWS Batch',
      'AWS App Runner',
    ],
  },
  {
    name: 'Storage',
    subtopics: [
      'S3',
      'S3 Glacier',
      'EBS',
      'EFS',
      'FSx for Windows File Server',
      'FSx for Lustre',
      'AWS Backup',
      'Storage Gateway',
    ],
  },
  {
    name: 'Databases',
    subtopics: [
      'RDS',
      'Aurora',
      'DynamoDB',
      'ElastiCache (Redis, Memcached)',
      'Redshift',
      'Neptune',
      'DocumentDB',
    ],
  },
  {
    name: 'Networking & Content Delivery',
    subtopics: [
      'VPC',
      'Subnets',
      'Route 53',
      'CloudFront',
      'API Gateway',
      'Direct Connect',
      'VPN',
      'Transit Gateway',
      'PrivateLink',
      'Global Accelerator',
      'NAT Gateway',
      'VPC Endpoints',
    ],
  },
  {
    name: 'Security, Identity, and Compliance',
    subtopics: [
      'IAM',
      'Organizations',
      'Cognito',
      'STS (Security Token Service)',
      'KMS',
      'Secrets Manager',
      'AWS Shield',
      'WAF (Web Application Firewall)',
      'AWS Config',
      'CloudTrail',
      'Security Hub',
      'GuardDuty',
      'Inspector',
      'Macie',
    ],
  },
  {
    name: 'Application Integration',
    subtopics: [
      'SQS',
      'SNS',
      'EventBridge (CloudWatch Events)',
      'Step Functions',
      'AppSync',
      'MQ (Amazon MQ)',
    ],
  },
  {
    name: 'Monitoring & Management',
    subtopics: [
      'CloudWatch',
      'CloudFormation',
      'CloudTrail',
      'Trusted Advisor',
      'AWS Budgets',
      'Cost Explorer',
      'Compute Optimizer',
      'Systems Manager (SSM)',
      'Service Catalog',
      'Control Tower',
      'AWS Organizations',
    ],
  },
  {
    name: 'Migration & Transfer',
    subtopics: [
      'AWS Migration Hub',
      'Database Migration Service (DMS)',
      'Server Migration Service (SMS)',
      'DataSync',
      'Snowball / Snowcone / Snowmobile',
      'Transfer Family (SFTP, FTPS, FTP)',
    ],
  },
  {
    name: 'Analytics',
    subtopics: ['Athena', 'Glue', 'Kinesis (Data Streams, Firehose, Analytics)', 'QuickSight'],
  },
  {
    name: 'Developer Tools',
    subtopics: ['CodeCommit', 'CodeBuild', 'CodeDeploy', 'CodePipeline', 'Cloud9'],
  },
  {
    name: 'Edge & Hybrid',
    subtopics: ['Outposts', 'Local Zones', 'Wavelength'],
  },
  {
    name: 'Cost & Governance',
    subtopics: [
      'Billing and Cost Management',
      'Pricing Calculator',
      'Savings Plans',
      'Reserved Instances',
    ],
  },
]

export default defineComponent({
  name: 'TopicsPage',
  components: { DefaultNavbar, DefaultSidebar },
  data() {
    return {
      skills,
      topics,
    }
  },
  methods: {},
})
</script>
<style scoped>
.content-scroller {
  height: 100%;
}
</style>
