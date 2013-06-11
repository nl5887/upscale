===========
Upscale
=========== 
Upscale is an open 'platform as a service' provider. It will deploy new hosts, start application containers and rebalance containers. Containers can be runned always on multiple different hosts, ensuring availability.

Our goal is to create an application platform where you don't have to think about hosts, scaling and deployment. The application platform will scale up and down new containers and new hosts when necessary, without downtime or any notice.
 
Upscale consist of namespaces, applications, runtime and containers. A company can have its own namespace, from within this namespace multiple applications can be created. A deployment of an application is done using containers. A container is an instance of a runtime, for running php, python or ruby. Multiple containers can be active.

Upscale runs currently on Ubuntu 13.04 and Amazon EC2.

## What do we have already
- we can create namespaces with applications
- repositories are created 
- app.yaml is being verified by each push
- load is balanced through the hosts and containers
- containers are started by the host

## How does it work
Each application is started within an LXC container, added to the loadbalancer and made available through the public dns.

## Contribute
Yes! We've got a lot of work to do, so all contributions are highly appreciated.

## Runtimes
Runtimes are located in the data/runtimes directory. These are yaml configurations, and can be easily added.
- PHP 5.3

## Technologies
- Amazon EC2 (currently we're using the ec2 cloud for running hosts)
- Ubuntu 13.04 (this is our current platform of choice)
- Python 2.7 (as programming language)
- MariaDB (as database)
- GlusterFS (as shared data storage)
- Git (for repository)
- Haproxy (for loadbalancing)
- Celery (Python) (as service bus)
- Jinja2 (Python) (as templating language)
- Sphinx (for documentation)
- RabbitMQ (as service bus)

## How to start?
- create an amazon vpc - 
- configure config.yaml to your needs
- run an instance
- run the deploy script for the instance
- configure elb to include the instance
- point a wildcard domain \*.upscale.yourdomain.org to the elb instance
- create a namespace
- create a application
- clone the repository, add files, update app.yaml, commit and push
- run the application (application.namespace.upscale.yourdomain.org)

## Components
- The upscale master is located at one of the servers, receives requests and routes them to the workers.
- An upscale worker needs to be deployed on each host, this worker is responsible for returning status information, running new containers, shutting down containers etc.
- The upscale git server creates a git repository for each application. New applications will be deployed running the HEAD of repository.
- An upscale manage console. This is being used for creating new namespaces, applications.

## Data
For each namespace a corresponding folder in the data folder is being created. The namespace folder will have a home folder, which will be used for authentication to the git repository, and the git repositories itself. Each application will create a data folder below the namespace folder. The application data folder is shared between all containers.

```
namespace/home/git/(application).git
namespace/application/
```

## Todo
- Support for other distributions
- Support for private clouds and other clouds
- Web frontend for signup, create namespaces and applications
- More runtimes
- Convert current api to remote http api
- Remote management (current is just local)
- Authorization and authentication
- Autoscale
- Weighted hosts 
- Adoption of Juju / Salt
- User management with NCSD?

### Prepare virtual env
```
cd /opt/upscale
virtualenv env
. env/activate/bin
pip install -r requirements
```

### Run worker 
. env/activate/bin
python bin/worker.py

### Deployment to new host
```
python deploy.py --host 10.0.0.231 -u username -i identity
```

## Commands:
### Create new namespace
```
python bin/manage.py namespace create  --namespace test 
```
### Add your ssh key to repository
```
python bin/manage.py keys add --namespace test --name test --public "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAIEAxBBy9uYqcxPIap9of7nbySHjJLurqTGART3k06NgSHpVvjotNMdMrz+NArijlTLunQD/5sxCxlIXHg2uXH2ECni0bfK/fC6TWWAmUuHcIdELfUTxark7CmalWG8BV39w6UYqGH0/nQfHgq4lRxSitrpWW90UCk2oJ0PvxNbrhnk="
```

### Create new application within namespace
```
python bin/manage.py app create  --namespace test --application website --runtime apache-php5.3
```

### Clone to local repository
```
git clone test@git.url:~/git/website.git . 
git commit
git push origin master
```

### Run instance on specified host 
```
python bin/manage.py hosts list
python bin/manage.py app run --host i-c811af85 --application website --namespace test 
```
### List hosts
```
python ./bin/manage.py hosts list
```
### Run the application
```
python ./bin/manage.py app run --namespace test --application test
```
