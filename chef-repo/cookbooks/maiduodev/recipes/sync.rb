bin_python = "/data/.virtualenvs/maiduodev/bin/python"
execute "setup maiduo app" do
  command "#{bin_python} manage.py syncdb --noinput > /tmp/sync.log 2>&1;"\
          "#{bin_python} manage.py migrate --all >> /tmp/sync.log 2>&1;"\
          "#{bin_python} manage.py createsuperuser --username admin --email "\
          "admin@admin.com --noinput >> /tmp/sync.log 2>&1;"\
          "#{bin_python} manage.py passwd2 admin --password admin"\
          " >> /tmp/sync.log 2>&1;"\
          "#{bin_python} manage.py collectstatic --noinput"\
          ">> /tmp/sync.log 2>&1;"\
          "echo 1>/tmp/ok"
  cwd "/data/maiduo/"
  not_if { ::File.exists?("/data/maiduo/dev.sqlite3") }
end

directory "/data/maiduo/static/"

execute "move static file" do
  command "mv /data/maiduo/admin /data/maiduo/static/"
  only_if { ::Dir.exists?("/data/maiduo/admin") }
end
