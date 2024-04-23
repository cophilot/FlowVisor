from flowvisor import FlowVisor, vis

@vis # Decorator to include the function in the graph
def deposit(amount):
    if exit:
        return
    print(f"Depositing ${amount}")
    balance = check_balance()
    print(f"New balance after deposit: ${balance + amount}")

@vis
def withdraw(amount):
    print(f"Withdrawing ${amount}")
    balance = check_balance()
    if balance >= amount:
        print(f"Withdrawal successful. New balance: ${balance - amount}")
    else:
        print("Insufficient funds!")

@vis
def check_balance():
    balance = 1000  # Assume initial balance is $1000
    print(f"Current balance: ${balance}")
    deposit(0)
    return balance

@vis
def transfer(amount):
    print(f"Transferring ${amount}")
    withdraw(amount)
    deposit(amount)

@vis
def main():
    print("Welcome to the bank!")
    transfer(200)
    check_balance()
    print("Thank you for banking with us!")

if __name__ == "__main__":
    main()
    FlowVisor.CONFIG.output_file = "example_graph" # You can add some configureation with the CONFIG object
    FlowVisor.graph() # Generate the graph
    FlowVisor.export("example_flow", "json") # Save the flow as json
