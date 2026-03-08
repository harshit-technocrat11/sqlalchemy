# imports
from sqlalchemy import create_engine, Column , String , Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError 

# Create your database
engine =  create_engine("sqlite:///tasks.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# define models
    # we are inhereting the base class from sql alchemy
class User (Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True) 
    name = Column(String, nullable=False)
    email = Column(String, nullable = False, unique =True)
    tasks = relationship('Task', back_populates='user', cascade="all, delete-orphan")

class Task (Base):
    __tablename__  = "tasks"
    id = Column (Integer, primary_key=True)
    title = Column (String(50), nullable=True)
    description = Column (String)
    user_id = Column(Integer, ForeignKey("users.id")) #foreign key from users table 
    user =  relationship('User', back_populates='tasks')

Base.metadata.create_all(engine)

# Utility Functions
def get_user_by_email(email):
    return session.query(User).filter_by(email=email).first()

# confirmation for deleting actions
def confirm_action(prompt:str) -> bool:
    # if the input is "yEs" or "yes" etc.. this func() returns true
    return input(f"{prompt} (yes/no):").strip().lower() == "yes"
    

# CRUD ops
def add_user():
    name, email = input("Enter user name: "), input("Enter the email:")
    if get_user_by_email(email):
        print(f"User already exists : {email}")
        return

    try:
        session.add(User(name=name, email=email))
        session.commit()
        print(f"User: {name} added")

    except:
        session.rollback()
        print(f"ERROR")


def add_task():
    email = input("Enter the email of the user to add tasks: ")
    user = get_user_by_email(email)
    if not user:
        print(f"No user found with that email!!")
        return
    
    title, description = input("enter the title:" ) , input("enter description: ")
    session.add(Task(title=title, description=description , user=user)) #attaching tasks to the user
    session.commit()
    print(f"added to the databse: {title} : {description}")


# Query 
def query_users():
    for user in session.query(User).all():
        print(f"ID: {user.id}, Name:{user.name}, Email: {user.email}")

def query_tasks():
    email = input("Enter the email of the user for tasks:")
    user  = get_user_by_email(email)
    if not user:
        print("no user exists with that email")
        return

    if not user.tasks:
        print(f"No tasks added by {user.email}")
    for task in user.tasks:
        print(f"Task ID: {task.id}, Title: {task.title}")    

def update_user():
    email = input(f"enter email of user who u wanna update:")
    user = get_user_by_email(email)
    if not user:
        print("no such user exists")
        return

    # user details:
    user.name= input("enter a new name for the user (leave blank to stay the same)") or user.name
    user.email=input("Enter a new email (leave blank to stay the same))") or user.email

    session.commit()
    print("user has been updated!!")

# Deleting
def delete_user():
    email = input(f"enter email of user who u wanna DELETE:")
    user= get_user_by_email(email=email)
    if not user:
        print("no such user exists with that email")
        return
    
    # delete 
    if ( confirm_action(f"Do you want to delete user: {user.email}?")):
        session.delete(user)
        session.commit()

        print("User has been deleted!!")

def delete_task():
    email =  input("Enter the email linked to the task: ")
    if not email:
        print("oops! no such email exists")
        return
    
    user = get_user_by_email(email)
    if not user.tasks: 
        print("no tasks exist")
        return
    for task in user.tasks:
        print(f"ID: {task.id}, title: {task.title}")

    task_id = input("Enter the ID of the task u wanna delete: ")
    
    # ensure that the task belongs to the user!! authenticated
    task = next((t for t in user.tasks if str(t.id)==task_id),None)
    
    if not task:
        print(f"no such task exists with the entered ID")
        return

    if confirm_action(f"are u sure u wanna delete this task: {task.id}? "):
        session.delete(task)
        session.commit()
        
        print("Task deleted , success")

# Main Ops
def main() -> None:
    actions = {
        "1":add_user,
        "2": add_task,
        "3":query_users,
        "4":query_tasks,
        "5":update_user,
        "6":delete_user,
        "7":delete_task
    }

    while True: 
        print("\nOptions:\n1. Add User\n2. Add Task\n3. Query Users\n4. Query Tasks\n5. Update User\n6. Delete User\n7. Delete Task\n8. Exit")

        choice = input("Enter an option: ")

        if choice == "8":
            print("Adios amigoss!")
            break
        action = actions.get(choice)

        if action:
            action()  #converting variable name to function call
        else: 
            print("That is not an option")


if __name__ == "__main__":
    main()