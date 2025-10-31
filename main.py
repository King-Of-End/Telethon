from Graph import *
from states import *

def main():
    initial_state = MessageState(user_message='привет')
    res = app.invoke(initial_state)
    try:
        with open('state_logs.txt', 'a', encoding='utf-8') as f:
            f.write('-' * 50 + '\n' + str(initial_state) + '\n' + str(res) + '\n')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
