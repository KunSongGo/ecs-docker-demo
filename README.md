# ECS Docker demo 

## Terminologies 

* Docker image: 
* Task Definition: 
* Service: 
* ECR
* ECS 

## Build docker image

### 1. Install docker and docker-compose 

```
[ec2-user@ip-10-0-0-204 ~]$ sudo yum install docker -y 
[ec2-user@ip-10-0-0-204 ~]$ sudo yum install docker -y sudo curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
[ec2-user@ip-10-0-0-204 ~]$ sudo chmod +x /usr/local/bin/docker-compose
[ec2-user@ip-10-0-0-204 ~]$ mkdir demo-docker
[ec2-user@ip-10-0-0-204 ~]$ cd demo-docker/
[ec2-user@ip-10-0-0-204 demo-docker]$
```

### 2. Create a file called `app.py` in your project directory and paste this in:

```
import time

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World! Welcome to demo-app'
```

### 3. Create another file called `requirements.txt` in your project directory and paste this in:

```
[ec2-user@ip-10-0-0-204 demo-docker]$ cat requirements.txt
flask
```

### 4. Create a Dockerfile

In this step, you write a Dockerfile that builds a Docker image. The image contains all the dependencies the Python application requires, including Python itself.
In your project directory, create a file named `Dockerfile` and paste the following:

```
FROM python:3.7-alpine
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_PORT 80
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]
EXPOSE 80
```

### 5. Build docker image

```
[ec2-user@ip-10-0-0-204 demo-docker]$ docker build -t ecs-demo-app .
```

### 6. Check docker image

```
[ec2-user@ip-10-0-0-204 demo-docker]$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
ecs-demo-app        latest              54f8232440d3        14 minutes ago      213MB
python              3.7-alpine          39fb80313465        2 days ago          98.7MB
```

### 7. Test the docker image 

```
[ec2-user@ip-10-0-0-204 demo-docker]$ docker run -p 80:5000 54f8232440d3
 * Serving Flask app "app.py"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
172.17.0.1 - - [29/Aug/2019 13:01:22] "GET / HTTP/1.1" 200 -

[ec2-user@ip-10-0-0-204 ~]$ curl localhost:80
Hello World! Welcome to demo-app[ec2-user@ip-10-0-0-204 ~]$
```



## Push image to ECR 

### Create ECR repository in AWS 

```
[ec2-user@ip-10-0-0-204 ~]$ aws ecr create-repository --repository-name ecs-demo-repository --region eu-west-1
{
    "repository": {
        "registryId": "xxxxxx",
        "repositoryName": "ecs-demo-repository",
        "repositoryArn": "arn:aws:ecr:eu-west-1:xxxxxxxx:repository/ecs-demo-repository",
        "createdAt": 1567083784.0,
        "repositoryUri": "xxxxxxxx.dkr.ecr.eu-west-1.amazonaws.com/ecs-demo-repository"
    }
}
```

### tag image to repo

```
[ec2-user@ip-10-0-0-204 ~]$ docker tag ecs-demo-app xxxxxxxx.dkr.ecr.eu-west-1.amazonaws.com/ecs-demo-repository
```

### get docker login credentials 

```
[ec2-user@ip-10-0-0-204 ~]$ aws ecr get-login --no-include-email --region eu-west-1
```

### push image to ECR 

```
[ec2-user@ip-10-0-0-204 ~]$ docker push xxxxxxxx.dkr.ecr.eu-west-1.amazonaws.com/ecs-demo-repository
```

### Check image in ECR

Go to your AWS Console and go to the ECR service page, you should be able to see the “ecs-demo-app” in the list of repositories, click on it and you will see the image details as below:
[Image: image]Copie the image URI and keep it,  we will use it to create the task definition. 


## Create Task Definition in ECS 

1. Go the ECS page in your AWS console, click ‘Task definitions“ in the left side of the page.
2. Click ”Create new Task Definition“, then choose ”Fargate“ then hit ”Next“, you will see a new page popped out. 
3. Enter a name in “Task Definition Name” field, for this example we will use “ecs-fargate-demo”.
4. Choose ‘None“ in Task Role, leave the rest by default then go to ”Task size“ section.
5. Select “1 GB” in “Task memory” and “0.5 vCPU” in “Task CPU” then hit “Add container” in this section.
6.  Enter a name in “Container name” field, for this example we will use “ecs-demo-container”, paste the image URI you have copied previous, then scroll down to “Port mappings” and enter “80”  leave the protocol to “tcp” as below. 

7. Scroll down and hit “Add”. 
8. Leave the rest sections with default setting and click “Create” 

Now we have created a Task Definition and we will use it to create a Service later. 


## Create Fargate cluster in ECS

1. Go to “Cluster” in ECS service page in your AWS console
2. Click “Create Cluster”, the leave the default selection of  “Networking only” panel and click '“Next”,
3. Enter a name in “Cluster name” field 
4. Check the “Create VPC” and leave all as default and click “Create” 
5. [Image: Screenshot 2019-09-03 at 17.26.37.png]
6. Note the newly created VPC id and we will use it in “Create Service in ECS” section.

Now we have a Fargate cluster and we are going to launch a Service. 


## Create Service in ECS 

1. Go to the cluster details page and choose the “Services” tab, click “Create” button, you will see a new page popped out. 
2. Choose “FARGATE” as launch type and “esc-fargate-demo” as Task Definition.
3. Leave the rest as default and enter a name in “Service Name” field, for this example we will use “ecs-demo-svc”
4. Enter “3” in “Number of tasks” then hit “Next” 
5. Choose the VPC you have noted in previous step and add the two subnets in this VPC
6. In “Load Balancing” section, choose “Network Load Balancer”, you will see an alert saying “No load balancer is found” 
7. Click the link “EC2 Console” to create a Network Load balancer“ by following this guide (https://docs.aws.amazon.com/elasticloadbalancing/latest/network/network-load-balancer-getting-started.html) and note the Network Load Balancer DNS name.
8. Once you have created a Network Load Balancer, click refresh button and you should be able to see the load balancer you’ve created. Choose that Network Load Balancer and then click the button "Add to load balancer" button 
9. [Image: Screenshot 2019-09-03 at 22.46.37.png]
10. Enter “80” in the second field of “Production listener port” 
11. [Image: Screenshot 2019-09-03 at 22.48.46.png]
12. The click “next”
13. Leave the default option and hit “Next”
14. Review the options you have choose and click “Create”
15. Wait until all the Tasks to be deployed and enter the Network Load Balancer DNS name in your browser, you should see something similar to this: 
16. [Image: Screenshot 2019-09-03 at 23.02.04.png]


