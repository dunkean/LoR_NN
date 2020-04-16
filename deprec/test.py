import json

ar = {}
with open('set1-en_us.json', encoding="utf8") as json_file:
    for p in json.load(json_file):
        str = p["type"]
        # for str in p["spellSpeed"]:
        ar[str] = None

print(ar.keys())


# from scapy.all import *
# sniff(filter="ip", prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}"))

# items = [1,1,3,4,5]
# knapsack = []
# limit = 7

# def print_solutions(current_item, knapsack, current_sum):
#     #if all items have been processed print the solution and return:
#     if current_item == len(items):
#         print(knapsack)
#         return

#     #don't take the current item and go check others
#     print_solutions(current_item + 1, list(knapsack), current_sum)

#     #take the current item if the value doesn't exceed the limit
#     if (current_sum + items[current_item] <= limit):
#         knapsack.append(items[current_item])
#         current_sum += items[current_item]
#         #current item taken go check others
#         print_solutions(current_item + 1, knapsack, current_sum )

# print_solutions(0,knapsack,0)


# from __future__ import print_function
# from ortools.algorithms import pywrapknapsack_solver


# def main():
#     # Create the solver.
#     solver = pywrapknapsack_solver.KnapsackSolver(
#         pywrapknapsack_solver.KnapsackSolver.
#         KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')

#     values = [
#         1,1,1,2,1,2
#     ]
#     weights = [[
#        2,2,2,4,2,4
#     ]]
#     capacities = [6]

#     solver.Init(values, weights, capacities)
#     computed_value = solver.Solve()

#     packed_items = []
#     packed_weights = []
#     total_weight = 0
#     print('Total value =', computed_value)
#     for i in range(len(values)):
#         if solver.BestSolutionContains(i):
#             packed_items.append(i)
#             packed_weights.append(weights[0][i])
#             total_weight += weights[0][i]
#     print('Total weight:', total_weight)
#     print('Packed items:', packed_items)
#     print('Packed_weights:', packed_weights)

#     # solver.


# if __name__ == '__main__':
#     main()
