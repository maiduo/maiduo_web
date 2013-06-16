#
# Cookbook Name:: maiduodev
# Recipe:: default
#
# Copyright 2013, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

include_recipe "apt"
file "/etc/apt/sources.list" do
  action :delete
end
apt_repository "netease" do
    uri "http://mirrors.163.com/ubuntu"
    components ["main","restricted", "universe", "multiverse"]
    distribution node['lsb']['codename']
    action :add
end

include_recipe "build-essential"

package "git"
package "python-mysqldb" do
  action :install
end 

include_recipe "python"
python_pip "virtualenv"

python_virtualenv "/data/.virtualenvs/maiduodev" do
  action :create
  options "--distribute"
end

python_pip "pip" do
  virtualenv "/data/.virtualenvs/maiduodev"
  # options "--distribute"
  action :install
end

git "/data/maiduo/" do
  repository "git://github.com/maiduo/maiduo_web.git"
  action :sync
end

execute "pip install -r requirements.txt" do
  command "source /data/.virtualenvs/maiduodev/bin/activate;"\
          "pip install -r requirements.txt"
  cwd "/data/maiduo/"
end
execute "pip install -r dev_requirements.txt" do
  command "source /data/.virtualenvs/maiduodev/bin/activate;"\
          "pip install -r requirements.txt"
  cwd "/data/maiduo/"
end

execute "setup maiduo app" do
  command "source /data/.virtualenvs/maiduodev/bin/activate;"\
          "python manage.py syncdb --noinput;"\
          "python manage.py migrate --all;"\
          "python manage.py createsuperuser --username admin --email "\
          "admin@admin.com --noinput;"
          "python manage.py passwd2 admin --password admin;"\
          "python manage.py collectstatic --noinput;"
  cwd "/data/maiduo/"
  not_if { ::File.exists?("/data/maiduo/dev.sqlite3") }
end

directory "/data/maiduo/static/"

execute "move static file" do
  command "mv /data/maiduo/admin /data/maiduo/static/"
  not_if { ::Dir.exists?("/data/maiduo/admin") }
end

#include_recipe 'gunicorn'
#include_recipe 'maiduodev::gunicorn'
#
template "/data/gunicorn_maiduo.py" do
  source "gunicorn.py.erb"
end 

directory "/data/log/" do
  mode 0644
  action :create
end
directory "/data/supervisor/log/" do
  mode 0644
  recursive true
  action :create
end

node.default['supervisor']['dir'] = '/data/supervisor/'
node.default['supervisor']['log_dir'] = '/data/supervisor/log/'
node.default['supervisor']['logolevel'] = 'debug'
supervisor_service "maiduo" do
  action "enable"
  autostart true
  directory "/data/maiduo/"
  stdout_logfile "maiduo.log"
  stderr_logfile "maiduo_error.log"

  command "/data/.virtualenvs/maiduodev/bin/"\
          "gunicorn mdapp.wsgi:application -c /data/gunicorn_maiduo.py"
end
include_recipe "supervisor"

include_recipe "nginx"
cookbook_file "#{node['nginx']['dir']}/sites-available/default" do
  source "nginx_site_default"
end

nginx_site "default" do
  entable true
end

=begin
nginx_site "default" do
  listen 80
  # server_name 
  location / {
    proxy_pass "http://localhost:8000"
    proxy_set_header "X-Real-IP \$remote_addr"
  }
end
=end
