# Deployment

This app is hosted live on an Amazon Web Services EC2 Instance serving an API at ec2-54-241-135-227.us-west-1.compute.amazonaws.com:8080. The Frontend client is hosted in an AWS S3 bucket, accessible from discoverlive.speal.ca.

## How to deploy this app on a brand new server:

Start up an EC2 Instance
 * OS: Amazon Linux AMI 2018.03.0 (HVM), SSD Volume Type (Because it includes python)
 * t2.micro (free tier eligible)
 * Use an existing SSH key (Saved in ~/.ssh or create a new one and download it there.)
 * Create a security group Discover Live Security Group for SSH and HTTP. Create a custom TCP rule to allow all inbound connections on port 8080. I couldn't figure out how to get daphne to serve on port 80...
 * Enable a public DNS within the VPC settings
 * Create an internet gateway for the VPC
 * Edit the route table associated with the subnet and add a route that routes all traffic (0.0.0.0/0) to the internet gateway
 * Confirm that you can SSH into the box
 * Configure the app to make sure it knows about the deployed address. In the frontend configure the API endpoint (.env.production file) and in the django settings add the public DNS to ALLOWED_HOSTS


Copy the app onto the server and install what's needed:
 * `scp -r musicThisWeek ec2-user@ec2-54-241-135-227.us-west-1.compute.amazonaws.com:/home/ec2-user` (Don't forget to specify the target directory at the end)
 * This takes about 6 min because it copies way too much. Someday I'll get a git-clone working better and quicker.
 * SSH in: `ssh ec2-user@ec2-54-241-135-227.us-west-1.compute.amazonaws.com`
 * `sudo yum-config-manager --enable epel` (Needed for redis I think)
 * `sudo yum install python36 python36-devel gcc redis`
 * `gem install teamocil`
 * Setup (install?) virtual env: `python36 -m venv discoverlive`
 * source ~/.virtualenv/discoverlive/bin/activate
 * confirm you're running python version 3.6 within the virtualenv: `python --version`
 * Install deps: `pip install -r requirements.txt`

Run the app:
  * There are several processes that need to run in order to run the app. They are listed in tmuxLayout.yml. You can run one script to start them all within tmux:
  * `./start.sh` (you may need to `chmod +x start.sh` once on a new box)
  * Within tmux Ctrl + b, 1 (replace with other low numbers) to switch tmux sessions and find the one with the app running
  * You should see one window with daphne, one with redis, and one with the django workers. Most logs are in the last terminal
  * ctrl +b, d detaches, and then you can exit the terminal. tmux attach attaches the session back again.


Testing
  * confirm that you can hit an HTTP endpoint on the server with this URL in the browser: http://ec2-54-183-72-229.us-west-1.compute.amazonaws.com:8080/test (you may need to replace the public DNS from the AWS EC2 instances list)
  * Use the frontend and confirm that the Search button works. You should see a POST request to the create endpoint and then the page changes and then you should see data streaming in as the server logs go wild.

## How to deploy an update
  * I'd like to speed this up eventually using git, but for now scp the whole app to the server (command is in the above section)
  * It could be a good idea to delete the existing ~/musicThisWeek folder first but probably not necessary.

## Improvements I'd like TODO

  * Audit the security structure with VPC etc
  * Setup a static IP or constant DNS so the app doesn't need to change with deployment IP address.
  * Setup some server in front of Daphne so that we can use port 80
  * Setup some sort of virtualhost shortcut on my machine to make sshing into the ec2 box more obvious
