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
mkdir _private
mv ../spotipyCreds _private

# Go!
tmux
teamocil --layout deploy/tmuxLayout.yml
