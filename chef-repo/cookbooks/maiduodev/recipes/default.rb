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
    components ["main","stable"]
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
