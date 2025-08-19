from auth import signup_user, login_user, save_user_profile

choice = input("1 - Signup, 2 - Login: ")
email = input("Enter email: ")
password = input("Enter password: ")

if choice == "1":
    user = signup_user(email, password)
elif choice == "2":
    user = login_user(email, password)
else:
    exit()

if user:
    insta_username = input("Enter Instagram username: ")
    save_user_profile(user['localId'], email, insta_username)
