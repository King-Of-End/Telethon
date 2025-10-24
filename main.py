from Graph import *
from states import *

def main():
    initial_state = MessageState(user_message=input('Введите сообщение\n'))
    print(get_type(initial_state).type)

if __name__ == '__main__':
    main()