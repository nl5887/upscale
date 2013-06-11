from upscale.config import config

def get_hosts():
        import boto.ec2

        access=config['ec2']['access-key']
        key= config['ec2']['secret-key']
        region= config['ec2']['region']
        vpc_id= config['ec2']['vpc-id']

        ec2_conn = boto.ec2.connect_to_region(region, aws_access_key_id=key, aws_secret_access_key=access)

        instances = []
        for reservation in ec2_conn.get_all_instances(filters={'vpc-id':vpc_id}):
                for instance in reservation.instances:
                        instances.append(instance)

        return (instances)

