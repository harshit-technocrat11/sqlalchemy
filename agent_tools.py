from sql_crud import User, Task, session, Session, get_user_by_email
from sqlalchemy.exc import IntegrityError 

# tools for agent  ( each tool needs input , and returns only the output , NO print statements )


# create
def add_user(name: str, email: str):

    if get_user_by_email(email):
        return f"User already exists: {email}"

    try:
        user = User(name=name, email=email)
        session.add(user)
        session.commit()

        return f"User {name} added"

    except IntegrityError:
        session.rollback()
        return "Error adding user"

def add_task(email: str, title: str, description: str=""):

    user = get_user_by_email(email)

    if not user:
        return "User not found"

    task = Task(title=title, description=description, user=user)

    session.add(task)
    session.commit()

    return f"Task '{title}' added for {email}"

# update
def update_user(email: str, new_name=None, new_email=None):

    user = get_user_by_email(email)

    if not user:
        return "User not found"

    if new_name:
        user.name = new_name

    if new_email:
        user.email = new_email

    session.commit()

    return "User updated"



# query
def query_users():

    users = session.query(User).all()

    if not users:
        return "No users found"

    result = []

    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email
        })

    return result

def query_tasks(email: str):

    user = get_user_by_email(email)

    if not user:
        return "User not found"

    tasks = []

    for t in user.tasks:
        tasks.append({
            "id": t.id,
            "title": t.title
        })

    return tasks

# delete
def delete_task(email:str, task_id: int):

    user = get_user_by_email(email)

    if not user: 
        return "User not found"
    
    task = session.query("Task").filter_by(id=task_id, user=user.id).first()

    if not task:
        return "Task not found!"
    
    session.delete(task)
    session.commit()

    return "Task deleted"

def delete_user(email: str):
    user = get_user_by_email(email)

    if not user:
        return "User not found!"
    
    session.delete(user)
    session.commit()

    return "User deleted , success"
