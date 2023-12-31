#!/usr/bin/python3
"""
This module defines HBNBCommand, the entry
point of the command interpreter
"""
import cmd
import re

from models import storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User

classes = ["BaseModel", "User", "State", "City", "Place", "Amenity", "Review"]

CLASS_DOES_NOT_EXIST = "** class doesn't exist **"
INSTANCE_NOT_FOUND = "** no instance found **"
CLASS_NAME_MISSING = "** class name missing **"
INSTANCE_ID_MISSING = "** instance id missing **"
INSTANCE_NAME_MISSING = "** attribute name missing **"
MISSING_VALUE = "** value missing **"


class HBNBCommand(cmd.Cmd):
    """The HBNBCommand class"""

    prompt = "(hbnb) "

    def parse_input(self, line):
        """
        Handles processing for alternate syntaxes <class name>.<command>()

        Receives any input that isn't recognized as a standard command,
        determines if it's an alternate syntax command & re-formats it
        into standard command syntax
        """

        # tokenize the input using "." as the delimeter
        tokens = line.strip().split(".")

        # continue with processing if exactly 2 tokens are produced
        if len(tokens) == 2:
            class_name = tokens[0]
            command = tokens[1]

            # retrieve all instances of a class using: <class name>.all()
            if re.match(r"^all\(\)$", command):
                command = "all"
                arguments = class_name
                return command, arguments

            # retrieve the number of instances of a class: <class name>.count()
            elif re.match(r"^count\(\)$", command):
                if class_name not in classes:
                    command = "error"
                    arguments = CLASS_DOES_NOT_EXIST
                else:
                    count = 0
                    for key in storage.all():
                        if class_name in key:
                            count = count + 1
                    command = "count"
                    arguments = count
                return command, arguments

            # retrieve an instance based on its ID: <class name>.show(<id>)
            elif match := re.match(r'show\("([^"]*)"\)', command):
                id = match.group(1)  # get id from capture-group 1 ([^"]*)
                command = "show"
                arguments = class_name + " " + id
                return command, arguments

            # destroy an instance based on its ID: <class name>.destroy(<id>)
            elif match := re.match(r'destroy\("([^"]*)"\)', command):
                id = match.group(1)  # get id from capture-group 1 ([^"]*)
                command = "destroy"
                arguments = class_name + " " + id
                return command, arguments

            # update an instance based on it's ID:
            # <class name>.update(<id>, <attribute name>, <attribute value>)
            elif command.startswith("update"):
                # if the class is invalid
                if class_name not in classes:
                    command = "error"
                    arguments = CLASS_DOES_NOT_EXIST
                    return command, arguments

                pattern1 = (
                    r"update"
                    + r'\(\s*"([^"]*)",'  # capture group 1 - string
                    + r'\s*"([^"]*)",'  # capture group 2 - string
                    + r'\s*("[^"]*")\s*\)'  # capture group 3 - string
                )
                pattern2 = (
                    r"update"
                    + r'\(\s*"([^"]*)",'  # capture group 1 - string
                    + r"\s*(\{.*\}\s*)"  # capture group 2 - dict/set
                )

                if match := re.match(pattern1, command):
                    id = match.group(1)  # grab from capture-group 1 ([^"]*)
                    attr_name = match.group(2)  # grab from capture-group 2
                    value = match.group(3)  # grab from capture-group 3

                    command = "update"
                    arguments = ""

                    # construct the arguments string sequentially and
                    # stop constructing once an empty substring is met
                    if class_name:
                        arguments += class_name
                    if class_name and id:
                        arguments += " " + id
                    if class_name and id and attr_name:
                        arguments += " " + attr_name
                    if class_name and id and attr_name and value:
                        arguments += " " + value
                    return command, arguments

                elif match := re.match(pattern2, command):
                    # DEBUG: print("match pattern 2")
                    id = match.group(1)  # grab from capture-group 1 ([^"]*)
                    dict_rep = match.group(2)  # grab from capture-group 2
                    instance_key = f"{class_name}.{id}"

                    # if the instace doesn't exist
                    if instance_key not in storage.all():
                        command = "error"
                        arguments = INSTANCE_NOT_FOUND
                        return command, arguments

                    # try to convert the grabbed dict_rep into a dictionary,
                    # if it is a valid representation, it should be successful
                    try:
                        dictionary = eval(dict_rep)
                        if isinstance(dictionary, dict):
                            command = "update_from_dictionary"
                            arguments = []

                            """ # if the dictionary is empty, produce an
                            # "attribute name missing" error
                            if len(dictionary) == 0:
                                command = "error"
                                arguments = "** attribute name missing **"
                                return command, arguments """

                            # construct a list of Update command arguments in
                            # the format: <classname> <id> <attr name> <value>
                            for attr_name, value in dictionary.items():
                                # if the attribute name is empty
                                if str(attr_name).strip() == "":
                                    command = "error"
                                    arguments = INSTANCE_NAME_MISSING
                                    return command, arguments

                                # if the value is empty
                                if str(value).strip() == "":
                                    command = "error"
                                    arguments = MISSING_VALUE
                                    return command, arguments

                                arg = f"{class_name} {id} {attr_name} {value}"
                                arguments.append(arg)

                            return command, arguments
                    except Exception:
                        pass
        return None, None

    def default(self, line):
        """
        Handles input that isn't recognised by any of the do_ methods

        These unrecognised commands could either be alternate syntax
        of standard commands or they could truly be invalid/uknown
        """

        # parse the input to determine if it is an alternate syntax
        command, arguments = self.parse_input(line)
        if command == "all":
            self.do_all(arguments)
        elif command == "count":
            print(arguments)
        elif command == "show":
            self.do_show(arguments)
        elif command == "destroy":
            self.do_destroy(arguments)
        elif command == "update":
            self.do_update(arguments)
        elif command == "update_from_dictionary":
            for arg in arguments:
                self.do_update(arg)
        elif command == "error":
            print(arguments)
        else:  # not an alternate syntax (ie. it's an uknown syntax)
            super().default(line)

    def do_quit(self, line):
        """quit command exits the program"""
        return True

    def do_EOF(self, line):
        """EOF signal exits the program"""
        print()  # adds a newline after EOF
        return True

    def emptyline(self):
        """When empty line is encountered, do nothing"""
        pass

    def do_create(self, line):
        """Creates a new instance of a class, saves it to storage
        and prints the id
        """
        line = line.split()
        if len(line) == 0:
            print()
        elif line[0] not in classes:
            print(CLASS_DOES_NOT_EXIST)
        else:
            instance = eval(line[0])()
            instance.save()
            print(instance.id)

    def do_show(self, line):
        """Prints the string representation of an instance based on the
        class name and id
        """
        line = line.split()
        if len(line) == 0:
            print(CLASS_NAME_MISSING)
        elif line[0] not in classes:
            print(CLASS_DOES_NOT_EXIST)
        elif len(line) == 1:
            print()
        else:
            instance_key = f"{line[0]}.{line[1]}"
            if instance_key not in storage.all():
                print(INSTANCE_NOT_FOUND)
            else:
                print(storage.all()[instance_key])

    def do_destroy(self, line):
        """Deletes an instance based on the class name id"""
        line = line.split()
        if len(line) == 0:
            print(CLASS_NAME_MISSING)
        elif line[0] not in classes:
            print(CLASS_DOES_NOT_EXIST)
        elif len(line) == 1:
            print(INSTANCE_ID_MISSING)
        else:
            instance_key = f"{line[0]}.{line[1]}"
            if instance_key not in storage.all():
                print(INSTANCE_NOT_FOUND)
            else:
                del storage.all()[instance_key]
                storage.save()

    def do_all(self, line):
        """Print all string representation of all instance based or
        not on the class name
        """
        line = line.split()
        if len(line) == 0:
            # print all objects in storage
            if len(storage.all()) > 0:
                print("[", end="")
                for index, obj in enumerate(storage.all().values()):
                    print('"', end="")
                    print(obj, end="")
                    print('"', end="")
                    if index != len(storage.all()) - 1:
                        print(", ", end="")
                print("]")
        elif line[0] not in classes:
            print(CLASS_DOES_NOT_EXIST)
        else:
            # print objects of a particular class in storage
            objects = []
            for key in storage.all():
                if key.startswith(line[0]):
                    objects.append(storage.all()[key])
            if len(objects) > 0:
                print("[", end="")
                for index, obj in enumerate(objects):
                    print('"', end="")
                    print(obj, end="")
                    print('"', end="")
                    if index != len(objects) - 1:
                        print(", ", end="")
                print("]")

    def do_update(self, line):
        """Updates an instance based on the class name and id
        by adding or updating attribute
        """
        # A token is either text delimited by whitespace
        # or an text between double quotes ie. "my expression"

        # Define the regular expression for extracting tokens
        pattern = r'"[^"]*"|\S+'
        # Create the tokens using the pattern
        tokens = re.findall(pattern, line)
        # Remove any surrounding quotes & whitespaces from tokens
        tokens = [token.strip('"').strip() for token in tokens]

        num_of_args = len(tokens)
        # DEBUG: print(f"num or args: {num_of_args}")

        # tokens[0]: classname         tokens[1]: id
        # tokens[2]: attribute name    tokens[3]: value

        # if no arguments entered at all
        if num_of_args == 0:
            print(CLASS_NAME_MISSING)

        # if some arguments entered but 1st one(classname) is invalid
        elif num_of_args > 0 and tokens[0] not in classes:
            print(CLASS_DOES_NOT_EXIST)

        # if id isn't entered or is entered but is an empty string
        elif num_of_args == 1 or (num_of_args > 1 and not tokens[1]):
            print(INSTANCE_ID_MISSING)

        elif num_of_args > 1:
            class_name = tokens[0]
            id = tokens[1]
            instance_key = f"{class_name}.{id}"

            # if the id is entered but doesnt exist in the storage
            if instance_key not in storage.all():
                print(INSTANCE_NOT_FOUND)

            # if attr name not entered or is entered but is empty string
            elif num_of_args == 2 or (num_of_args > 2 and not tokens[2]):
                print(INSTANCE_NAME_MISSING)

            # if value not entered or is entered but is empty string
            # or a string of double quotes with arbitrary whitespace
            elif num_of_args == 3 or (num_of_args > 3 and not tokens[3]):
                print(MISSING_VALUE)

            # else go ahead and update
            else:
                attr_name = tokens[2]
                value = tokens[3]
                obj = storage.all()[instance_key]
                try:
                    setattr(obj, attr_name, eval(value))
                except Exception:
                    # fallback in-case eval fails
                    setattr(obj, attr_name, value)
                obj.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
