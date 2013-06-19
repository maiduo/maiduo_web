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
python_pip "get-mirror"

python_virtualenv "/data/.virtualenvs/maiduodev" do
  action :create
  options "--distribute"
end

python_pip "pip" do
  virtualenv "/data/.virtualenvs/maiduodev"
  action :install
end

git "/data/maiduo/" do
  repository "git://github.com/maiduo/maiduo_web.git"
  action :sync
  enable_submodules true
end

ruby_block "load-get-mirror" do
  block do
    # node[:maiduodev] = {}
    node.default[:maiduodev][:mirror_pypi] = `get-mirror pypi`
  end
  action :create
end
execute "pip install -r requirements.txt" do
  command "/data/.virtualenvs/maiduodev/bin/pip install -r requirements.txt"
  cwd "/data/maiduo/"
end
execute "pip install -r dev_requirements.txt" do
  command "/data/.virtualenvs/maiduodev/bin/pip install -r "\
          "dev_requirements.txt"
  cwd "/data/maiduo/"
end

include_recipe "maiduodev::sync"



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

node.default['supervisor']['dir'] = '/data/supervisor'
node.default['supervisor']['log_dir'] = '/data/supervisor/log/'
node.default['supervisor']['logolevel'] = 'debug'
include_recipe "supervisor"

supervisor_service "maiduo" do
  action "enable"
  autostart true
  directory "/data/maiduo/"
  stdout_logfile "maiduo.log"
  stderr_logfile "maiduo_error.log"

  command "/data/.virtualenvs/maiduodev/bin/"\
          "gunicorn mdapp.wsgi:application -c /data/gunicorn_maiduo.py"
end

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
