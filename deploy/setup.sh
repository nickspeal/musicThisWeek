# Install
sudo yum -y update
sudo yum-config-manager --enable epel # Needed for redis server
sudo yum -y install git python36 python36-devel gcc redis tmux #nginx
gem install teamocil

# Clone
git clone https://github.com/nickspeal/musicThisWeek.git /home/ec2-user/musicThisWeek

# Python Setup
virtualenv -p `which python36` env
./env/bin/pip install -r musicThisWeek/requirements.txt

# App setup
cd musicThisWeek
mv ../spotipyCreds.sh _private
source /home/ec2-user/musicThisWeek/_private/spotipyCreds.sh
source /home/ec2-user/env/bin/activate
python manage.py migrate

# Go!
tmux new-session -d -s discover_live 'teamocil --layout /home/ec2-user/musicThisWeek/deploy/tmuxLayout.yml'

echo 'Deployment complete. SSH in and then run `tmux attach`'
echo 'ssh -i ~/.ssh/discover_live_lightsail.pem ec2-user@api.discoverlive.speal.ca'
