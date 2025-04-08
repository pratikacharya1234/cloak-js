

# Define conditions
entry_conditions = (":begin", "start", "go")
exit_conditions = (":q", "quit", "exit")

#syntax list to use bot
syntax_list = {
    'start': "To Start Bot",
    ':q': "To Exit Bot",
    'create' : "To Create a new Chat with Bot",
    'submit' : "To Submit a chat",
    'exit' : "To exit bot"
}

while True:
    print("Chatbot is ready to chat! Type 'syntax' to see the syntax list.")
    query = input("> ")

    if query in ('syntax'):
        print(syntax_list)
    if query in syntax_list[0]:
        chat = input('Hey, How can i assist you today')
    elif query in entry_conditions:
        print("What's your problem?")
        break
    elif query in exit_conditions:
        print("Goodbye!")
        break