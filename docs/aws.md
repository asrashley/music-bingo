# Amazon AWS installation

As the resource of the music bingo service are relatively low, it is
possible to run the service in a nano AWS EC2 instance. If high
availability is not required, this allows the service to be hosted for
less than £4 (Europe Ireland) / $4 (US East) per month.

## Single EC2 instance without fault tollerance

This repository contains CloudFormation scripts to deploy a single EC2
instance with code deploy to automatically install the
musicbingo-prod.tar.gz file.

Deploy the [codedeploy-s3.yaml](../musicbingo/server/aws/codedeploy-s3.yaml)
CloudFormation script. This script creates an S3 bucket that will be used to
hold the musicbingo-prod.tar.gz file.

Upload the musicbingo-prod.tar.gz file to this S3 bucket.

Deploy the [cloudformation.yaml](../musicbingo/server/aws/cloudformation.yaml)
CloudFormation script to build the rest of the stack. It will create:

* an EC2 instance with:
** two EBS volumes (one for root, one for the database)
** a cron job that snapshots the EBS volumes daily
** mariadb as the database
** nginx as an HTTP server and reverse proxy
** uwsgi to run the Python server
* a CodeDeploy pipeline to automatically install musicbingo-prod.tar.gz
* a Route53 domain that provides a DNS entry for the EC2 instance

Uploading a new version of musicbingo-prod.tar.gz file to the
CodeDeploy S3 bucket will automatically re-deploy this code into the
EC2 instance.

To enable HTTPS, log into the EC2 instance and run certbot:

    sudo certbot --nginx

## High-availability deployment

A high availability system can be created using Aurora RDS,
multiple EC2 instances and an elastic load balancer.

A serverless Aurora mysql resource will probably be cheaper than an
conventional instance based version.

The [codedeploy-s3.yaml](../musicbingo/server/aws/codedeploy-s3.yaml)
CloudFormation script could be used to create an S3 bucket that is used to
hold the musicbingo-prod.tar.gz file and automatically deploy it to every
EC2 instance. Remember to upload the musicbingo-prod.tar.gz file to this
S3 bucket before deploying the EC2 instances, otherwise the CodeDeploy
resources will fail, causing the CloudFormation script to be rolled
back.

Most of the [cloudformation.yaml](../musicbingo/server/aws/cloudformation.yaml)
CloudFormation script is relevant to an HA deployment. The
/home/ec2-user/bingo.ini file created as part of the EC2 instance would
need to be modified to set the RDS address and port from the output of
the AWS::RDS::DBCluster resource. The Configure steps to install and
configure mariadb need to be removed. The EBS volume that is used to
hold the database can also be removed, as that will not be required.

An ELB resource is needed to distribute requests to each of the EC2
instances. This ELB resource also makes a handy place to perform HTTPS
termination, to avoid having to include TLS certificates in each EC2
instance.

CloudFront can be utilised to cache the static assets of the
application. Requests to any URL in the within the /api path must not
be cached. The server will include "no not cache" headers in its API
responses, which should stop CloudFront from trying to cache them.
