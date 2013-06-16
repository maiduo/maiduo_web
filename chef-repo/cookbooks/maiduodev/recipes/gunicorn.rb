node.default['gunicorn']['virtualenv'] = '/data/.virtualenvs/maiduodev'

gunicorn_config "/data/gunicorn_maiduo.py" do
  action :create
end
