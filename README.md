# The Scheduler


### Run project locally => Do each in separate terminals

### start flask app
python app.py

### start redis-server
brew install redis-server
redis-server

### start celery workers
celery -A service.celery worker

### start celery scheduled processes
 celery -A service.celery beat


### Deploy project on AWS => TBD