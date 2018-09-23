# Copy credentials and setup script over
rsync ../_private/spotipyCreds.sh ec2-user@api.discoverlive.speal.ca:/home/ec2-user/spotipyCreds.sh
rsync ./setup.sh ec2-user@api.discoverlive.speal.ca:/home/ec2-user/setup.sh

# Run setup script
ssh -i ~/.ssh/discover_live_lightsail.pem ec2-user@api.discoverlive.speal.ca source /home/ec2-user/setup.sh
