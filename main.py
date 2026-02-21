import argparse

from services.auth_s import AuthService
from services.task_s import TaskService
from storage.json_st import JSONStorage
from utils.exceptions import ValidationError, AuthenticationError


def build_services():
    storage = JSONStorage("data.json")
    auth_service = AuthService(storage)
    task_service = TaskService(storage)
    return auth_service, task_service


def register_cmd(args):
    auth_service, _ = build_services()
    user = auth_service.register(
        username=args.username,
        email=args.email,
        password=args.password,
        role=args.role,
    )
    print(f"✅ User registered: {user.username}")


def login_cmd(args):
    auth_service, _ = build_services()
    user = auth_service.login(
        username=args.username,
        password=args.password,
    )
    print(f"✅ Logged in as: {user.username}")


def create_task_cmd(args):
    _, task_service = build_services()
    task = task_service.create_task(
        title=args.title,
        description=args.description,
        owner_id=args.user_id,
    )
    print(f"✅ Task created: {task.title} (id={task.id})")


def list_tasks_cmd(args):
    _, task_service = build_services()
    tasks = task_service.list_tasks(owner_id=args.user_id)

    if not tasks:
        print("📭 No tasks found")
        return

    for task in tasks:
        status = "✔" if task.completed else "✖"
        print(f"[{status}] {task.id} - {task.title}")


def main():
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    subparsers = parser.add_subparsers(required=True)

    # register
    register = subparsers.add_parser("register")
    register.add_argument("--username", required=True)
    register.add_argument("--email", required=True)
    register.add_argument("--password", required=True)
    register.add_argument("--role", required=True)
    register.set_defaults(func=register_cmd)

    # login
    login = subparsers.add_parser("login")
    login.add_argument("--username", required=True)
    login.add_argument("--password", required=True)
    login.set_defaults(func=login_cmd)

    # create-task
    create_task = subparsers.add_parser("create-task")
    create_task.add_argument("--title", required=True)
    create_task.add_argument("--description", required=True)
    create_task.add_argument("--user-id", type=int, required=True)
    create_task.set_defaults(func=create_task_cmd)

    # list-tasks
    list_tasks = subparsers.add_parser("list-tasks")
    list_tasks.add_argument("--user-id", type=int, required=True)
    list_tasks.set_defaults(func=list_tasks_cmd)

    args = parser.parse_args()

    try:
        args.func(args)
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    except AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
    except Exception as e:
        print(f"🔥 Unexpected error: {e}")


if __name__ == "__main__":
    main()