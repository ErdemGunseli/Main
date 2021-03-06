class User():

    def __init__(self, fName, lName, email, password):
        self.fName = fName
        self.lName = lName
        self.email = email
        self.password = password


    def validEmail(self):
        if "@" in self.email and "." in self.email:
            return True
        return False

    def validPassword(self):
        password = self.password

        if len(password) >= 9 and len(password) <= 12 and password != password.upper() and password != password.lower():
                for i in range(10): 
                    if str(i) in password: return True        
        return False      

## TESTING:

myUser =  User("Bob", "Dave", "bobdave@gmail.com", "Password1")

if myUser.validEmail():
    print("Email Valid")
else:
    print("Email Invalid") 
       

if myUser.validPassword():
    print("Password Valid")
else:
    print("Password Invalid")           

# Password needs uppercase, lowercase, number, length between 9, 12 inclusive.
# Email needs @ sign and .