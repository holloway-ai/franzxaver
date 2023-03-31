from celery import Celery

celery_app = Celery("worker", backend="redis://redis:6379/0", broker="redis://redis:6379/0")

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue",
                               "app.worker.process_video": "main-queue"}
