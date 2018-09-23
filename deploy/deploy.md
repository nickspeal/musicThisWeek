# Deployment

This Django app is hosted on AWS Lightsail, serving an API at api.discoverlive.speal.ca. The Frontend client is hosted in an AWS S3 bucket, accessible from discoverlive.speal.ca.

# Initial Setup

* Create a new Amazon Lightsail Instance at https://lightsail.aws.amazon.com/
* Create a new SSH private key in us-west-2a called discover_live_lightsail
* Download it, move it to ~/.ssh/discover_live_lightsail.pm
* chmod 600 ~/.ssh/discover_live_lightsail.pem
* Select the minimal config for an instance running Amazon Linux
* Create a static IP for Discover Live: 35.155.133.134 (named api.discoverlive.speal.ca)
* Configure Godaddy DNS to add an A record for 35.155.133.134 mapping to api.discoverlive.speal.ca
* Verify that you can SSH into the instance: ssh -i ~/.ssh/discover_live_lightsail.pem ec2-user@api.discoverlive.speal.ca

# For updates

* Delete the instance from the Amazon Lightsail console
* Create a new instance with minimal config
* Under network configuration, add a custom rule to allow TCP connections on port 8080 and assign the static IP address
* On your local machine, you might need to remove the entry for api.discoverlive.speal.ca from ~/.ssh/known_hosts
* cd to the deploy directory and then `sh deploy.sh`

# Checking status

* `ssh -i ~/.ssh/discover_live_lightsail.pem ec2-user@api.discoverlive.speal.ca`
* `tmux attach`
* `ctrl + b` for tmux commands. o changes panes, d detaches.
* See logs in each pane.

# TODOs

* Linux does not allow daphne to serve on port 80. Instead run nginx on port 80 and communicate with daphne via a socket.
* Send logs to files and maybe ditch tmux


# Testing

* confirm that you can hit an HTTP endpoint on the server with this URL in the browser: http://api.discoverlive.speal.ca:8080/test
* Use the frontend and confirm that the Search button works. You should see a POST request to the create endpoint and then the page changes and then you should see data streaming in as the server logs go wild.
