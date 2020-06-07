import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')
volumes = ec2.volumes.all()

def filter_instances(project):
    instances = []
    
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    
    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """shotty manages snapshots"""
 
@cli.group('volumes') 
def volumes():
    """ Commands for Volumes"""
    
@volumes.command('list')  
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")  
def list_volumes(project):
    "List EC2 volumes"
    
    instances = filter_instances(project) 
       
    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))
            
    return

@volumes.command('snapshots')  
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")  
@click.option('--all','list_all', default=False, is_flag=True,
        help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project,list_all):
    "List EC2 snapshots"
    
    instances = filter_instances(project) 
       
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))
                
                if s.state == "completed" and not list_all: break
            
    return

@volumes.command('takesnap')  
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")  
def take_snapshots(project):
    "Create new Snapshots"
    
    instances = filter_instances(project)
        
    for i in instances:
        
        print(f'Stopping {i.id}....')
        
        i.stop()
        i.wait_until_stopped()
        
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print(f'  Skipping {v.id}, snapshot already in progress..,')
                continue
            
            print(f'   Creating Snapshot for {v.id}......')
            v.create_snapshot(Description="Created by Snapshotalyer 3000")
            
        print(f'Starting {i.id}...')
        
        i.start()
        i.wait_until_running()
        
    print("Job's done!! ")
    
    return
        
@volumes.command('delete')  
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")  
def delete_snapshots(project):
    "Deletes all the existing Snapshots"
    
    instances = filter_instances(project)    
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                s.delete()
      
@cli.group('instances')
def instances():
    """Commands for instances"""
    
@instances.command('list')  
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")  
def list_instances(project):
    "List EC2 instances"
    
    instances = filter_instances(project)    
    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print (', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
            )))
    
    return

@instances.command('stop')  
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")  

def stop_instances(project):
    "Stop EC2 instances"
    
    instances = filter_instances(project)
    
    for i in instances:
        print(f'Stopping {i.id}....')
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(f'Could not stop {i.id}... ' + str(e))
            continue
                 
    return

@instances.command('start')  
@click.option('--project', default=None,
        help="Only instances for project (tag Project:<name>)")  

def start_instances(project):
    "Start EC2 instances"
    
    instances = filter_instances(project)
    
    for i in instances:
        print(f'Starting {i.id}....')
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(f'Could not start {i.id}... ' + str(e))
            continue
            
    return

if __name__ == '__main__':
    cli()
    
    